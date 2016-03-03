# W1ThermSensor
[![Gitter](https://badges.gitter.im/Join Chat.svg)](https://gitter.im/timofurrer/w1thermsensor?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
> This little pure python module provides a single class to get the temperature of a w1 therm sensor<br>
> It can be easily used on are Rasperry Pi, Beagle Bone etc. over the GPIO interface.

***

[![Build Status](https://travis-ci.org/timofurrer/w1thermsensor.svg?branch=master)](https://travis-ci.org/timofurrer/w1thermsensor) [![codecov.io](http://codecov.io/github/timofurrer/w1thermsensor/coverage.svg?branch=master)](http://codecov.io/github/timofurrer/w1thermsensor?branch=master) [![Code Climate](https://codeclimate.com/github/timofurrer/w1thermsensor/badges/gpa.svg)](https://codeclimate.com/github/timofurrer/w1thermsensor)  [![Code Health](https://landscape.io/github/timofurrer/w1thermsensor/master/landscape.svg?style=flat)](https://landscape.io/github/timofurrer/w1thermsensor/master) [![PyPI version](https://badge.fury.io/py/w1thermsensor.svg)](https://badge.fury.io/py/w1thermsensor) [![PyPI](https://img.shields.io/pypi/dm/w1thermsensor.svg)]()

**Author**: Timo Furrer <tuxtimo@gmail.com><br>
**Version**: 0.3.0 <br>
**License**: MIT

## Supported devices

The following w1 therm sensor devices are supported:

* DS18S20
* DS1822
* DS18B20
* DS28EA00
* DS1825/MAX31850K

## Setup

You just need a w1 therm sensor. <br>
Some of them can be bought here: [Adafruit: DS18B20](https://www.adafruit.com/search?q=DS18B20) <br>
I've used a Raspberry Pi with an GPIO Breakout (Pi Cobbler). Other hardware like the Beagle Bone are supported, too.

## Installation

## On Raspbian

If you are using the `w1thermsensor` module on a Rasperry Pi running raspbian you can install it from the offical repository:

```bash
sudo apt-get install python-w1thermsensor
```

Or if you are using python 3:

```bash
sudo apt-get install python3-w1thermsensor
```

### Create debian packages

For python 2:

    python setup.py --command-packages=stdeb.command bdist_deb

For python 3:

    python3 setup.py --command-packages=stdeb.command bdist_deb

### From Source

    git clone https://github.com/timofurrer/w1thermsensor.git && cd w1thermsensor
    python setup.py install

*Note: maybe root privileges are required*

### From PIP

This possibility is supported on all distribution:

    pip install w1thermsensor

*Note: maybe root privileges are required*

## Usage as python package

The usage is very simple and the interface clean..
All examples are with the `DS18B20` sensor - It works the same way for the other supported devices.

### Basic usage with one sensor (implicit)

```python
from w1thermsensor import W1ThermSensor

sensor = W1ThermSensor()
temperature_in_celsius = sensor.get_temperature()
temperature_in_fahrenheit = sensor.get_temperature(W1ThermSensor.DEGREES_F)
temperature_in_all_units = sensor.get_temperatures([W1ThermSensor.DEGREES_C, W1ThermSensor.DEGREES_F, W1ThermSensor.KELVIN])
```

The need kernel modules will be automatically loaded in the constructor of the `W1ThermSensor` class. <br>
If something went wrong an exception is raised.

*The first found sensor will be taken*

### Basic usage with one sensor (explicit)

The DS18B20 sensor with the ID `00000588806a` will be taken.

```python
from w1thermsensor import W1ThermSensor

sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "00000588806a")
temperature_in_celsius = sensor.get_temperature()
```

### Multiple sensors

With the `get_available_sensors` class-method you can get the ids of all available sensors.

```python
from w1thermsensor import W1ThermSensor

for sensor in W1ThermSensor.get_available_sensors():
    print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))
```

Only sensors of a specific therm sensor type:

```python
from w1thermsensor import W1ThermSensor

for sensor in W1ThermSensor.get_available_sensors([W1ThermSensor.THERM_SENSOR_DS18B20]):
    print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))
```

## Usage as CLI tool

The w1thermsensor module can be used as CLI tool since version `0.3.0`.

### List sensors

List all available sensors:

```
$ w1thermsensor ls
$ w1thermsensor ls --json  # show results in JSON format
```

List only sensors of specific type:

```
$ w1thermsensor ls --type DS1822
$ w1thermsensor ls --type DS1822 --type MAX31850K  # specify multiple sensor types
$ w1thermsensor ls --type DS1822 --json  # show results in JSON format
```

### Show temperatures

Show temperature of all available sensors. (Some synopsis as `ls`):

```
$ w1thermsensor all --type DS1822
$ w1thermsensor all --type DS1822 --type MAX31850K  # specify multiple sensor types
$ w1thermsensor all --type DS1822 --json  # show results in JSON format
```

Show temperature of single sensor

```
$ w1thermsensor get 1  # 1 is the id obtained by the ls command
$ w1thermsensor get --hwid 00000588806a --type DS18B20
$ w1thermsensor get 1  # show results in JSON format
```

## Contribution

Feel free to contribute!
If you have made any changes and you want to make a `pull request`:

1. You are a **pro** to contribute to this repo!
2. Please make the tests pass by `make tests`
3. Now you can make the `pull request`
4. Catch my thank!
