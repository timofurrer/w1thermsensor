# DS18B20
> This little pure python module provides a single class to get the temperature of a DS18B20 sensor<br>
> It can be easily used on are Rasperry Pi over the GPIO interface.

***

*Author*: Timo Furrer <tuxtimo@gmail.com><br>
*Version*: 0.00.01

## Setup

You just need a DS18B20 temperature sensor. <br>
Some of them can be bought here: [Adafruit: DS18B20](https://www.adafruit.com/search?q=DS18B20) <br>
I've used a Raspberry Pi with an GPIO Breakout (Pi Cobbler)

## Installation

### From Source

    python setup.py install

*Note: maybe root privileges are required*

### From PIP

    pip install ds18b20

*Note: maybe root privileges are required*

## Sample program

There is a little sample program in the `tests` directory.
Just execute it and you will get the temperatures in Kelvin, Degrees Celcius and Degrees Fahrenheit.

      $ python example.py
      Kelvin: 295.275000
      Degress Celcius: 23.125000
      Degress Fahrenheit: 73.625000
      =====================================
      Kelvin: 296.025000
      Degress Celcius: 23.875000
      Degress Fahrenheit: 74.975000
      =====================================
      ...
