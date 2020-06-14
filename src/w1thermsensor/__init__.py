"""
    This module provides a temperature sensor of type w1 therm.
"""

__description__ = "A Python package and CLI tool to work with w1 temperature sensors like DS1822, DS18S20 & DS18B20 on the Raspberry Pi, Beagle Bone and other devices."  # noqa
__license__ = "MIT"
__version__ = "2.0.0a1"
__author__ = "Timo Furrer"
__author_email__ = "tuxtimo@gmail.com"
__url__ = "http://github.com/timofurrer/w1thermsensor"
__download_url__ = "http://github.com/timofurrer/w1thermsensor"


from w1thermsensor.core import W1ThermSensor  # noqa
from w1thermsensor.errors import (  # noqa
    NoSensorFoundError,
    ResetValueError,
    SensorNotReadyError,
    UnsupportedUnitError
)
from w1thermsensor.units import Unit  # noqa
