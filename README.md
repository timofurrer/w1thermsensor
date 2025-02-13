# W1ThermSensor

[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/timofurrer/w1thermsensor?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
> Get the temperature from your w1 therm sensor in a single line of code!<br>
> It's designed to be used with the Rasperry Pi hardware but also works on a Beagle Bone and others.

***

![CI](https://github.com/timofurrer/w1thermsensor/workflows/CI/badge.svg)
[![PyPI version](https://badge.fury.io/py/w1thermsensor.svg)](https://badge.fury.io/py/w1thermsensor)
[![codecov.io](http://codecov.io/github/timofurrer/w1thermsensor/coverage.svg?branch=master)](http://codecov.io/github/timofurrer/w1thermsensor?branch=master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

**Raspberry Pi:** this package is available in Raspbian as `python-w1thermsensor` and `python3-w1thermsensor`.

**Python 2 drop**: all w1thermsensor releases from 2.0 are Python 3.5+

## Supported devices

The following w1 therm sensor devices are supported:

* DS18S20
* DS1822
* DS18B20
* DS28EA00
* DS1825/MAX31850K

## Setup

The following hardware is needed:

* w1 therm compatible sensor (some of them can be bought here: [Adafruit: DS18B20](https://www.adafruit.com/search?q=DS18B20))
* wires to connect the sensor to your board (you might need a breadboard, too)
* a board like the Raspberry Pi or the Beagle Bone

On the Raspberry Pi, you will need to add `dtoverlay=w1-gpio` (for regular connection) or `dtoverlay=w1-gpio,pullup="y"` (for parasitic connection) to your /boot/config.txt. The default data pin is GPIO4 (RaspPi connector pin 7), but that can be changed from 4 to `x` with `dtoverlay=w1-gpio,gpiopin=x`.

After that, don't forget to reboot.

### Hardware-connection


    Raspi VCC (3V3) Pin 1 -----------------------------   VCC    DS18B20
                                                   |
                                                   |
                                                   R1 = 4k7 ...10k
                                                   |
                                                   |
    Raspi GPIO 4    Pin 7 -----------------------------   Data   DS18B20
           (BCM)    (BOARD)

    Raspi GND       Pin 6 -----------------------------   GND    DS18B20

### Soft-pull-up

Alternatively to the hardware pull-up made by a physical resistor, or to the above mentioned software configuration `dtoverlay=w1-gpio,pullup="y"` in /boot/config.txt, the following soft pull-up can be used:

```python
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
```

When using this software pull-up, 1-Wire devices will be visible to the kernel only while the program pulls the GPIO pin up.

### Hw device connection verification

Run the following command:

```bash
ls -l /sys/bus/w1/devices
```

You should check the availability of one or more filenames starting with "28-".

Filenames starting with "00-" possibly mean that the pull-up resistor is missing.

1-Wire devices can be plugged in dynamically and are visible to the kernel driver just after their hw connection.

To test reading the temperature, issue the following command:

```bash
for i in /sys/bus/w1/devices/28-*; do cat $i/w1_slave; done
```

## Installation

### From PIP

This possibility is supported on all distributions:

    pip install w1thermsensor

*Note: maybe root privileges are required*

Use the `async` extra to add support for asyncio and `AsyncW1ThermSensor`:

    pip install w1thermsensor[async]

### On Raspbian using `apt-get`

If you are using the `w1thermsensor` module on a Rasperry Pi running Raspbian you can install it from the official repository:

```bash
sudo apt-get install python3-w1thermsensor
```

**Note:** For older versions of this package you might get the following error: `ImportError: No module named 'pkg_resources'` which indicates that you need to install `python-setuptools` or `python3-setuptools` respectively.

### Manually build and install the debian package

    debuild -us -uc
    dpkg -i ../python3-w1thermsensor_*.deb

## Usage as python package

The usage is very simple and the interface clean..
All examples are with the `DS18B20` sensor - It works the same way for the other supported devices.

### Basic usage with one sensor (implicit)

```python
from w1thermsensor import W1ThermSensor, Unit

sensor = W1ThermSensor()
temperature_in_celsius = sensor.get_temperature()
temperature_in_fahrenheit = sensor.get_temperature(Unit.DEGREES_F)
temperature_in_all_units = sensor.get_temperatures([
    Unit.DEGREES_C,
    Unit.DEGREES_F,
    Unit.KELVIN])
```

The need kernel modules will be automatically loaded in the constructor of the `W1ThermSensor` class. <br>
If something went wrong an exception is raised.

*The first found sensor will be taken*

### Basic usage with one sensor (explicit)

The DS18B20 sensor with the ID `00000588806a` will be taken.

```python
from w1thermsensor import W1ThermSensor, Sensor

sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id="00000588806a")
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
from w1thermsensor import W1ThermSensor, Sensor

for sensor in W1ThermSensor.get_available_sensors([Sensor.DS18B20]):
    print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))
```

### Multiple sensors using bulk conversion

Using bulk conversion method returns a list of available sensors in a bus, with property `temperature`. By default, uses temperature in Celsius, if `Unit` parameter is not specified. Otherwise, use `w1thermsensor.Unit` to convert to your desired unit.

This method speeds up the process of reading all sensors in the bus to the single sensor conversion time.

E.g. Having 3 sensors in the bus with a 12bit resolution will result in `~750ms * 3 sensors = ~2,3s` using traditional method above. With the bulk conversion it will last around `~750ms`  

*Note: Bulk conversion requires root privileges or permissions change to `w1_master*` path*

*Method do not support sensor calibration or offset configuration!*

`*w1_master` path is: 
- (symbolic link) - `/sys/bus/w1/devices/w1_bus_master1/therm_bulk_read`
- (destination link) - `/sys/devices/w1_bus_master1/therm_bulk_read`

If you don't want to run your script as a root - do `chmod +w` or `chown` to a user executing your python script to the one of the paths above.

```python
from w1thermsensor import W1ThermSensor, Unit

for sensor in W1ThermSensor.get_bulk_temperature():
            # W1ThermSensor.bulk_read(Unit.KELVIN)
            # W1ThermSensor.bulk_read(Unit.DEGREES_F)
    print(f"Sensor: {sensor.id}, temp: {sensor.temperature}")
```

### Set sensor resolution

Some w1 therm sensors support changing the resolution for the temperature reads.
`w1thermsensor` enables to do so with the `W1ThermSensor.set_resolution()` method:

```python
sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id="00000588806a")
sensor.set_resolution(9)
```

If the ``persist`` argument is set to ``False`` this value
is "only" stored in the volatile SRAM, so it is reset when
the sensor gets power-cycled.

If the ``persist`` argument is set to ``True`` the current set
resolution is stored into the EEPROM. Since the EEPROM has a limited
amount of writes (>50k), this command should be used wisely.

```python
sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id="00000588806a")
sensor.set_resolution(9, persist=True)
```

**Note**: this is supported since Linux Kernel 4.7<br>
**Note**: this requires `root` privileges

### Disable kernel module auto loading

Upon import of the `w1thermsensor` package the `w1-therm` and `w1-gpio` kernel modules get loaded automatically.
This requires the python process to run as root. Sometimes that's not what you want, thus you can disable the auto loading
and load the kernel module yourself prior to talk to your sensors with `w1thermsensor`.

You can disable the auto loading feature by setting the `W1THERMSENSOR_NO_KERNEL_MODULE` environment variable to `1`:

```bash
# set it globally for your shell so that sub-processes will inherit it.
export W1THERMSENSOR_NO_KERNEL_MODULE=1

# set it just for your Python process
W1THERMSENSOR_NO_KERNEL_MODULE=1 python my_awesome_thermsensor_script.py
```

Every other values assigned to `W1THERMSENSOR_NO_KERNEL_MODULE` will case `w1thermsensor` to load the kernel modules.

*Note: the examples above also apply for the CLI tool usage. See below.*

### Correcting Temperatures / Sensor Calibration
Calibrating the temperature sensor relies on obtaining a measured high and measured low value that
have known reference values that can be used for correcting the sensor's readings.  The simplest
way to do this is to measure the melting point and boiling point of water since those values are
known.  This method will only work with waterproof sensors - you will need a different mechanism
for obtaining measured values if you are not using a waterproof sensor.

In order to obtain the `measured_low_point`, fill a container to 80% with ice and add water to the
ice until the ice is floating and water is at the surface.  Submerse your sensor in the ice water,
ensuring it does not touch the container.  Wait 5 minutes for the temperature to stabilize in the
container and then once the sensor readings have stabilized for approximately 30 seconds (readings
remain consistent), record the value as the `measured_low_point`

In order to obtain the `measured_high_point`, bring a pot of water to a rapid boil.  Place your
sensor in the boiling water, ensuring that it does not touch the pot.  Allow the sensor to come up
to temperature and once it has stabilized for approximately 30 seconds (readings remain
consistent), record the value as the `measured_high_point`

Generally speaking, the `reference_low_point` should be left at 0.0 unless you have some special
situation that changes the melting point of water.  Because melting does not involve a gaseous
phase change, the effects of air pressure and altitude on the melting point are minimal.

The `reference_high_point` on the other hand is greatly impacted by air pressure (and thus
altitude).  For example, the boiling point of water is 100.0C at sea level, and is approximately
72C at the summit of Mount Everest (8848m above sea level).  While air pressure is what actually
dictates boiling point, generally speaking altitude is a close enough approximation for most use
cases.  [Engineering Toolbox](https://www.engineeringtoolbox.com/boiling-points-water-altitude-d_1344.html)
has a page that gives you the boiling point of water at different altitudes.

This method is derived from [this Instructable](https://www.instructables.com/Calibration-of-DS18B20-Sensor-With-Arduino-UNO/).

```python
from w1thermsensor.calibration_data import CalibrationData
from w1thermsensor import W1ThermSensor, Unit

calibration_data = CalibrationData(
        measured_high_point=measured_high_point,
        measured_low_point=measured_low_point,
        reference_high_point=reference_high_point,
        reference_low_point=reference_low_point, # optional, defaults to 0.0
    )
sensor = W1ThermSensor(calibration_data=calibration_data)

corrected_temperature_in_celsius = sensor.get_corrected_temperature()
corrected_temperature_in_fahrenheit = sensor.get_corrected_temperature(Unit.DEGREES_F)
corrected_temperature_in_all_units = sensor.get_corrected_temperatures([
    Unit.DEGREES_C,
    Unit.DEGREES_F,
    Unit.KELVIN])
```

### Async Interface

The `w1thermsensor` package implements an async interface `AsyncW1ThermSensor` for asyncio.

The following methods are supported:

* `get_temperature()`
* `get_temperatures()`
* `get_resolution()`

For example:

```python
from w1thermsensor import AsyncW1ThermSensor, Unit

sensor = AsyncW1ThermSensor()
temperature_in_celsius = await sensor.get_temperature()
temperature_in_fahrenheit = await sensor.get_temperature(Unit.DEGREES_F)
temperature_in_all_units = await sensor.get_temperatures([
    Unit.DEGREES_C,
    Unit.DEGREES_F,
    Unit.KELVIN])
```


## Usage as CLI tool

The w1thermsensor module can be used as CLI tool since version `0.3.0`. <br>
*Please note that the CLI tool will only get installed with the Raspbian Python 3 package* (`sudo apt-get install python3-w1thermsensor`)

### List sensors

List all available sensors:

```
$ w1thermsensor ls
$ w1thermsensor ls --json  # show results in JSON format
```

List only sensors of a specific type:

```
$ w1thermsensor ls --type DS1822
$ w1thermsensor ls --type DS1822 --type MAX31850K  # specify multiple sensor types
$ w1thermsensor ls --type DS1822 --json  # show results in JSON format
```

### Show temperatures

Show temperature of all available sensors: (Same synopsis as `ls`)

```
$ w1thermsensor all --type DS1822
$ w1thermsensor all --type DS1822 --type MAX31850K  # specify multiple sensor types
$ w1thermsensor all --type DS1822 --json  # show results in JSON format
```

Show temperature of a single sensor:

```
$ w1thermsensor get 1  # 1 is the id obtained by the ls command
$ w1thermsensor get --hwid 00000588806a --type DS18B20
$ w1thermsensor get 1  # show results in JSON format
```

Show temperature of a single sensor in the given resolution

```
$ w1thermsensor get 1 --resolution 10
$ w1thermsensor get --hwid 00000588806a --type DS18B20 --resolution 11
```

### Change temperature read resolution and write to EEPROM

```
# w1thermsensor resolution 10 1
# w1thermsensor resolution --hwid 00000588806a --type DS18B20 11
```

**Note**: this requires `root` privileges

## Contribution

I'm happy about all types of contributions to this project! :beers:

***

*<p align="center">This project is published under [MIT](LICENSE).<br>A [Timo Furrer](https://tuxtimo.me) project.<br>- :tada: -</p>*
