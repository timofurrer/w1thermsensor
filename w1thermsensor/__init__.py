# -*- coding: utf-8 -*-

__version__ = "0.02.00"
__author__ = "Timo Furrer"
__email__ = "tuxtimo@gmail.com"

from os import path, listdir, system
from glob import glob


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
    LOAD_KERNEL_MODULES = True
    UNIT_FACTORS = {DEGREES_C: lambda x: x * 0.001, DEGREES_F: lambda x: x * 0.001 * 1.8 + 32.0, KELVIN: lambda x: x * 0.001 + 273.15}
    TYPE_NAMES = {THERM_SENSOR_DS18S20: "DS18S20", THERM_SENSOR_DS1822: "DS1822", THERM_SENSOR_DS18B20: "DS18B20"}
    RESOLVE_TYPE_STR = {"10": THERM_SENSOR_DS18S20, "22": THERM_SENSOR_DS1822, "28": THERM_SENSOR_DS18B20}

    class DS18B20Error(Exception):
        """Exception Baseclass for DS18B20 sensor errors"""
        pass

    class NoSensorFoundError(DS18B20Error):
        """Exception when no sensor is found"""
        def __init__(self, sensor_type, sensor_id):
            self._sensor_type = sensor_type
            self._sensor_id = sensor_id

        def __str__(self):
            return "No %s temperature sensor with id '%s' found" % (W1ThermSensor.TYPE_NAMES.get(self._sensor_type, "Unknown"), self._sensor_id)

    class SensorNotReadyError(DS18B20Error):
        """Exception when the sensor is not ready yet"""
        def __str__(self):
            return "Sensor is not yet ready to read temperature"

    class UnsupportedUnitError(DS18B20Error):
        """Exception when unsupported unit is given"""
        def __str__(self):
            return "Only Degress C, F and Kelvin are currently supported"

    @classmethod
    def get_available_sensors(cls, types=[THERM_SENSOR_DS18S20, THERM_SENSOR_DS1822, THERM_SENSOR_DS18B20]):
        """Returns all available sensors"""
        is_sensor = lambda s: any(s.startswith(hex(x)[2:]) for x in types)
        return [cls(cls.RESOLVE_TYPE_STR[s[:2]], s[3:]) for s in listdir(cls.BASE_DIRECTORY) if is_sensor(s)]

    def __init__(self, sensor_type=None, sensor_id=None):
        """If no sensor id is given the first found sensor will be taken"""
        self._type = sensor_type
        self._id = sensor_id
        if not sensor_type and not sensor_id:
            s = W1ThermSensor.get_available_sensors()
            if not s:
                raise W1ThermSensor.NoSensorFoundError(None, "")
            self._type = s[0].type
            self._id = s[0].id
        elif not sensor_id:
            s = W1ThermSensor.get_available_sensors([sensor_type])
            if not s:
                raise W1ThermSensor.NoSensorFoundError(sensor_type, "")
            self._id = s[0].id

        if W1ThermSensor.LOAD_KERNEL_MODULES:
            self._load_kernel_modules()
        self._sensor = self._get_sensor()

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

    def _get_sensor(self):
        """Returns the sensors slave path"""
        sensor_path = path.join(W1ThermSensor.BASE_DIRECTORY, self.slave_prefix + self._id, W1ThermSensor.SLAVE_FILE)
        if not path.exists(sensor_path):
            raise W1ThermSensor.NoSensorFoundError(self._type, self._id)

        return sensor_path

    def _get_sensor_value(self):
        """Returns the raw sensor value"""
        with open(self._sensor, "r") as f:
            data = f.readlines()

        if data[0].strip()[-3:] != "YES":
            raise W1ThermSensor.SensorNotReadyError()
        return float(data[1].split("=")[1])

    def _get_unit_factor(self, unit):
        """Returns the unit factor depending on the unit constant"""
        try:
            return W1ThermSensor.UNIT_FACTORS[unit]
        except KeyError:
            raise W1ThermSensor.UnsupportedUnitError()

    def get_temperature(self, unit=DEGREES_C):
        """Returns the temperature in the specified unit"""
        factor = self._get_unit_factor(unit)
        sensor_value = self._get_sensor_value()
        return factor(sensor_value)

    def get_temperatures(self, units):
        """Returns the temperatures in the specified units"""
        sensor_value = self._get_sensor_value()
        temperatures = []
        for unit in units:
            factor = self._get_unit_factor(unit)
            temperatures.append(factor(sensor_value))
        return temperatures

    def _load_kernel_modules(self):
        """Load kernel modules needed by the temperature sensor"""
        system("modprobe w1-gpio")
        system("modprobe w1-therm")
