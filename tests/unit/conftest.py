"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2020 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import random
from pathlib import Path

import pytest

from w1thermsensor import Sensor, W1ThermSensor

#: Holds sample contents for a ready and not ready sensor
W1_FILE = """{lsb:x} {msb:x} 4b 46 {config:x} ff 02 10 56 : crc=56 {ready}
{lsb:x} {msb:x} 4b 46 {config:x} ff 02 10 56 t={temperature}
"""
#: Holds sample content for a partially disconnected sensor which only repors zero bytes
W1_FILE_ZEROVALUES = """00 00 00 00 00 00 00 00 00 : crc=00 YES
00 00 00 00 00 00 00 00 00 t=0
"""


def get_random_sensor_id():
    """
    Return a valid random sensor id
    """
    return "".join(random.choice("0123456789abcdef") for i in range(12))


@pytest.fixture(scope="function")
def kernel_module_dir(tmpdir):
    """
    Fixture to mock the w1 therm kernel module
    file structure
    """
    # save original base dir
    original_base_dir = W1ThermSensor.BASE_DIRECTORY
    # create temporary base dir
    devices_path = tmpdir.mkdir("devices")
    W1ThermSensor.BASE_DIRECTORY = Path(str(devices_path))
    yield devices_path
    # restore original base dir
    W1ThermSensor.BASE_DIRECTORY = original_base_dir


@pytest.fixture(scope="function")
def sensors(request, kernel_module_dir):  # pylint: disable=redefined-outer-name
    """
    Fixture which returns a valid sensor object
    with the given settings in ``request.param``
    """
    sensors_ = []
    if hasattr(request, "param"):
        for sensor_conf in request.param:
            sensor_type = sensor_conf.get("type", Sensor.DS18B20)
            sensor_id = sensor_conf.get("id") or get_random_sensor_id()
            sensor_temperature = sensor_conf.get("temperature", 20)
            sensor_counts = int(sensor_temperature * 16.0)
            sensor_msb = sensor_conf.get("msb", sensor_counts >> 8)
            sensor_lsb = sensor_conf.get("lsb", sensor_counts & 0xFF)
            sensor_config_bit = sensor_conf.get("config", 0x7F)
            sensor_ready = sensor_conf.get("ready", True)
            sensor_zerovalues = sensor_conf.get("zero_values", False)

            sensor_dir = kernel_module_dir.mkdir(
                "{0}-{1}".format(hex(sensor_type)[2:], sensor_id)
            )

            sensor_file = sensor_dir.join(W1ThermSensor.SLAVE_FILE)
            sensor_file_content = (
                W1_FILE.format(
                    msb=sensor_msb,
                    lsb=sensor_lsb,
                    temperature=sensor_temperature * 1000.0,
                    config=sensor_config_bit,
                    ready="YES" if sensor_ready else "NO",
                )
                if not sensor_zerovalues
                else W1_FILE_ZEROVALUES
            )
            sensor_file.write(sensor_file_content)

            sensors_.append(
                {
                    "type": sensor_type,
                    "id": sensor_id,
                    "temperature": sensor_temperature,
                }
            )

    return sensors_
