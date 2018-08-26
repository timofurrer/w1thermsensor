# -*- coding: utf-8 -*-

"""
    This module provides a temperature sensor of type w1 therm.
"""

from .core import W1ThermSensor  # noqa
from .errors import NoSensorFoundError  # noqa
from .errors import SensorNotReadyError  # noqa
from .errors import UnsupportedUnitError  # noqa
from .errors import ResetValueError  # noqa

__version__ = "1.0.5"
__author__ = "Timo Furrer"
__email__ = "tuxtimo@gmail.com"
