"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2020 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import asyncio

from w1thermsensor import AsyncW1ThermSensor


async def main():
    # initialize sensor with first available sensor
    sensor = AsyncW1ThermSensor()

    # continuously read temperature from sensor
    while True:
        temperature = await sensor.get_temperature()
        print(f"Temperature: {temperature:.3f}")
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
