"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2020 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from enum import Enum
from typing import Callable

from w1thermsensor.errors import UnsupportedUnitError


class Unit(Enum):
    DEGREES_C = "celsius"
    DEGREES_F = "fahrenheit"
    KELVIN = "kelvin"

    @classmethod
    def get_conversion_function(
        cls, unit_from: "Unit", unit_to: "Unit"
    ) -> Callable[[float], float]:
        """Returns the unit factor depending on the 'from' and 'to' unit constants

        :param int unit_from: the unit to convert from
        :param int unit_to: the unit to convert into

        :returns: a function to convert temperatures from one unit to another
        :rtype: lambda function

        :raises UnsupportedUnitError: if the unit pair is not supported
        """
        try:
            if isinstance(unit_from, str):
                unit_from = cls(unit_from)
            if isinstance(unit_to, str):
                unit_to = cls(unit_to)

            return UNIT_FACTORS[(unit_from, unit_to)]
        except KeyError:
            raise UnsupportedUnitError()


#: Holds conversion functions for all units
UNIT_FACTORS = {
    # identity functions
    (Unit.DEGREES_C, Unit.DEGREES_C): lambda x: x,
    (Unit.DEGREES_F, Unit.DEGREES_F): lambda x: x,
    (Unit.KELVIN, Unit.KELVIN): lambda x: x,
    # Celsius to X
    (Unit.DEGREES_C, Unit.DEGREES_F): lambda x: x * 1.8 + 32.0,
    (Unit.DEGREES_C, Unit.KELVIN): lambda x: x + 273.15,
    # Fahrenheit to X
    (Unit.DEGREES_F, Unit.DEGREES_C): lambda x: (x - 32) * (5.0 / 9.0),
    (Unit.DEGREES_F, Unit.KELVIN): lambda x: ((x - 32) * (5.0 / 9.0)) + 273.15,
    # Kelvin to X
    (Unit.KELVIN, Unit.DEGREES_C): lambda x: x - 273.15,
    (Unit.KELVIN, Unit.DEGREES_F): lambda x: (x - 273.15) * 1.8 + 32,
}
