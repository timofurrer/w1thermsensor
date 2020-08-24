"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2020 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import subprocess
import time
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional, Union

from w1thermsensor.errors import (
    NoSensorFoundError,
    ResetValueError,
    SensorNotReadyError,
    W1ThermSensorError,
    UnsupportedSensorError,
)
from w1thermsensor.sensors import Sensor
from w1thermsensor.units import Unit


class W1ThermSensor:
    """
    Represents a w1 therm sensor connected to the device accessed by
    the Linux w1 therm sensor kernel modules.


    Examples:
        List all sensors

        >>> W1ThermSensor.get_available_sensors()

        Initialize first available sensor

        >>> sensor = W1ThermSensor()

        Initialize sensor of specific type

        >>> sensor = W1ThermSensor(Sensor.DS18B20)

        Get sensor temperature

        >>> sensor.get_temperature()

        Get temperature in a specific unit

        >>> sensor.get_temperature(Unit.DEGREES_F)

    Supported sensors are:
        * DS18S20
        * DS1822
        * DS18B20
        * DS28EA00
        * DS1825
        * MAX31850K

    Supported temperature units are:
        * Kelvin
        * Celsius
        * Fahrenheit
    """

    #: Holds information about the location of the needed
    #  sensor devices on the system provided by the kernel modules
    BASE_DIRECTORY = Path("/sys/bus/w1/devices")
    SLAVE_FILE = "w1_slave"

    #: Holds the sensor reset value in Degrees Celsius
    SENSOR_RESET_VALUE = 85.0

    #: Holds the factor to convert the raw sensor value to Degrees Celsius
    RAW_VALUE_TO_DEGREE_CELSIUS_FACTOR = 1e-3

    #: Holds settings for patient retries used to access the sensors
    RETRY_ATTEMPTS = 10
    RETRY_DELAY_SECONDS = 1.0 / RETRY_ATTEMPTS

    @classmethod
    def get_available_sensors(
        cls, types: Optional[Iterable[Union[Sensor, str]]] = None
    ) -> List["W1ThermSensor"]:
        """Return all available sensors.

        :param list types: the type of the sensor to look for.
                           If types is None it will search for all available types.

        :returns: a list of sensor instances.
        :rtype: list
        """
        if not types:
            types = list(Sensor)
        else:
            try:
                types = [s if isinstance(s, Sensor) else Sensor[s] for s in types]
            except KeyError as exc:  # sensor type does not exist
                raise UnsupportedSensorError(str(exc), (s.name for s in Sensor))

        def is_sensor(dir_name):
            return any(dir_name.startswith(hex(x.value)[2:]) for x in types)

        return [
            cls(Sensor.from_id_string(s.name[:2]), s.name[3:])
            for s in cls.BASE_DIRECTORY.iterdir()
            if is_sensor(s.name)
        ]

    def __init__(
        self,
        sensor_type: Optional[Sensor] = None,
        sensor_id: Optional[str] = None,
        offset: float = 0.0,
        offset_unit: Unit = Unit.DEGREES_C,
    ) -> None:
        """Initializes a W1ThermSensor.

        If the W1ThermSensor base directory is not found it will automatically load
        the needed kernel modules to make this directory available.
        If the expected directory will not be created after some time an exception is raised.

        If no type and no id are given the first found sensor will be taken for this instance.

        :param int sensor_type: the type of the sensor.
        :param string id: the id of the sensor.
        :param float offset: a calibration offset for the temperature sensor readings
                             in the unit of ``offset_unit``.
        :param offset_unit: the unit in which the offset is provided.

        :raises KernelModuleLoadError: if the w1 therm kernel modules could not
                                       be loaded correctly
        :raises NoSensorFoundError: if the sensor with the given type and/or id
                                    does not exist or is not connected
        """
        if not sensor_type and not sensor_id:
            self._init_with_first_sensor()
        elif not sensor_id and sensor_type:
            self._init_with_first_sensor_by_type(sensor_type)
        elif not sensor_type and sensor_id:
            self._init_with_first_sensor_by_id(sensor_id)
        else:
            self._init_with_type_and_id(sensor_type, sensor_id)  # type: ignore

        # store path to sensor
        self.sensorpath = (
            self.BASE_DIRECTORY / (self.slave_prefix + self.id) / self.SLAVE_FILE
        )

        if not self.exists():
            raise NoSensorFoundError(
                "Could not find sensor of type {} with id {}".format(self.name, self.id)
            )

        self.set_offset(offset, offset_unit)

    def _init_with_first_sensor(self):
        for _ in range(self.RETRY_ATTEMPTS):
            s = self.get_available_sensors()
            if s:
                self._init_with_type_and_id(s[0].type, s[0].id)
                break
            time.sleep(self.RETRY_DELAY_SECONDS)
        else:
            raise NoSensorFoundError("Could not find any sensor")

    def _init_with_first_sensor_by_type(self, sensor_type: Sensor) -> None:
        s = self.get_available_sensors([sensor_type])
        if not s:
            raise NoSensorFoundError(
                "Could not find any sensor of type {}".format(sensor_type.name)
            )

        self._init_with_type_and_id(sensor_type, s[0].id)

    def _init_with_first_sensor_by_id(self, sensor_id: str) -> None:
        sensor = next(  # pragma: no cover
            (s for s in self.get_available_sensors() if s.id == sensor_id), None
        )
        if not sensor:
            raise NoSensorFoundError(
                "Could not find sensor with id {}".format(sensor_id)
            )

        self._init_with_type_and_id(sensor.type, sensor.id)

    def _init_with_type_and_id(self, sensor_type: Sensor, sensor_id: str) -> None:
        self.type = sensor_type
        self.id = sensor_id

    def __repr__(self) -> str:  # pragma: no cover
        """Returns a string that eval can turn back into this object

        :returns: representation of this instance
        :rtype: string
        """
        return "{}(sensor_type={}, sensor_id='{}')".format(
            self.__class__.__name__, str(self.type), self.id
        )

    def __str__(self) -> str:
        """Returns a pretty string respresentation

        :returns: representation of this instance
        :rtype: string
        """
        return "{0}(name='{1}', type={2}(0x{2:x}), id='{3}')".format(
            self.__class__.__name__, self.type.name, self.type.value, self.id
        )

    @property
    def name(self) -> str:
        """Returns the type name of this temperature sensor"""
        return self.type.name

    @property
    def slave_prefix(self) -> str:
        """Returns the slave prefix for this temperature sensor"""
        return "%s-" % hex(self.type.value)[2:]

    def exists(self) -> bool:
        """Returns the sensors slave path"""
        return self.sensorpath.exists()

    def get_raw_sensor_strings(self) -> List[str]:
        """Reads the raw strings from the kernel module sysfs interface

        :returns: raw strings containing all bytes from the sensor memory
        :rtype: str

        :raises NoSensorFoundError: if the sensor could not be found
        :raises SensorNotReadyError: if the sensor is not ready yet
        """
        try:
            with self.sensorpath.open("r") as f:
                data = f.readlines()
        except IOError:
            raise NoSensorFoundError(
                "Could not find sensor of type {} with id {}".format(self.name, self.id)
            )

        if (
            len(data) < 1
            or data[0].strip()[-3:] != "YES"
            or "00 00 00 00 00 00 00 00 00" in data[0]
        ):
            raise SensorNotReadyError(self)

        return data

    def get_temperature(self, unit: Unit = Unit.DEGREES_C) -> float:
        """Returns the temperature in the specified unit

        :param int unit: the unit of the temperature requested

        :returns: the temperature in the given unit
        :rtype: float

        :raises UnsupportedUnitError: if the unit is not supported
        :raises NoSensorFoundError: if the sensor could not be found
        :raises SensorNotReadyError: if the sensor is not ready yet
        :raises ResetValueError: if the sensor has still the initial value and no measurment
        """
        raw_temperature_line = self.get_raw_sensor_strings()[1]
        return evaluate_temperature(
            raw_temperature_line,
            self.RAW_VALUE_TO_DEGREE_CELSIUS_FACTOR,
            unit,
            self.type,
            self.id,
            self.offset,
            self.SENSOR_RESET_VALUE,
        )

    def get_temperatures(self, units: Iterable[Unit]) -> List[float]:
        """Returns the temperatures in the specified units

        :param list units: the units for the sensor temperature

        :returns: the sensor temperature in the given units. The order of
        the temperatures matches the order of the given units.
        :rtype: list

        :raises UnsupportedUnitError: if the unit is not supported
        :raises NoSensorFoundError: if the sensor could not be found
        :raises SensorNotReadyError: if the sensor is not ready yet
        """
        sensor_value = self.get_temperature(Unit.DEGREES_C)
        return [
            Unit.get_conversion_function(Unit.DEGREES_C, unit)(sensor_value)
            for unit in units
        ]

    def get_resolution(self) -> int:
        """Get the current resolution from the sensor.

        :returns: sensor resolution from 9-12 bits
        :rtype: int
        """
        raw_temperature_line = self.get_raw_sensor_strings()[1]
        return evaluate_resolution(raw_temperature_line)

    def set_resolution(self, resolution: int, persist: bool = False) -> bool:
        """Set the resolution of the sensor for the next readings.

        If the ``persist`` argument is set to ``False`` this value
        is "only" stored in the volatile SRAM, so it is reset when
        the sensor gets power-cycled.

        If the ``persist`` argument is set to ``True`` the current set
        resolution is stored into the EEPROM. Since the EEPROM has a limited
        amount of writes (>50k), this command should be used wisely.

        Note: root permissions are required to change the sensors resolution.

        Note: This function is supported since kernel 4.7.

        :param int resolution: the sensor resolution in bits.
                              Valid values are between 9 and 12
        :param bool persist: if the sensor resolution should be written
                             to the EEPROM.

        :returns: if the sensor resolution could be set or not.
        :rtype: bool
        """
        if not 9 <= resolution <= 12:
            raise ValueError(
                "The given sensor resolution '{0}' is out of range (9-12)".format(
                    resolution
                )
            )

        exitcode = subprocess.call(
            "echo {0} > {1}".format(resolution, self.sensorpath), shell=True
        )
        if exitcode != 0:
            raise W1ThermSensorError(
                "Failed to change resolution to {0} bit. "
                "You might have to be root to change the resolution".format(resolution)
            )

        if persist:
            exitcode = subprocess.call(
                "echo 0 > {0}".format(self.sensorpath), shell=True
            )
            if exitcode != 0:
                raise W1ThermSensorError(
                    "Failed to write resolution configuration to sensor EEPROM"
                )

        return True

    def set_offset(self, offset: float, unit: Unit = Unit.DEGREES_C) -> None:
        """Set an offset to be applied to each temperature reading.

        This is used to tune sensors which report values
        which are either too high or too low.

        The offset is converted as needed when getting temperatures in
        other units than Celcius.

        :param float offset: The value to add or subtract from the
                             temperature measurement. Positive values
                             increase themperature, negative values
                             decrease temperature.

        :param: int unit: The unit in which offset is expressed. Default is
                          Celcius.

        :rtype: None
        """
        # We need to subtract `factor(0)` from the result, in order to
        # eliminate any offset temperatures used in the conversion formulas
        # (such as 32F, when converting from C to F).
        factor = Unit.get_conversion_function(unit, Unit.DEGREES_C)
        self.offset = factor(offset) - factor(0)

    def get_offset(self, unit: Unit = Unit.DEGREES_C) -> float:
        """Get the offset set for this sensor. If no offset has been set, 0.0 is returned.

        :param: int unit: The unit to return the temperature offset in

        :returns: The offset set for this temperature sensor
        :rtype: float
        """

        # We need to subtract `factor(0)` from the result, in order to
        # eliminate any offset temperatures used in the conversion formulas
        # (such as 32F, when converting from C to F).
        factor = Unit.get_conversion_function(Unit.DEGREES_C, unit)
        return factor(self.offset) - factor(0)


