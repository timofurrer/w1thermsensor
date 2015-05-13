# -*- coding: utf-8 -*-

"""
    This module provides a temperature sensor of type w1 therm.
"""

__version__ = "0.2.2"
__author__ = "Timo Furrer"
__email__ = "tuxtimo@gmail.com"

from w1thermsensor.core import W1ThermSensor, NoSensorFoundError, SensorNotReadyError, UnsupportedUnitError
