# -*- coding: utf-8 -*-

from sure import expect
import nose.tools as nose

import random
from os import path, makedirs
from shutil import rmtree
from glob import glob

from w1thermsensor import W1ThermSensor

MOCKED_SENSORS_DIR = "test/mockedsensors"
W1_FILE = """9e 01 4b 46 7f ff 02 10 56 : crc=56 YES
9e 01 4b 46 7f ff 02 10 56 t=%d
"""
W1_FILE_NOT_READY = """9e 01 4b 46 7f ff 02 10 56 : crc=56 NO
9e 01 4b 46 7f ff 02 10 56 t=%d
"""

RANDOM_SENSOR_ID = lambda: "".join(random.choice("0123456789abcdef") for i in range(12))

# create mocked sensors directory
if path.exists(MOCKED_SENSORS_DIR):
    rmtree(MOCKED_SENSORS_DIR)
makedirs(MOCKED_SENSORS_DIR)

# set base directory for sensors
W1ThermSensor.BASE_DIRECTORY = MOCKED_SENSORS_DIR

# disable kernel module loading
W1ThermSensor.LOAD_KERNEL_MODULES = False


def _create_w1_therm_sensor(sensor_type, sensor_id=None, temperature=20, w1_file=W1_FILE):
    """
        Creates a new mocked w1 therm sensor.
    """
    if not sensor_id:
        sensor_id = RANDOM_SENSOR_ID()

    sensor_path = path.join(MOCKED_SENSORS_DIR, "%s-%s" % (hex(sensor_type)[2:], sensor_id))
    if path.exists(sensor_path):
        print("Sensor already exists")
        return sensor_id

    makedirs(sensor_path)

    data = w1_file % (temperature * 1000)
    with open(path.join(sensor_path, W1ThermSensor.SLAVE_FILE), "w+") as f:
        f.write(data)
        return sensor_id


def _remove_w1_therm_sensors():
    for d in glob(path.join(MOCKED_SENSORS_DIR, "*")):
        rmtree(d)


def test_get_available_sensors_no_sensors():
    _remove_w1_therm_sensors()

    sensors = W1ThermSensor.get_available_sensors()
    sensors.should.be.empty


def test_get_available_sensors():
    _remove_w1_therm_sensors()

    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensors = W1ThermSensor.get_available_sensors()
    sensors.should.have.length_of(1)
    sensors[0].type.should.be.equal(W1ThermSensor.THERM_SENSOR_DS18B20)

    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS1822)
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18S20)

    sensors = W1ThermSensor.get_available_sensors()
    sensors.should.have.length_of(3)
    W1ThermSensor.THERM_SENSOR_DS1822.should.be.within(s.type for s in sensors)
    W1ThermSensor.THERM_SENSOR_DS18S20.should.be.within(s.type for s in sensors)
    W1ThermSensor.THERM_SENSOR_DS18B20.should.be.within(s.type for s in sensors)


def test_get_available_ds18s20_sensors():
    _remove_w1_therm_sensors()

    # create 3 DS18S20 sensors
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18S20)
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18S20)
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18S20)

    sensors = W1ThermSensor.get_available_sensors([W1ThermSensor.THERM_SENSOR_DS18S20])
    sensors.should.have.length_of(3)

    # create 2 DS18B20 sensors
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensors = W1ThermSensor.get_available_sensors([W1ThermSensor.THERM_SENSOR_DS18S20])
    sensors.should.have.length_of(3)


def test_get_available_ds1822_sensors():
    _remove_w1_therm_sensors()

    # create 3 DS1822 sensors
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS1822)
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS1822)
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS1822)

    sensors = W1ThermSensor.get_available_sensors([W1ThermSensor.THERM_SENSOR_DS1822])
    sensors.should.have.length_of(3)

    # create 2 DS18B20 sensors
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensors = W1ThermSensor.get_available_sensors([W1ThermSensor.THERM_SENSOR_DS1822])
    sensors.should.have.length_of(3)


def test_get_available_ds18b20_sensors():
    _remove_w1_therm_sensors()

    # create 3 DS18B20 sensors
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensors = W1ThermSensor.get_available_sensors([W1ThermSensor.THERM_SENSOR_DS18B20])
    sensors.should.have.length_of(3)

    # create 2 DS18S20 sensors
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18S20)
    _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18S20)

    sensors = W1ThermSensor.get_available_sensors([W1ThermSensor.THERM_SENSOR_DS18B20])
    sensors.should.have.length_of(3)


def test_init_first_sensor():
    _remove_w1_therm_sensors()

    # create DS18B20 sensor
    sensor_id = _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensor = W1ThermSensor()
    sensor.should.be.a(W1ThermSensor)
    sensor.type.should.be.equal(W1ThermSensor.THERM_SENSOR_DS18B20)
    sensor.id.should.be.equal(sensor_id)


