# -*- coding: utf-8 -*-

"""
    This module provides a temperature sensor of type w1 therm.
"""

__description__ = "A Python package and CLI tool to work with w1 temperature sensors like DS1822, DS18S20 & DS18B20 on the Raspberry Pi, Beagle Bone and other devices."  # noqa
__license__ = "MIT"
__version__ = "1.3.0"
__author__ = "Timo Furrer"
__author_email__ = "tuxtimo@gmail.com"
__url__ = "http://github.com/timofurrer/w1thermsensor"
__download_url__ = "http://github.com/timofurrer/w1thermsensor"


from .core import W1ThermSensor  # noqa
from .errors import NoSensorFoundError  # noqa
from .errors import SensorNotReadyError  # noqa
from .errors import UnsupportedUnitError  # noqa
from .errors import ResetValueError  # noqa
