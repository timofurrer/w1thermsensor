#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
from ds18b20 import DS18B20


def main():
    sensor = DS18B20()
    while True:
        temperatures = sensor.get_temperatures([DS18B20.DEGREES_C, DS18B20.DEGREES_F, DS18B20.KELVIN])
        print("Kelvin: %f" % temperatures[2])
        print("Degrees Celsius: %f" % temperatures[0])
        print("Degrees Fahrenheit: %f" % temperatures[1])
        print("=====================================")
        sleep(1)


if __name__ == "__main__":
    main()
