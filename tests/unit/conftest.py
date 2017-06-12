# -*- coding: utf-8 -*-

"""
pytest fixtures and helpers
"""

import random

import pytest

from w1thermsensor import W1ThermSensor

#: Holds sample contents for a ready and not ready sensor
W1_FILE = """9e 01 4b 46 7f ff 02 10 56 : crc=56 {ready}
9e 01 4b 46 7f ff 02 10 56 t={temperature}
"""


def get_random_sensor_id():
    """
    Return a valid random sensor id
    """
    return ''.join(random.choice('0123456789abcdef') for i in range(12))


@pytest.fixture(scope='function')
def kernel_module_dir(tmpdir):
    """
    Fixture to mock the w1 therm kernel module
    file structure
    """
    # save original base dir
    original_base_dir = W1ThermSensor.BASE_DIRECTORY
    # create temporary base dir
    devices_path = tmpdir.mkdir('devices')
    W1ThermSensor.BASE_DIRECTORY = str(devices_path)
    yield devices_path
    # restore original base dir
    W1ThermSensor.BASE_DIRECTORY = original_base_dir


@pytest.fixture(scope='function')
def sensors(request, kernel_module_dir):  # pylint: disable=redefined-outer-name
    """
    Fixture which returns a valid sensor object
    with the given settings in ``request.param``
    """
    sensors_ = []
    if hasattr(request, 'param'):
        for sensor_conf in request.param:
            sensor_type = sensor_conf.get('type', W1ThermSensor.THERM_SENSOR_DS18B20)
            sensor_id = sensor_conf.get('id') or get_random_sensor_id()
            sensor_temperature = sensor_conf.get('temperature', 20)
            sensor_ready = sensor_conf.get('ready', True)

            sensor_dir = kernel_module_dir.mkdir('{0}-{1}'.format(hex(sensor_type)[2:], sensor_id))

            sensor_file = sensor_dir.join(W1ThermSensor.SLAVE_FILE)
            sensor_file_content = W1_FILE.format(
                temperature=sensor_temperature * 1000.0, ready='YES' if sensor_ready else 'NO')
            sensor_file.write(sensor_file_content)

            sensors_.append({
                'type': sensor_type, 'id': sensor_id,
                'temperature': sensor_temperature
            })

    return sensors_