def test_init_first_sensor_of_specific_type():
    _remove_w1_therm_sensors()

    # create DS18B20 sensor
    sensor_id = _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    sensor.should.be.a(W1ThermSensor)
    sensor.type.should.be.equal(W1ThermSensor.THERM_SENSOR_DS18B20)
    sensor.id.should.be.equal(sensor_id)


def test_init_specific_sensor():
    _remove_w1_therm_sensors()

    # create DS18B20 sensor
    sensor_id = _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    sensor.should.be.a(W1ThermSensor)
    sensor.type.should.be.equal(W1ThermSensor.THERM_SENSOR_DS18B20)
    sensor.id.should.be.equal(sensor_id)


def test_sensor_temperature_in_C():
    _remove_w1_therm_sensors()

    # create DS18B20 sensor with 20 C degrees
    sensor_id = _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20, temperature=20)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    sensor.id.should.be.equal(sensor_id)
    sensor.get_temperature(W1ThermSensor.DEGREES_C).should.be.equal(20)

    # FIXME: sure should support float comparisation
    # create DS18B20 sensor with 26.55 C degrees
    #sensor_id = _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20, temperature=26.55)

    #sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    #sensor.id.should.be.equal(sensor_id)
    #sensor.get_temperature(W1ThermSensor.DEGREES_C).should.be.equal(26.55)



def test_sensor_temperature_in_F():
    _remove_w1_therm_sensors()

    # 20 C = 68 F
    # 26.55 C = 79.79 F

    # create DS18B20 sensor with 20 C degrees
    sensor_id = _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20, temperature=20)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    sensor.id.should.be.equal(sensor_id)
    sensor.get_temperature(W1ThermSensor.DEGREES_F).should.be.equal(68)

    # FIXME: sure should support float comparisation
    # create DS18B20 sensor with 26.55 C degrees
    #sensor_id = _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20, temperature=26.55)

    #sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    #sensor.id.should.be.equal(sensor_id)
    #sensor.get_temperature(W1ThermSensor.DEGREES_F).should.be.equal(79.79)



def test_sensor_temperature_in_K():
    _remove_w1_therm_sensors()

    # 20 C = 293.15 K
    # 26.55 C = 299.7 K

    # create DS18B20 sensor with 20 C degrees
    sensor_id = _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20, temperature=20)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    sensor.id.should.be.equal(sensor_id)
    sensor.get_temperature(W1ThermSensor.KELVIN).should.be.equal(293.15)

    # FIXME: sure should support float comparisation
    # create DS18B20 sensor with 26.55 C degrees
    sensor_id = _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20, temperature=26.55)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    sensor.id.should.be.equal(sensor_id)
    sensor.get_temperature(W1ThermSensor.KELVIN).should.be.equal(299.7)


def test_sensor_all_temperature_units():
    _remove_w1_therm_sensors()

    # create DS18B20 sensor with 20 C degrees
    sensor_id = _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20, temperature=20)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    sensor.id.should.be.equal(sensor_id)
    sensor.get_temperatures([W1ThermSensor.DEGREES_C, W1ThermSensor.DEGREES_F, W1ThermSensor.KELVIN]).should.be.equal([20, 68, 293.15])


def test_sensor_type_name():
    _remove_w1_therm_sensors()

    # create sensors of all types
    ds18s20_sensor_id = _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18S20)
    ds1822_sensor_id = _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS1822)
    ds18b20_sensor_id = _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18S20, ds18s20_sensor_id)
    sensor.type_name.should.be.equal("DS18S20")

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS1822, ds1822_sensor_id)
    sensor.type_name.should.be.equal("DS1822")

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, ds18b20_sensor_id)
    sensor.type_name.should.be.equal("DS18B20")


def test_no_sensor_found_error():
    _remove_w1_therm_sensors()

    W1ThermSensor.when.called_with().should.throw(W1ThermSensor.NoSensorFoundError, "No Unknown temperature sensor with id '' found")
    W1ThermSensor.when.called_with(W1ThermSensor.THERM_SENSOR_DS1822).should.throw(W1ThermSensor.NoSensorFoundError, "No DS1822 temperature sensor with id '' found")

    sensor_id = RANDOM_SENSOR_ID()
    W1ThermSensor.when.called_with(W1ThermSensor.THERM_SENSOR_DS1822, sensor_id).should.throw(W1ThermSensor.NoSensorFoundError, "No DS1822 temperature sensor with id '%s' found" % sensor_id)


def test_sensor_not_ready_error():
    _remove_w1_therm_sensors()

    sensor_id = _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS1822, w1_file=W1_FILE_NOT_READY)
    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS1822, sensor_id)
    sensor.get_temperature.when.called_with(W1ThermSensor.DEGREES_C).should.throw(W1ThermSensor.SensorNotReadyError, "Sensor is not yet ready to read temperature")


def test_unsupported_unit_error():
    _remove_w1_therm_sensors()

    unsupported_unit = 0xFF
    sensor_id = _create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS1822)
    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS1822, sensor_id)
    sensor.get_temperature.when.called_with(unsupported_unit).should.throw(W1ThermSensor.UnsupportedUnitError, "Only Degress C, F and Kelvin are currently supported")
