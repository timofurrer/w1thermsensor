# -*- coding: utf-8 -*-

"""
This module provides a temperature sensor of type w1 therm.
"""

import os
import time
import subprocess

from .errors import W1ThermSensorError, NoSensorFoundError, SensorNotReadyError
from .errors import KernelModuleLoadError, UnsupportedUnitError


class W1ThermSensor(object):
    """
    Represents a w1 therm sensor connected to the device accessed by
    the Linux w1 therm sensor kernel modules.

    Supported sensors are:
        * DS18S20
        * DS1822
        * DS18B20
        * DS1825
        * DS28EA00
        * MAX31850K

    Supported temperature units are:
        * Kelvin
        * Celsius
        * Fahrenheit
    """

    #: Holds information about supported w1therm sensors
    THERM_SENSOR_DS18S20 = 0x10
    THERM_SENSOR_DS1822 = 0x22
    THERM_SENSOR_DS18B20 = 0x28
    THERM_SENSOR_DS1825 = 0x3B
    THERM_SENSOR_DS28EA00 = 0x42
    THERM_SENSOR_MAX31850K = 0x3B
    TYPE_NAMES = {
        THERM_SENSOR_DS18S20: "DS18S20", THERM_SENSOR_DS1822: "DS1822",
        THERM_SENSOR_DS18B20: "DS18B20", THERM_SENSOR_DS1825: "DS1825",
        THERM_SENSOR_DS28EA00: "DS28EA00", THERM_SENSOR_MAX31850K: "MAX31850K"
    }
    RESOLVE_TYPE_STR = {
        "10": THERM_SENSOR_DS18S20, "22": THERM_SENSOR_DS1822, "28": THERM_SENSOR_DS18B20,
        "42": THERM_SENSOR_DS28EA00, "3b": THERM_SENSOR_MAX31850K
    }

    #: Holds information about the location of the needed
    #  sensor devices on the system provided by the kernel modules
    BASE_DIRECTORY = "/sys/bus/w1/devices"
    SLAVE_FILE = "w1_slave"

    #: Holds information about temperature type conversion
    DEGREES_C = 0x01
    DEGREES_F = 0x02
    KELVIN = 0x03
    UNIT_FACTORS = {
        DEGREES_C: lambda x: x * 0.001,
        DEGREES_F: lambda x: x * 0.001 * 1.8 + 32.0,
        KELVIN: lambda x: x * 0.001 + 273.15
    }
    UNIT_FACTOR_NAMES = {
        "celsius": DEGREES_C,
        "fahrenheit": DEGREES_F,
        "kelvin": KELVIN
    }

    #: Holds settings for patient retries used to access the sensors
    RETRY_ATTEMPTS = 10
    RETRY_DELAY_SECONDS = 1.0 / float(RETRY_ATTEMPTS)

    @classmethod
    def get_available_sensors(cls, types=None):
        """
            Return all available sensors.

            :param list types: the of the sensor to look for.
                               If types is None it will search for all available types.

            :returns: a list of sensor instances.
            :rtype: list

        """
        if not types:
            types = cls.TYPE_NAMES.keys()
        is_sensor = lambda s: any(s.startswith(hex(x)[2:]) for x in types)  # noqa
        return [cls(cls.RESOLVE_TYPE_STR[s[:2]], s[3:]) for s
                in os.listdir(cls.BASE_DIRECTORY) if is_sensor(s)]

    def __init__(self, sensor_type=None, sensor_id=None):
        """
            Initializes a W1ThermSensor.
            If the W1ThermSensor base directory is not found it will automatically load
            the needed kernel modules to make this directory available.
            If the expected directory will not be created after some time an exception is raised.

            If no type and no id are given the first found sensor will be taken for this instance.

            :param int sensor_type: the type of the sensor.
            :param string id: the id of the sensor.

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
                raise NoSensorFoundError("Unknown", "")
        elif not sensor_id:
            s = self.get_available_sensors([sensor_type])
            if not s:
                raise NoSensorFoundError(self.TYPE_NAMES.get(sensor_type, "Unknown"), "")
            self.type = sensor_type
            self.id = s[0].id
        elif not sensor_type:  # get sensor by id
            sensor = next((s for s in self.get_available_sensors() if s.id == sensor_id), None)
            if not sensor:
                raise NoSensorFoundError('N/A', sensor_id)
            self.type = sensor.type
            self.id = sensor.id
        else:
            self.type = sensor_type
            self.id = sensor_id

        # store path to sensor
        self.sensorpath = os.path.join(self.BASE_DIRECTORY,
                                       self.slave_prefix + self.id, self.SLAVE_FILE)

        if not self.exists():
            raise NoSensorFoundError(self.type_name, self.id)

    def __repr__(self):
        """
            Returns a string that eval can turn back into this object

            :returns: representation of this instance
            :rtype: string
        """
        return "{}(sensor_type={}, sensor_id='{}')".format(
            self.__class__.__name__, self.type, self.id)

    def __str__(self):
        """
            Returns a pretty string respresentation

            :returns: representation of this instance
            :rtype: string
        """
        return "{0}(name='{1}', type={2}(0x{2:x}), id='{3}')".format(
            self.__class__.__name__, self.type_name, self.type, self.id)

    @property
    def type_name(self):
        """Returns the type name of this temperature sensor"""
        return self.TYPE_NAMES.get(self.type, "Unknown")

    @property
    def slave_prefix(self):
        """Returns the slave prefix for this temperature sensor"""
        return "%s-" % hex(self.type)[2:]

    def exists(self):
        """Returns the sensors slave path"""
        return os.path.exists(self.sensorpath)

    @property
    def raw_sensor_value(self):
        """
            Returns the raw sensor value

            :returns: the raw value read from the sensor
            :rtype: int

            :raises NoSensorFoundError: if the sensor could not be found
            :raises SensorNotReadyError: if the sensor is not ready yet
        """
        try:
            with open(self.sensorpath, "r") as f:
                data = f.readlines()
        except IOError:
            raise NoSensorFoundError(self.type_name, self.id)

        if data[0].strip()[-3:] != "YES":
            raise SensorNotReadyError()
        return float(data[1].split("=")[1])

    @classmethod
    def _get_unit_factor(cls, unit):
        """
            Returns the unit factor depending on the unit constant

            :param int unit: the unit of the factor requested

            :returns: a function to convert the raw sensor value to the given unit
            :rtype: lambda function

            :raises UnsupportedUnitError: if the unit is not supported
        """
        try:
            if isinstance(unit, str):
                unit = cls.UNIT_FACTOR_NAMES[unit]
            return cls.UNIT_FACTORS[unit]
        except KeyError:
            raise UnsupportedUnitError()

    def get_temperature(self, unit=DEGREES_C):
        """
            Returns the temperature in the specified unit

            :param int unit: the unit of the temperature requested

            :returns: the temperature in the given unit
            :rtype: float

            :raises UnsupportedUnitError: if the unit is not supported
            :raises NoSensorFoundError: if the sensor could not be found
            :raises SensorNotReadyError: if the sensor is not ready yet
        """
        factor = self._get_unit_factor(unit)
        return factor(self.raw_sensor_value)

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
        sensor_value = self.raw_sensor_value
        return [self._get_unit_factor(unit)(sensor_value) for unit in units]

    def set_precision(self, precision, persist=False):
        """
            Set the precision of the sensor for the next readings.

            If the ``persist`` argument is set to ``False`` this value
            is "only" stored in the volatile SRAM, so it is reset when
            the sensor gets power-cycled.

            If the ``persist`` argument is set to ``True`` the current set
            precision is stored into the EEPROM. Since the EEPROM has a limited
            amount of writes (>50k), this command should be used wisely.

            Note: root permissions are required to change the sensors precision.

            Note: This function is supported since kernel 4.7.

            :param int precision: the sensor precision in bits.
                                  Valid values are between 9 and 12
            :param bool persist: if the sensor precision should be written
                                 to the EEPROM.

            :returns: if the sensor precision could be set or not.
            :rtype: bool
        """
        if not 9 <= precision <= 12:
            raise ValueError("The given sensor precision '{0}' is out of range (9-12)".format(
                precision))

        exitcode = subprocess.call("echo {0} > {1}".format(
            precision, self.sensorpath), shell=True)
        if exitcode != 0:
            raise W1ThermSensorError("Failed to change resolution to {0} bit".format(precision))

        if persist:
            exitcode = subprocess.call("echo 0 > {0}".format(self.sensorpath), shell=True)
            if exitcode != 0:
                raise W1ThermSensorError("Failed to write precision configuration to sensor EEPROM")

        return True


def load_kernel_modules():
    """
    Load kernel modules needed by the temperature sensor
    if they are not already loaded.
    If the base directory then does not exist an exception is raised an the kernel module loading
    should be treated as failed.

    :raises KernelModuleLoadError: if the kernel module could not be loaded properly
    """
    if not os.path.isdir(W1ThermSensor.BASE_DIRECTORY):
        os.system("modprobe w1-gpio >/dev/null 2>&1")
        os.system("modprobe w1-therm >/dev/null 2>&1")

    for _ in range(W1ThermSensor.RETRY_ATTEMPTS):
        if os.path.isdir(W1ThermSensor.BASE_DIRECTORY):  # w1 therm modules loaded correctly
            break
        time.sleep(W1ThermSensor.RETRY_DELAY_SECONDS)
    else:
        raise KernelModuleLoadError()


# Load kernel modules automatically upon import.
# Set the environment variable W1THERMSENSOR_NO_KERNEL_MODULE=1
if os.environ.get('W1THERMSENSOR_NO_KERNEL_MODULE', '0') != '1':
    load_kernel_modules()
