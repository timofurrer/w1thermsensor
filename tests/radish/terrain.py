# -*- coding: utf-8-*-

from os import path, remove
from sys import path as syspath
from glob import glob

syspath.insert(0, path.join(path.dirname(path.abspath(__file__)), "../../"))

from radish import before, after, world, Step
from ds18b20 import DS18B20

world.MOCKED_SENSORS_DIR = "tests/mockedsensors"
world.units = {"C": DS18B20.DEGREES_C, "F": DS18B20.DEGREES_F, "K": DS18B20.KELVIN}

__TEMPERATURE_SENSOR_FORMAT__ = """9e 01 4b 46 7f ff 02 10 56 : crc=56 YES
9e 01 4b 46 7f ff 02 10 56 t=%d
"""

@before.all
def before_all():
    # mock sensors
    DS18B20.BASE_DIRECTORY = world.MOCKED_SENSORS_DIR

    sensors = []
    sensor_ids = DS18B20.get_available_sensors()
    for sensor_id in sensor_ids:
        sensors.append(DS18B20(sensor_id, load_kernel_modules=False))
    world.sensors = sensors


@after.all
def after_all(endresult):
    slaves = glob(path.join(world.MOCKED_SENSORS_DIR, DS18B20.SLAVE_PREFIX + "*", DS18B20.SLAVE_FILE))
    for slave in slaves:
        remove(slave)

def set_temperature_on_sensor(sensor_id, temperature):
    """Sets the temperature (in celsius) on a mocked sensor"""
    sensor_path = path.join(world.MOCKED_SENSORS_DIR, DS18B20.SLAVE_PREFIX + sensor_id)
    if not path.exists(sensor_path):
        raise Step.ValidationError("No mocked sensor with id %s found" % sensor_id)

    data = __TEMPERATURE_SENSOR_FORMAT__ % (temperature * 1000)
    with open(path.join(sensor_path, DS18B20.SLAVE_FILE), "w+") as f:
        f.write(data)

    return True

world.set_temperature_on_sensor = set_temperature_on_sensor
