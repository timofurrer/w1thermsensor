"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2020 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import os
import time

from w1thermsensor.core import W1ThermSensor
from w1thermsensor.errors import KernelModuleLoadError


def load_kernel_modules() -> None:
    """
    Load kernel modules needed by the temperature sensor
    if they are not already loaded.
    If the base directory then does not exist an exception is raised an the kernel module loading
    should be treated as failed.

    :raises KernelModuleLoadError: if the kernel module could not be loaded properly
    """
    if W1ThermSensor.BASE_DIRECTORY.is_dir():  # pragma: no cover
        return

    # load kernel modules
    os.system("modprobe w1-gpio >/dev/null 2>&1")
    os.system("modprobe w1-therm >/dev/null 2>&1")

    for _ in range(W1ThermSensor.RETRY_ATTEMPTS):
        if W1ThermSensor.BASE_DIRECTORY.is_dir():  # pragma: no cover
            # w1 therm modules loaded correctly
            break
        time.sleep(W1ThermSensor.RETRY_DELAY_SECONDS)
    else:
        raise KernelModuleLoadError()
