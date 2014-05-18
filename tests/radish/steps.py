# -*- coding: utf-8 -*-

from radish import step, world
from math import fabs

__TEMPERATURE_HYSTERESIS__ = 0.01

def get_sensor(sensor_id):
    if 0 < int(sensor_id, 16) <= 3:
        return world.sensors[int(sensor_id) - 1]
    return [x for x in world.sensors if x.get_id() == sensor_id][0]

@step(u'the temperature for sensor ([a-f0-9]+) is (\d+(?:\.\d+)?) (C|F|K)')
def set_temperature(step, sensor_id, temperature, unit):
    sensor = get_sensor(sensor_id)
    assert world.set_temperature_on_sensor(sensor.get_id(), float(temperature)), "Cannot set temperature on sensor %s" % sensor_id


@step(u'the temperature for sensor ([a-f0-9]+) is increased by (\d+(?:\.\d+)?) (C|F|K)')
def increase_temperature(step, sensor_id, temperature_delta, unit):
    sensor = get_sensor(sensor_id)
    assert world.set_temperature_on_sensor(sensor.get_id(), sensor.get_temperature() + float(temperature_delta)), "Cannot increase temperature on sensor %s" % sensor_id


@step(u'I expect the temperature for sensor ([a-f0-9]+) to return (\d+(?:\.\d+)?) (C|F|K)')
def expect_temperature(step, sensor_id, temperature, unit):
    sensor = get_sensor(sensor_id)
    actual_temperature = sensor.get_temperature(world.units[unit])
    assert fabs(actual_temperature - float(temperature)) <= __TEMPERATURE_HYSTERESIS__, "Actual temperature: %f, Expected temperature: %f" % (actual_temperature, float(temperature))
