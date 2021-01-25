"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2020 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

__description__ = "A Python package and CLI tool to work with w1 temperature sensors like DS1822, DS18S20 & DS18B20 on the Raspberry Pi, Beagle Bone and other devices."  # noqa
__license__ = "MIT"
__version__ = "2.0.0"
__author__ = "Timo Furrer"
__author_email__ = "tuxtimo@gmail.com"
__url__ = "http://github.com/timofurrer/w1thermsensor"
__download_url__ = "http://github.com/timofurrer/w1thermsensor"

import os

from w1thermsensor.async_core import AsyncW1ThermSensor  # noqa
from w1thermsensor.core import W1ThermSensor  # noqa
from w1thermsensor.errors import (  # noqa
    KernelModuleLoadError,
    NoSensorFoundError,
    ResetValueError,
    SensorNotReadyError,
    UnsupportedUnitError,
    W1ThermSensorError
)
from w1thermsensor.kernel import load_kernel_modules
from w1thermsensor.sensors import Sensor  # noqa
from w1thermsensor.units import Unit  # noqa

# Load kernel modules automatically upon import.
# Set the environment variable W1THERMSENSOR_NO_KERNEL_MODULE=1
if os.environ.get("W1THERMSENSOR_NO_KERNEL_MODULE", "0") != "1":  # pragma: no cover
    load_kernel_modules()
