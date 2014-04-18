#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep

from temperaturesensor import TemperatureSensor


def main():
    ts = TemperatureSensor()
    while True:
        temperatures = ts.get_temperatures([TemperatureSensor.DEGREES_C, TemperatureSensor.DEGREES_F, TemperatureSensor.KELVIN])
        print("Kelvin: %f" % temperatures[2])
        print("Degress Celcius: %f" % temperatures[0])
        print("Degress Fahrenheit: %f" % temperatures[1])
        print("=====================================")
        sleep(1)


if __name__ == "__main__":
    main()
