"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2020 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import os
import time

import pytest

from w1thermsensor.errors import KernelModuleLoadError
from w1thermsensor.kernel import load_kernel_modules


def test_kernel_module_load_error(monkeypatch):
    """Test exception if kernel modules cannot be loaded"""
    # given
    monkeypatch.setattr(os, "system", lambda x: True)
    monkeypatch.setattr(os.path, "isdir", lambda x: False)
    monkeypatch.setattr(time, "sleep", lambda x: True)
    expected_error_msg = "Cannot load w1 therm kernel modules"

    # when & then
    with pytest.raises(KernelModuleLoadError, match=expected_error_msg):
        load_kernel_modules()
