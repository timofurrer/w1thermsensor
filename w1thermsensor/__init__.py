# -*- coding: utf-8 -*-

"""
    This module provides a temperature sensor of type w1 therm.
"""

from .core import W1ThermSensor  # noqa
from .errors import NoSensorFoundError, SensorNotReadyError, UnsupportedUnitError  # noqa

__version__ = "1.0.2"
__author__ = "Timo Furrer"
__email__ = "tuxtimo@gmail.com"
