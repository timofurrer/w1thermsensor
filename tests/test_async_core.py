"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2020 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest

from w1thermsensor.async_core import AsyncW1ThermSensor
from w1thermsensor.units import Unit


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sensors, unit, expected_temperature",
    [
        (({"msb": 0x01, "lsb": 0x40, "temperature": 20.0},), Unit.DEGREES_C, 20.0,),
        (({"msb": 0xFF, "lsb": 0xF8, "temperature": -0.5},), Unit.DEGREES_C, -0.5,),
        (({"msb": 0xFC, "lsb": 0x90, "temperature": -55},), Unit.DEGREES_C, -55,),
        (({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},), "celsius", 25.0625),
        (({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},), "fahrenheit", 77.1125),
        (({"msb": 0xFC, "lsb": 0x90, "temperature": -55},), "fahrenheit", -67),
        (({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},), "kelvin", 298.2125),
        (({"msb": 0xFC, "lsb": 0x90, "temperature": -55},), "kelvin", 218.15),
    ],
    indirect=["sensors"],
)
async def test_async_get_temperature_for_different_units(
    sensors, unit, expected_temperature
):
    # given
    sensor = AsyncW1ThermSensor()
    # when
    temperature = await sensor.get_temperature(unit)
    # then
    assert temperature == pytest.approx(expected_temperature)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sensors, units, expected_temperatures",
    [
        (({"msb": 0x01, "lsb": 0x40, "temperature": 20.0},), [Unit.DEGREES_C], [20.0],),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},),
            [Unit.DEGREES_C, Unit.DEGREES_F],
            [25.0625, 77.1125],
        ),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.06251},),
            [Unit.DEGREES_F, Unit.KELVIN],
            [77.1125, 298.2125],
        ),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},),
            [Unit.DEGREES_C, Unit.DEGREES_F, Unit.KELVIN],
            [25.0625, 77.1125, 298.2125],
        ),
    ],
    indirect=["sensors"],
)
async def test_get_temperature_in_multiple_units(sensors, units, expected_temperatures):
    # given
    sensor = AsyncW1ThermSensor()
    # when
    temperatures = await sensor.get_temperatures(units)
    # then
    assert temperatures == pytest.approx(expected_temperatures)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sensors, expected_resolution",
    [
        (({"config": 0x1F},), 9),
        (({"config": 0x3F},), 10),
        (({"config": 0x5F},), 11),
        (({"config": 0x7F},), 12),
    ],
    indirect=["sensors"],
)
async def test_get_resolution(sensors, expected_resolution):
    # given
    sensor = AsyncW1ThermSensor()
    # when
    resolution = await sensor.get_resolution()
    # then
    assert resolution == pytest.approx(expected_resolution)