@lru_cache()
def evaluate_temperature(
    raw_temperature_line: str,
    raw_temperature_to_degree_celsius_factor: float,
    target_temperature_unit: Unit,
    sensor_type: Sensor,
    sensor_id: str,
    sensor_offset: float,
    sensor_reset_value: float,
) -> float:
    factor = Unit.get_conversion_function(Unit.DEGREES_C, target_temperature_unit)
    if sensor_type.comply_12bit_standard():
        value = float(convert_raw_temperature_to_sensor_count(raw_temperature_line))
        # the int part is 8 bit wide, 4 bit are left on 12 bit
        # so divide with 2^4 = 16 to get the celsius fractions
        value /= 16.0

        # check if the sensor value is the reset value
        if value == sensor_reset_value:
            raise ResetValueError(sensor_id)
    else:
        # Fallback to precalculated value for other sensor types
        value = get_raw_temperature(raw_temperature_line)
        value *= raw_temperature_to_degree_celsius_factor

    return factor(value + sensor_offset)


@lru_cache()
def evaluate_resolution(raw_temperature_line: str) -> int:
    # Byte 5 is the config register
    config_str = raw_temperature_line.split()[4]
    # Bit 5-6 contains the resolution, cut off the rest
    bit_base = int(config_str, 16) >> 5
    return bit_base + 9  # min. is 9 bits


@lru_cache()
def convert_raw_temperature_to_sensor_count(raw_temperature_line: str) -> int:
    """Convert the raw temperature from the kernel module to the raw integer ADC count

    Note: Must be divided depending on the max. sensor resolution
    to get floating point celsius

    :returns: the raw value from the sensor ADC
    :rtype: int

    :raises NoSensorFoundError: if the sensor could not be found
    :raises SensorNotReadyError: if the sensor is not ready yet
    """
    # two complement bytes, MSB comes after LSB!
    sensor_bytes = raw_temperature_line.split()

    # Convert from 16 bit hex string into int
    int16 = int(sensor_bytes[1] + sensor_bytes[0], 16)

    # check first signing bit
    if int16 >> 15 == 0:
        return int16  # positive values need no processing
    else:
        return int16 - (1 << 16)  # substract 2^16 to get correct negative value


@lru_cache()
def get_raw_temperature(raw_temperature_line: str) -> float:
    """Get the raw temperature from a temperature line

    :returns: the milicelsius value read from the sensor
    :rtype: int

    :raises NoSensorFoundError: if the sensor could not be found
    :raises SensorNotReadyError: if the sensor is not ready yet
    """
    return float(raw_temperature_line.split("=")[1])
