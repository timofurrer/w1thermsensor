"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2020 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from enum import IntEnum


class Sensor(IntEnum):
    #: Holds information about supported w1therm sensors
    DS18S20 = 0x10
    DS1822 = 0x22
    DS18B20 = 0x28
    DS28EA00 = 0x42
    DS1825 = 0x3B
    MAX31850K = 0x3B

    def comply_12bit_standard(self) -> bool:
        return self in {
            Sensor.DS1822,
            Sensor.DS18B20,
            Sensor.DS1825,
            Sensor.DS28EA00,
        }

    @classmethod
    def from_id_string(cls, id_string: str) -> "Sensor":
        return Sensor(int(id_string, 16))
