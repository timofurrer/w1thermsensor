# -*- coding: utf-8 -*-

"""
    This module provides a temperature sensor of type w1 therm.
"""

__version__ = "0.02.01"
__author__ = "Timo Furrer"
__email__ = "tuxtimo@gmail.com"

from os import path, listdir, system
from glob import glob
from time import sleep


class W1ThermSensorError(Exception):
    """Exception Baseclass for DS18B20 sensor errors"""
    pass

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
        """Returns all available sensors"""
        if not types:
            types = [W1ThermSensor.THERM_SENSOR_DS18S20, W1ThermSensor.THERM_SENSOR_DS1822, W1ThermSensor.THERM_SENSOR_DS18B20]
        is_sensor = lambda s: any(s.startswith(hex(x)[2:]) for x in types)
        return [cls(cls.RESOLVE_TYPE_STR[s[:2]], s[3:]) for s in listdir(cls.BASE_DIRECTORY) if is_sensor(s)]

    def __init__(self, sensor_type=None, sensor_id=None):
        """If no sensor id is given the first found sensor will be taken"""
        if not path.isdir(W1ThermSensor.BASE_DIRECTORY):
            self._load_kernel_modules()
        check_base_dir_attempts = 0
        while not path.isdir(W1ThermSensor.BASE_DIRECTORY) and check_base_dir_attempts <= self.RETRY_ATTEMPS:
            sleep(W1ThermSensor.RETRY_DELAY_SECONDS)
            check_base_dir_attempts += 1
        self._type = sensor_type
        self._id = sensor_id
        if not sensor_type and not sensor_id:
            s = W1ThermSensor.get_available_sensors()
            find_sensor_attemps = 0
            while not s and find_sensor_attemps <= W1ThermSensor.RETRY_ATTEMPS:
                sleep(W1ThermSensor.RETRY_DELAY_SECONDS)
                find_sensor_attemps += 1
                s = W1ThermSensor.get_available_sensors()
            if not s:
                raise NoSensorFoundError(None, "")
            self._type, self._id = s[0].type, s[0].id
        elif not sensor_id:
            s = W1ThermSensor.get_available_sensors([sensor_type])
            if not s:
                raise NoSensorFoundError(sensor_type, "")
            self._id = s[0].id

        self._sensorpath = self.sensorpath

    def __repr__(self):
        """ Returns a string that eval can turn back into this object """
        return "{}(sensor_type={}, sensor_id='{}')".format(
            self.__class__.__name__, self.type, self.id)

    def __str__(self):
        """ Returns a pretty string respresentation """
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
        """Returns the sensors slave path"""
        sensor_path = path.join(W1ThermSensor.BASE_DIRECTORY, self.slave_prefix + self._id, W1ThermSensor.SLAVE_FILE)
        if not path.exists(sensor_path):
            raise NoSensorFoundError(self._type, self._id)

        return sensor_path

    @property
    def raw_sensor_value(self):
        """Returns the raw sensor value"""
        with open(self.sensorpath, "r") as f:
            data = f.readlines()

        if data[0].strip()[-3:] != "YES":
            raise SensorNotReadyError()
        return float(data[1].split("=")[1])

    @classmethod
    def _get_unit_factor(cls, unit):
        """Returns the unit factor depending on the unit constant"""
        try:
            return cls.UNIT_FACTORS[unit]
        except KeyError:
            raise UnsupportedUnitError()

    def get_temperature(self, unit=DEGREES_C):
        """Returns the temperature in the specified unit"""
        factor = self._get_unit_factor(unit)
        return factor(self.raw_sensor_value)

    def get_temperatures(self, units):
        """Returns the temperatures in the specified units"""
        sensor_value = self.raw_sensor_value
        return [self._get_unit_factor(unit)(sensor_value) for unit in units]

    @staticmethod
    def _load_kernel_modules():
        """Load kernel modules needed by the temperature sensor"""
        system("modprobe w1-gpio")
        system("modprobe w1-therm")
