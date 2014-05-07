# -*- coding: utf-8 -*-

__version__ = "0.01.01"

import sys
import os
from glob import glob

class DS18B20(object):
    """This class represents a temperature sensor of type DS18B20"""
    DEGREES_C = 0x01
    DEGREES_F = 0x02
    KELVIN = 0x03
    BASE_DIRECTORY = "/sys/bus/w1/devices"
    SLAVE_PREFIX = "28-*"
    SLAVE_FILE = "w1_slave"
    UNIT_FACTORS = {DEGREES_C: lambda x: x * 0.001, DEGREES_F: lambda x: x * 0.001 * 1.8 + 32.0, KELVIN: lambda x: x * 0.001 + 272.15}

    def __init__(self):
        self._type = "DS18B20"
        self._load_kernel_modules()

    def get_type(self):
        """Returns the type of this temperature sensor"""
        return self._type

    def exists(self):
        """Returns True if the sensor exists and is available to read temperature"""
        path = self._get_slave_path()
        return path is not None

    def _get_slave_path(self):
        """Returns the slaves path"""
        slave_path = os.path.join(DS18B20.BASE_DIRECTORY, DS18B20.SLAVE_PREFIX, DS18B20.SLAVE_FILE)
        globbed = glob(slave_path)
        if globbed:
            return globbed[0]
        return None

    def _get_sensor_value(self):
        """Returns the raw sensor value"""
        slave_path = self._get_slave_path()
        with open(slave_path, "r") as f:
            data = f.readlines()
        if data[0].strip()[-3:] != "YES":
            sys.stderr.write("Sensor is not yet ready to read temperature\n")
            return 0
        return float(data[1].split("=")[1])

    def _get_unit_factor(self, unit):
        """Returns the unit factor depending on the unit constant"""
        try:
            return DS18B20.UNIT_FACTORS[unit]
        except KeyError:
            sys.stderr.write("Only Degress C, F and Kelvin are currently supported\n")
            return lambda x: 0

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
        os.system("modprobe w1-gpio")
        os.system("modprobe w1-therm")
