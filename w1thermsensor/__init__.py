# -*- coding: utf-8 -*-

"""
    This module provides a temperature sensor of type w1 therm.
"""

from .core import W1ThermSensor
from .errors import NoSensorFoundError, SensorNotReadyError, UnsupportedUnitError

__version__ = "0.4.3"
__author__ = "Timo Furrer"
__email__ = "tuxtimo@gmail.com"
