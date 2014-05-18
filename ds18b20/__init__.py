# -*- coding: utf-8 -*-

__version__ = "0.01.03"

from os import path, listdir, system
from glob import glob


class DS18B20(object):
    """This class represents a temperature sensor of type DS18B20"""
    DEGREES_C = 0x01
    DEGREES_F = 0x02
    KELVIN = 0x03
    BASE_DIRECTORY = "/sys/bus/w1/devices"
    SLAVE_PREFIX = "28-"
    SLAVE_FILE = "w1_slave"
    UNIT_FACTORS = {DEGREES_C: lambda x: x * 0.001, DEGREES_F: lambda x: x * 0.001 * 1.8 + 32.0, KELVIN: lambda x: x * 0.001 + 273.15}

    class DS18B20Error(Exception):
        """Exception Baseclass for DS18B20 sensor errors"""
        pass

    class NoSensorFoundError(DS18B20Error):
        """Exception when no sensor is found"""
        def __init__(self, sensor_id):
            self._sensor_id = sensor_id

        def __str__(self):
            if self._sensor_id:
                return "No DS18B20 temperature sensor with id '%s' found" % self._sensor_id
            return "No DS18B20 temperature sensor found"

    class SensorNotReadyError(DS18B20Error):
        """Exception when the sensor is not ready yet"""
        def __str__(self):
            return "Sensor is not yet ready to read temperature"

    class UnsupportedUnitError(DS18B20Error):
        """Exception when unsupported unit is given"""
        def __str__(self):
            return "Only Degress C, F and Kelvin are currently supported"

    @classmethod
    def get_available_sensors(cls):
        """Returns all available sensors"""
        sensors = []
        for sensor in listdir(cls.BASE_DIRECTORY):
            if sensor.startswith(cls.SLAVE_PREFIX):
                sensors.append(sensor[3:])
        return sensors

    @classmethod
    def get_all_sensors(cls):
        """Returns an instance for every available DS18B20 sensor"""
        return [DS18B20(sensor_id) for sensor_id in cls.get_available_sensors()]

    def __init__(self, sensor_id=None, load_kernel_modules=True):
        """If no sensor id is given the first found sensor will be taken"""
        self._type = "DS18B20"
        self._id = sensor_id
        if load_kernel_modules:
            self._load_kernel_modules()
        self._sensor = self._get_sensor()

    def get_id(self):
        """Returns the id of the sensor"""
        return self._id

    def get_type(self):
        """Returns the type of this temperature sensor"""
        return self._type

    def exists(self):
        """Returns True if the sensor exists and is available to read temperature"""
        path = self._get_sensor()
        return path is not None

    def _get_sensor(self):
        """Returns the sensors slave path"""
        sensors = self.get_available_sensors()
        if self._id and self._id not in sensors:
            raise DS18B20.NoSensorFoundError(sensor_id)

        if not self._id and sensors:
            self._id = sensors[0]

        return path.join(DS18B20.BASE_DIRECTORY, DS18B20.SLAVE_PREFIX + self._id, DS18B20.SLAVE_FILE)

    def _get_sensor_value(self):
        """Returns the raw sensor value"""
        with open(self._sensor, "r") as f:
            data = f.readlines()

        if data[0].strip()[-3:] != "YES":
            raise DS18B20.SensorNotReadyError()
        return float(data[1].split("=")[1])

    def _get_unit_factor(self, unit):
        """Returns the unit factor depending on the unit constant"""
        try:
            return DS18B20.UNIT_FACTORS[unit]
        except KeyError:
            raise DS18B20.UnsupportedUnitError()

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
