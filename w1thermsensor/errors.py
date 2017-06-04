# -*- coding: utf-8 -*-

"""
This module provides exceptions for the w1thermsensor.
"""


class W1ThermSensorError(Exception):
    """Exception base-class for W1ThermSensor errors"""
    pass


class KernelModuleLoadError(W1ThermSensorError):
    """Exception when the w1 therm kernel modules could not be loaded properly"""
    def __init__(self):
        super(KernelModuleLoadError, self).__init__("Cannot load w1 therm kernel modules")


class NoSensorFoundError(W1ThermSensorError):
    """Exception when no sensor is found"""
    def __init__(self, sensor_name, sensor_id):
        super(NoSensorFoundError, self).__init__(
            "No {0} temperature sensor with id '{1}' found".format(
                sensor_name, sensor_id))


class SensorNotReadyError(W1ThermSensorError):
    """Exception when the sensor is not ready yet"""
    def __init__(self):
        super(SensorNotReadyError, self).__init__(
            "Sensor is not yet ready to read temperature")


class UnsupportedUnitError(W1ThermSensorError):
    """Exception when unsupported unit is given"""
    def __init__(self):
        super(UnsupportedUnitError, self).__init__(
            "Only Degrees C, F and Kelvin are currently supported")
