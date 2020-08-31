"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2020 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from typing import Iterable, List

from w1thermsensor.core import W1ThermSensor, evaluate_resolution, evaluate_temperature
from w1thermsensor.errors import NoSensorFoundError, SensorNotReadyError, W1ThermSensorError
from w1thermsensor.units import Unit


class AsyncW1ThermSensor(W1ThermSensor):
    """
    Represents a w1 therm sensor connected to the device accessed by
    the Linux w1 therm sensor kernel modules.

    The ``AsyncW1ThermSensor`` provides an interface suitable
    for use with Python's ``asyncio`` module.

    The following methods are implemented as coroutines:
    * ``get_temperature()``
    * ``get_temperatures()``
    * ``get_resolution()``

    See ``W1ThermSensor`` for full reference.
    """

    def __init__(self, *args, **kwargs):  # pragma: no cover
        try:
            import aiofiles  # noqa
        except ImportError:
            raise W1ThermSensorError(
                "Install the async extras to add support for AsyncW1ThermSensor: "
                "pip install w1thermsensor[async]"
            )

        super().__init__(*args, **kwargs)

    async def get_raw_sensor_strings(self) -> List[str]:  # type: ignore
        """Reads the raw strings from the kernel module sysfs interface

        :returns: raw strings containing all bytes from the sensor memory
        :rtype: str

        :raises NoSensorFoundError: if the sensor could not be found
        :raises SensorNotReadyError: if the sensor is not ready yet
        """
        try:
            import aiofiles

            async with aiofiles.open(str(self.sensorpath), mode="r") as f:
                data = await f.readlines()
        except IOError:  # pragma: no cover
            raise NoSensorFoundError(
                "Could not find sensor of type {} with id {}".format(self.name, self.id)
            )

        if (
            len(data) < 1
            or data[0].strip()[-3:] != "YES"
            or "00 00 00 00 00 00 00 00 00" in data[0]
        ):  # pragma: no cover
            raise SensorNotReadyError(self)

        return data

    async def get_temperature(self, unit: Unit = Unit.DEGREES_C) -> float:  # type: ignore
        """Returns the temperature in the specified unit

        :param int unit: the unit of the temperature requested

        :returns: the temperature in the given unit
        :rtype: float

        :raises UnsupportedUnitError: if the unit is not supported
        :raises NoSensorFoundError: if the sensor could not be found
        :raises SensorNotReadyError: if the sensor is not ready yet
        :raises ResetValueError: if the sensor has still the initial value and no measurment
        """
        raw_temperature_line = (await self.get_raw_sensor_strings())[1]
        return evaluate_temperature(
            raw_temperature_line,
            self.RAW_VALUE_TO_DEGREE_CELSIUS_FACTOR,
            unit,
            self.type,
            self.id,
            self.offset,
            self.SENSOR_RESET_VALUE,
        )

    async def get_temperatures(self, units: Iterable[Unit]) -> List[float]:  # type: ignore
        """Returns the temperatures in the specified units

        :param list units: the units for the sensor temperature

        :returns: the sensor temperature in the given units. The order of
        the temperatures matches the order of the given units.
        :rtype: list

        :raises UnsupportedUnitError: if the unit is not supported
        :raises NoSensorFoundError: if the sensor could not be found
        :raises SensorNotReadyError: if the sensor is not ready yet
        """
        sensor_value = await self.get_temperature(Unit.DEGREES_C)
        return [
            Unit.get_conversion_function(Unit.DEGREES_C, unit)(sensor_value)
            for unit in units
        ]

    async def get_resolution(self) -> int:  # type: ignore
        """Get the current resolution from the sensor.

        :returns: sensor resolution from 9-12 bits
        :rtype: int
        """
        raw_temperature_line = (await self.get_raw_sensor_strings())[1]
        return evaluate_resolution(raw_temperature_line)
