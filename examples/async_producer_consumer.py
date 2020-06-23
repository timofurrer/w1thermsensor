"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2020 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

# NOTE(TF):
# This examples uses async producers which read
# temperature from sensors and an async consumer
# which consumes all the read temperature and does
# something with it.

import asyncio
import time
from dataclasses import dataclass

from w1thermsensor import AsyncW1ThermSensor


@dataclass
class Reading:
    sensor_id: str
    timestamp: float
    temperature: float


async def produce_readings(sensor: AsyncW1ThermSensor, queue: asyncio.Queue):
    """Single async producer which reads a temperature from a single sensor"""
    while True:
        timestamp = time.time_ns() / 1e9
        temperature = await sensor.get_temperature()
        await queue.put(Reading(sensor.id, timestamp, temperature))


async def consumer(queue):
    while True:
        reading = await queue.get()

        # do something very fancy with the reading ...
        print(reading)

        queue.task_done()


def main():
    # create queue to share readings between producers and consumer
    queue = asyncio.Queue()
    # create an async producer for each available sensor
    producers = [
        produce_readings(sensor, queue)
        for sensor in AsyncW1ThermSensor.get_available_sensors()
    ]
    print(f"Created {len(producers)} producers ...")

    # create threaded consumer
    consumers = [consumer(queue)]

    tasks = producers + consumers

    loop = asyncio.get_event_loop()
    try:
        for task in tasks:
            asyncio.ensure_future(task)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


if __name__ == "__main__":
    main()
