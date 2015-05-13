# -*- coding: utf-8 -*-

"""
    This module provides a temperature sensor of type w1 therm.
"""

from os import path, listdir, system
from time import sleep


class W1ThermSensorError(Exception):
    """Exception Baseclass for DS18B20 sensor errors"""
    pass


class KernelModuleLoadError(W1ThermSensorError):
    """Exception when the w1 therm kernel modules could not be loaded properly"""
    def __init__(self):
        W1ThermSensorError.__init__(self, "Cannot load w1 therm kernel modules")


class NoSensorFoundError(W1ThermSensorError):
    """Exception when no sensor is found"""
    def __init__(self, sensor_type, sensor_id):
        W1ThermSensorError.__init__(self, "No %s temperature sensor with id '%s' found" % (W1ThermSensor.TYPE_NAMES.get(sensor_type, "Unknown"), sensor_id))


class SensorNotReadyError(W1ThermSensorError):
    """Exception when the sensor is not ready yet"""
    def __init__(self):
        W1ThermSensorError.__init__(self, "Sensor is not yet ready to read temperature")


class UnsupportedUnitError(W1ThermSensorError):
    """Exception when unsupported unit is given"""
    def __init__(self):
        W1ThermSensorError.__init__(self, "Only Degress C, F and Kelvin are currently supported")


class W1ThermSensor(object):
    """This class represents a temperature sensor of type w1-therm"""
    THERM_SENSOR_DS18S20 = 0x10
    THERM_SENSOR_DS1822 = 0x22
    THERM_SENSOR_DS18B20 = 0x28
    DEGREES_C = 0x01
    DEGREES_F = 0x02
    KELVIN = 0x03
    BASE_DIRECTORY = "/sys/bus/w1/devices"
    SLAVE_FILE = "w1_slave"
    UNIT_FACTORS = {DEGREES_C: lambda x: x * 0.001, DEGREES_F: lambda x: x * 0.001 * 1.8 + 32.0, KELVIN: lambda x: x * 0.001 + 273.15}
    TYPE_NAMES = {THERM_SENSOR_DS18S20: "DS18S20", THERM_SENSOR_DS1822: "DS1822", THERM_SENSOR_DS18B20: "DS18B20"}
    RESOLVE_TYPE_STR = {"10": THERM_SENSOR_DS18S20, "22": THERM_SENSOR_DS1822, "28": THERM_SENSOR_DS18B20}
    RETRY_ATTEMPS = 10
    RETRY_DELAY_SECONDS = 1.0 / float(RETRY_ATTEMPS)

    @classmethod
    def get_available_sensors(cls, types=None):
        """
            Return all available sensors.

            :param list types: the of the sensor to look for. If types is None it will search for all available types.

            :returns: a list of sensor instances.
            :rtype: list

        """
        if not types:
            types = [W1ThermSensor.THERM_SENSOR_DS18S20, W1ThermSensor.THERM_SENSOR_DS1822, W1ThermSensor.THERM_SENSOR_DS18B20]
        is_sensor = lambda s: any(s.startswith(hex(x)[2:]) for x in types)
        return [cls(cls.RESOLVE_TYPE_STR[s[:2]], s[3:]) for s in listdir(cls.BASE_DIRECTORY) if is_sensor(s)]

    def __init__(self, sensor_type=None, sensor_id=None):
        """
            Initializes a W1ThermSensor.
            If the W1ThermSensor base directory is not found it will automatically load
            the needed kernel modules to make this directory available.
            If the expected directory will not be created after some time an exception is raised.

            If no type and no id are given the first found sensor will be taken for this instance.

            :param int sensor_type: the type of the sensor.
            :param string id: the id of the sensor.

            :raises KernelModuleLoadError: if the w1 therm kernel modules could not be loaded correctly
            :raises NoSensorFoundError: if the sensor with the given type and/or id does not exist or is not connected
        """
        # try to load kernel modules
        self._load_kernel_modules()

        self._type = sensor_type
        self._id = sensor_id
        if not sensor_type and not sensor_id:  # take first found sensor
            for i in range(W1ThermSensor.RETRY_ATTEMPS):
                s = W1ThermSensor.get_available_sensors()
                if s:
                    self._type, self._id = s[0].type, s[0].id
                    break
                sleep(self.RETRY_DELAY_SECONDS)
            else:
                raise NoSensorFoundError(None, "")
        elif not sensor_id:
            s = W1ThermSensor.get_available_sensors([sensor_type])
            if not s:
                raise NoSensorFoundError(sensor_type, "")
            self._id = s[0].id

        # store path to sensor
        self._sensorpath = path.join(W1ThermSensor.BASE_DIRECTORY, self.slave_prefix + self._id, W1ThermSensor.SLAVE_FILE)

        if not self.exists():
            raise NoSensorFoundError(self._type, self._id)

    def _load_kernel_modules(self):
        """
            Load kernel modules needed by the temperature sensor
            if they are not already loaded.
            If the base directory then does not exist an exception is raised an the kernel module loading
            should be treated as failed.

            :raises KernelModuleLoadError: if the kernel module could not be loaded properly
        """
        if not path.isdir(W1ThermSensor.BASE_DIRECTORY):
            system("modprobe w1-gpio")
            system("modprobe w1-therm")

        for i in range(self.RETRY_ATTEMPS):
            if path.isdir(W1ThermSensor.BASE_DIRECTORY):  # w1 therm modules loaded correctly
                break
            sleep(self.RETRY_DELAY_SECONDS)
        else:
            raise KernelModuleLoadError()

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
        return "{}(name='{}', type={}(0x{:x}), id='{}')".format(
            self.__class__.__name__, self.type_name, self.type, self.type, self.id)

    @property
    def id(self):
        """Returns the id of the sensor"""
        return self._id

    @property
    def type(self):
        """Returns the type of this temperature sensor"""
        return self._type

    @property
    def type_name(self):
        """Returns the type name of this temperature sensor"""
        return W1ThermSensor.TYPE_NAMES.get(self._type, "Unknown")

    @property
    def slave_prefix(self):
        """Returns the slave prefix for this temperature sensor"""
        return "%s-" % hex(self._type)[2:]

    @property
    def sensorpath(self):
        """Returns the path to the sensor kernel file"""
        return self._sensorpath

    def exists(self):
        """Returns the sensors slave path"""
        return path.exists(self._sensorpath)

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
            with open(self._sensorpath, "r") as f:
                data = f.readlines()
        except IOError:
            raise NoSensorFoundError(self._type, self._id)

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

            :returns: the sensor temperature in the given units. The order of the temperatures matches the order of the given units.
            :rtype: list

            :raises UnsupportedUnitError: if the unit is not supported
            :raises NoSensorFoundError: if the sensor could not be found
            :raises SensorNotReadyError: if the sensor is not ready yet
        """
        sensor_value = self.raw_sensor_value
        return [self._get_unit_factor(unit)(sensor_value) for unit in units]
