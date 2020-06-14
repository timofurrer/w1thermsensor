"""
This module provides a temperature sensor of type w1 therm.
"""

import os
import subprocess
import time
from pathlib import Path

from w1thermsensor.errors import (
    KernelModuleLoadError,
    NoSensorFoundError,
    ResetValueError,
    SensorNotReadyError,
    W1ThermSensorError
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

    #: Holds settings for patient retries used to access the sensors
    RETRY_ATTEMPTS = 10
    RETRY_DELAY_SECONDS = 1.0 / RETRY_ATTEMPTS

    @classmethod
    def get_available_sensors(cls, types=None):
        """
            Return all available sensors.

            :param list types: the type of the sensor to look for.
                               If types is None it will search for all available types.

            :returns: a list of sensor instances.
            :rtype: list

        """
        if not types:
            types = list(Sensor)
        else:
            types = [s if isinstance(s, Sensor) else Sensor[s] for s in types]

        is_sensor = lambda s: any(s.name.startswith(hex(x.value)[2:]) for x in types)  # noqa
        return [
            cls(Sensor.from_id_string(s.name[:2]), s.name[3:])
            for s in cls.BASE_DIRECTORY.iterdir()
            if is_sensor(s)
        ]

    def __init__(
        self, sensor_type=None, sensor_id=None, offset=0.0, offset_unit=Unit.DEGREES_C
    ):
        """
            Initializes a W1ThermSensor.
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
        if not sensor_type and not sensor_id:  # take first found sensor
            for _ in range(self.RETRY_ATTEMPTS):
                s = self.get_available_sensors()
                if s:
                    self.type, self.id = s[0].type, s[0].id
                    break
                time.sleep(self.RETRY_DELAY_SECONDS)
            else:
                raise NoSensorFoundError("Could not find any sensor")
        elif not sensor_id:
            s = self.get_available_sensors([sensor_type])
            if not s:
                try:
                    sensor_type_name = Sensor(sensor_type)
                except ValueError:  # no known sensor, create anyway for error message
                    sensor_type = hex(sensor_type)
                error_msg = "Could not find any sensor of type {}".format(
                    sensor_type_name
                )
                raise NoSensorFoundError(error_msg)

            self.type = sensor_type
            self.id = s[0].id
        elif not sensor_type:  # get sensor by id
            sensor = next(
                (s for s in self.get_available_sensors() if s.id == sensor_id), None
            )
            if not sensor:
                raise NoSensorFoundError(
                    "Could not find sensor with id {}".format(sensor_id)
                )
            self.type = sensor.type
            self.id = sensor.id
        else:
            self.type = sensor_type
            self.id = sensor_id

        # store path to sensor
        self.sensorpath = self.BASE_DIRECTORY / (self.slave_prefix + self.id) / self.SLAVE_FILE

        if not self.exists():
            raise NoSensorFoundError(
                "Could not find sensor of type {} with id {}".format(
                    self.name, self.id
                )
            )

        self.set_offset(offset, offset_unit)

    def __repr__(self):
        """
            Returns a string that eval can turn back into this object

            :returns: representation of this instance
            :rtype: string
        """
        return "{}(sensor_type={}, sensor_id='{}')".format(
            self.__class__.__name__, str(self.type), self.id
        )

    def __str__(self):
        """
            Returns a pretty string respresentation

            :returns: representation of this instance
            :rtype: string
        """
        return "{0}(name='{1}', type={2}(0x{2:x}), id='{3}')".format(
            self.__class__.__name__, self.type.name, self.type.value, self.id
        )

    @property
    def name(self):
        """Returns the type name of this temperature sensor"""
        return self.type.name

    @property
    def slave_prefix(self):
        """Returns the slave prefix for this temperature sensor"""
        return "%s-" % hex(self.type.value)[2:]

    def exists(self):
        """Returns the sensors slave path"""
        return self.sensorpath.exists()

    @property
    def raw_sensor_strings(self):
        """
            Reads the raw strings from the kernel module sysfs interface

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
                "Could not find sensor of type {} with id {}".format(
                    self.name, self.id
                )
            )

        if data[0].strip()[-3:] != "YES" or "00 00 00 00 00 00 00 00 00" in data[0]:
            raise SensorNotReadyError(self)

        return data

    @property
    def raw_sensor_count(self):
        """
            Returns the raw integer ADC count from the sensor

            Note: Must be divided depending on the max. sensor resolution
            to get floating point celsius

            :returns: the raw value from the sensor ADC
            :rtype: int

            :raises NoSensorFoundError: if the sensor could not be found
            :raises SensorNotReadyError: if the sensor is not ready yet
        """

        # two complement bytes, MSB comes after LSB!
        bytes = self.raw_sensor_strings[1].split()

        # Convert from 16 bit hex string into int
        int16 = int(bytes[1] + bytes[0], 16)

        # check first signing bit
        if int16 >> 15 == 0:
            return int16  # positive values need no processing
        else:
            return int16 - (1 << 16)  # substract 2^16 to get correct negative value

    @property
    def raw_sensor_temp(self):
        """
            Returns the raw sensor value in milicelsius

            :returns: the milicelsius value read from the sensor
            :rtype: int

            :raises NoSensorFoundError: if the sensor could not be found
            :raises SensorNotReadyError: if the sensor is not ready yet
        """

        # return the value in millicelsius
        return float(self.raw_sensor_strings[1].split("=")[1])

    def get_temperature(self, unit=Unit.DEGREES_C):
        """
            Returns the temperature in the specified unit

            :param int unit: the unit of the temperature requested

            :returns: the temperature in the given unit
            :rtype: float

            :raises UnsupportedUnitError: if the unit is not supported
            :raises NoSensorFoundError: if the sensor could not be found
            :raises SensorNotReadyError: if the sensor is not ready yet
            :raises ResetValueError: if the sensor has still the initial value and no measurment
        """
        if self.type.comply_12bit_standard():
            value = self.raw_sensor_count
            # the int part is 8 bit wide, 4 bit are left on 12 bit
            # so divide with 2^4 = 16 to get the celsius fractions
            value /= 16.0

            # check if the sensor value is the reset value
            if value == 85.0:
                raise ResetValueError(self)

            factor = Unit.get_conversion_function(Unit.DEGREES_C, unit)
            return factor(value + self.offset)

        # Fallback to precalculated value for other sensor types
        factor = Unit.get_conversion_function(Unit.DEGREES_C, unit)
        return factor((self.raw_sensor_temp * 0.001) + self.offset)

    def get_temperatures(self, units):
        """
            Returns the temperatures in the specified units

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
            Unit.get_conversion_function(Unit.DEGREES_C, unit)(sensor_value) for unit in units
        ]

    def get_resolution(self):
        """
            Get the current resolution from the sensor.

            :returns: sensor resolution from 9-12 bits
            :rtype: int
        """
        config_str = self.raw_sensor_strings[1].split()[
            4
        ]  # Byte 5 is the config register
        bit_base = (
            int(config_str, 16) >> 5
        )  # Bit 5-6 contains the resolution, cut off the rest
        return bit_base + 9  # min. is 9 bits

    def set_resolution(self, resolution, persist=False):
        """
            Set the resolution of the sensor for the next readings.

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

    def set_offset(self, offset, unit=Unit.DEGREES_C):
        """
            Set an offset to be applied to each temperature reading. This is
            used to tune sensors which report values which are either too high
            or too low.

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

    def get_offset(self, unit=Unit.DEGREES_C):
        """
            Get the offset set for this sensor. If no offset has been set, 0.0
            is returned.

            :param: int unit: The unit to return the temperature offset in

            :returns: The offset set for this temperature sensor
            :rtype: float
        """

        # We need to subtract `factor(0)` from the result, in order to
        # eliminate any offset temperatures used in the conversion formulas
        # (such as 32F, when converting from C to F).
        factor = Unit.get_conversion_function(Unit.DEGREES_C, unit)
        return factor(self.offset) - factor(0)


def load_kernel_modules():
    """
    Load kernel modules needed by the temperature sensor
    if they are not already loaded.
    If the base directory then does not exist an exception is raised an the kernel module loading
    should be treated as failed.

    :raises KernelModuleLoadError: if the kernel module could not be loaded properly
    """
    if not W1ThermSensor.BASE_DIRECTORY.is_dir():
        os.system("modprobe w1-gpio >/dev/null 2>&1")
        os.system("modprobe w1-therm >/dev/null 2>&1")

    for _ in range(W1ThermSensor.RETRY_ATTEMPTS):
        if W1ThermSensor.BASE_DIRECTORY.is_dir():
            # w1 therm modules loaded correctly
            break
        time.sleep(W1ThermSensor.RETRY_DELAY_SECONDS)
    else:
        raise KernelModuleLoadError()


# Load kernel modules automatically upon import.
# Set the environment variable W1THERMSENSOR_NO_KERNEL_MODULE=1
if os.environ.get("W1THERMSENSOR_NO_KERNEL_MODULE", "0") != "1":
    load_kernel_modules()
