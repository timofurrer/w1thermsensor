# DS18B20
> This little pure python module provides a single class to get the temperature of a DS18B20 sensor<br>
> It can be easily used on a Rasperry Pi over the GPIO interface.

***

*Author*: Timo Furrer <tuxtimo@gmail.com><br>
*Version*: 0.01.03

## Setup

You just need a DS18B20 temperature sensor. <br>
Some of them can be bought here: [Adafruit: DS18B20](https://www.adafruit.com/search?q=DS18B20) <br>
I've used a Raspberry Pi with an GPIO Breakout (Pi Cobbler)

## Installation

### From Source

    git clone https://github.com/timofurrer/ds18b20.git && cd ds18b20
    pip install .

*Note: maybe root privileges are required*

### From PIP

    pip install ds18b20

*Note: maybe root privileges are required*

## Usage

The usage is very simple and the interface clean..

### Basic usage with one sensor (implicit)

```python
from ds18b20 import DS18B20

sensor = DS18B20()
temperature_in_celsius = sensor.get_temperature()
temperature_in_fahrenheit = sensor.get_temperature(DS18B20.DEGREES_F)
temperature_in_all_units = sensor.get_temperatures([DS18B20.DEGREES_C, DS18B20.DEGREES_F, DS18B20.KELVIN])
```

The need kernel modules will be automatically loaded in the constructor of the `DS18B20` class. <br>
If something went wrong an exception is raised.

*The first found sensor will be taken*

### Basic usage with one sensor (explicit)

The sensor with the ID `00000588806a` will be taken.

```python
from ds18b20 import DS18B20

sensor = DS18B20("00000588806a")
temperature_in_celsius = sensor.get_temperature()
```

### Multiple sensors

With the `get_available_sensors` class-method you can get the ids of all available sensors.

```python
from ds18b20 import DS18B20

sensors = []
for sensor_id in DS18B20.get_available_sensors():
    sensors.append(DS18B20(sensor_id))

for sensor in sensors:
    print("Sensor %s has temperature %.2f" % (sensor.get_id(), sensor.get_temperature()))
```

The first path of the above code can be replaced by the `get_all_sensors` method:

```python
from ds18b20 import DS18B20

sensors = DS18B20.get_all_sensors()
...
```

## Sample program

There is a little sample program in the `tests` directory.
Just execute it and you will get the temperatures in Kelvin, Degrees Celsius and Degrees Fahrenheit.

      $ python example.py
      Kelvin: 295.275000
      Degrees Celsius: 23.125000
      Degrees Fahrenheit: 73.625000
      =====================================
      Kelvin: 296.025000
      Degrees Celsius: 23.875000
      Degrees Fahrenheit: 74.975000
      =====================================
      ...

## Contribution

Feel free to contribute!
If you have made any changes and you want to make a `pull request`:

1. You are a **pro** to contribute to this repo!
2. Please make the tests pass by `make test`
3. Now you can make the `pull request`
4. Catch my thank!
