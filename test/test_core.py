# -*- coding: utf-8 -*-

import os
import shutil
import random
from functools import wraps

import sure
from mock import patch

from w1thermsensor.core import W1ThermSensor, load_kernel_modules
from w1thermsensor.errors import W1ThermSensorError, KernelModuleLoadError, NoSensorFoundError, SensorNotReadyError, UnsupportedUnitError

MOCKED_SENSORS_DIR = "test/mockedsensors"
W1_FILE = """9e 01 4b 46 7f ff 02 10 56 : crc=56 YES
9e 01 4b 46 7f ff 02 10 56 t=%d
"""
W1_FILE_NOT_READY = """9e 01 4b 46 7f ff 02 10 56 : crc=56 NO
9e 01 4b 46 7f ff 02 10 56 t=%d
"""
# set base directory for sensors, note existing DIR
# skips loading the kernel modules
W1ThermSensor.BASE_DIRECTORY = MOCKED_SENSORS_DIR

RANDOM_SENSOR_ID = lambda: "".join(random.choice("0123456789abcdef") for i in range(12))
FLOAT_EPSILON = 0.00001


def mock_kernel_modules(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # create mocked sensors directory
        if os.path.exists(MOCKED_SENSORS_DIR):
            shutil.rmtree(MOCKED_SENSORS_DIR)
        os.makedirs(MOCKED_SENSORS_DIR)
        func(*args, **kwargs)

        # remove all mocked temperature sensors
        shutil.rmtree(MOCKED_SENSORS_DIR)
    return wrapper


def create_w1_therm_sensor(sensor_type, sensor_id=None, temperature=20, w1_file=W1_FILE):
    """
        Creates a new mocked w1 therm sensor.
    """
    if not sensor_id:
        sensor_id = RANDOM_SENSOR_ID()

    sensor_path = os.path.join(MOCKED_SENSORS_DIR, "%s-%s" % (hex(sensor_type)[2:], sensor_id))
    if os.path.exists(sensor_path):
        print("Sensor already exists")
        return sensor_id

    os.makedirs(sensor_path)

    data = w1_file % (temperature * 1000)
    with open(os.path.join(sensor_path, W1ThermSensor.SLAVE_FILE), "w+") as f:
        f.write(data)
        return sensor_id


@mock_kernel_modules
def test_get_available_sensors_no_sensors():
    sensors = W1ThermSensor.get_available_sensors()
    sensors.should.be.empty


@mock_kernel_modules
def test_get_available_sensors():
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensors = W1ThermSensor.get_available_sensors()
    sensors.should.have.length_of(1)
    sensors[0].type.should.be.equal(W1ThermSensor.THERM_SENSOR_DS18B20)

    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS1822)
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18S20)

    sensors = W1ThermSensor.get_available_sensors()
    sensors.should.have.length_of(3)
    W1ThermSensor.THERM_SENSOR_DS1822.should.be.within(s.type for s in sensors)
    W1ThermSensor.THERM_SENSOR_DS18S20.should.be.within(s.type for s in sensors)
    W1ThermSensor.THERM_SENSOR_DS18B20.should.be.within(s.type for s in sensors)


@mock_kernel_modules
def test_get_available_ds18s20_sensors():
    # create 3 DS18S20 sensors
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18S20)
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18S20)
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18S20)

    sensors = W1ThermSensor.get_available_sensors([W1ThermSensor.THERM_SENSOR_DS18S20])
    sensors.should.have.length_of(3)

    # create 2 DS18B20 sensors
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensors = W1ThermSensor.get_available_sensors([W1ThermSensor.THERM_SENSOR_DS18S20])
    sensors.should.have.length_of(3)


@mock_kernel_modules
def test_get_available_ds1822_sensors():
    # create 3 DS1822 sensors
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS1822)
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS1822)
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS1822)

    sensors = W1ThermSensor.get_available_sensors([W1ThermSensor.THERM_SENSOR_DS1822])
    sensors.should.have.length_of(3)

    # create 2 DS18B20 sensors
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensors = W1ThermSensor.get_available_sensors([W1ThermSensor.THERM_SENSOR_DS1822])
    sensors.should.have.length_of(3)


@mock_kernel_modules
def test_get_available_ds18b20_sensors():
    # create 3 DS18B20 sensors
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensors = W1ThermSensor.get_available_sensors([W1ThermSensor.THERM_SENSOR_DS18B20])
    sensors.should.have.length_of(3)

    # create 2 DS18S20 sensors
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18S20)
    create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18S20)

    sensors = W1ThermSensor.get_available_sensors([W1ThermSensor.THERM_SENSOR_DS18B20])
    sensors.should.have.length_of(3)


@mock_kernel_modules
def test_init_first_sensor():
    # create DS18B20 sensor
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensor = W1ThermSensor()
    sensor.should.be.a(W1ThermSensor)
    sensor.type.should.be.equal(W1ThermSensor.THERM_SENSOR_DS18B20)
    sensor.id.should.be.equal(sensor_id)


@mock_kernel_modules
def test_init_first_sensor_of_specific_type():
    # create DS18B20 sensor
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    sensor.should.be.a(W1ThermSensor)
    sensor.type.should.be.equal(W1ThermSensor.THERM_SENSOR_DS18B20)
    sensor.id.should.be.equal(sensor_id)


@mock_kernel_modules
def test_init_specific_sensor():
    # create DS18B20 sensor
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    sensor.should.be.a(W1ThermSensor)
    sensor.type.should.be.equal(W1ThermSensor.THERM_SENSOR_DS18B20)
    sensor.id.should.be.equal(sensor_id)


@mock_kernel_modules
def test_sensor_temperature_in_C():
    # create DS18B20 sensor with 20 C degrees
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20, temperature=20)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    sensor.id.should.be.equal(sensor_id)
    sensor.get_temperature(W1ThermSensor.DEGREES_C).should.be.equal(20.0)

    # create DS18B20 sensor with 26.55 C degrees
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20, temperature=26.55)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    sensor.id.should.be.equal(sensor_id)
    sensor.get_temperature(W1ThermSensor.DEGREES_C).should.be.equal(26.55, epsilon=FLOAT_EPSILON)


@mock_kernel_modules
def test_sensor_temperature_in_F():
    # 20 C = 68 F
    # 26.55 C = 79.79 F

    # create DS18B20 sensor with 20 C degrees
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20, temperature=20)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    sensor.id.should.be.equal(sensor_id)
    sensor.get_temperature(W1ThermSensor.DEGREES_F).should.be.equal(68.0)

    # create DS18B20 sensor with 26.55 C degrees
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20, temperature=26.55)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    sensor.id.should.be.equal(sensor_id)
    sensor.get_temperature(W1ThermSensor.DEGREES_F).should.be.equal(79.79, epsilon=FLOAT_EPSILON)


@mock_kernel_modules
def test_sensor_temperature_in_K():
    # 20 C = 293.15 K
    # 26.55 C = 299.7 K

    # create DS18B20 sensor with 20 C degrees
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20, temperature=20)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    sensor.id.should.be.equal(sensor_id)
    sensor.get_temperature(W1ThermSensor.KELVIN).should.be.equal(293.15)

    # create DS18B20 sensor with 26.55 C degrees
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20, temperature=26.55)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    sensor.id.should.be.equal(sensor_id)
    sensor.get_temperature(W1ThermSensor.KELVIN).should.be.equal(299.7, epsilon=FLOAT_EPSILON)


@mock_kernel_modules
def test_sensor_all_temperature_units():
    # create DS18B20 sensor with 20 C degrees
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20, temperature=20)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    sensor.id.should.be.equal(sensor_id)
    sensor.get_temperatures([W1ThermSensor.DEGREES_C, W1ThermSensor.DEGREES_F, W1ThermSensor.KELVIN]).should.be.equal([20, 68, 293.15])


@mock_kernel_modules
def test_sensor_type_name():
    # create sensors of all types
    ds18s20_sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18S20)
    ds1822_sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS1822)
    ds18b20_sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18S20, ds18s20_sensor_id)
    sensor.type_name.should.be.equal("DS18S20")

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS1822, ds1822_sensor_id)
    sensor.type_name.should.be.equal("DS1822")

    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, ds18b20_sensor_id)
    sensor.type_name.should.be.equal("DS18B20")


@mock_kernel_modules
def test_no_sensor_found_error():
    W1ThermSensor.when.called_with().should.throw(NoSensorFoundError, "No Unknown temperature sensor with id '' found")
    W1ThermSensor.when.called_with(W1ThermSensor.THERM_SENSOR_DS1822).should.throw(NoSensorFoundError, "No DS1822 temperature sensor with id '' found")

    sensor_id = RANDOM_SENSOR_ID()
    W1ThermSensor.when.called_with(W1ThermSensor.THERM_SENSOR_DS1822, sensor_id).should.throw(NoSensorFoundError, "No DS1822 temperature sensor with id '%s' found" % sensor_id)


@mock_kernel_modules
def test_sensor_not_ready_error():
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS1822, w1_file=W1_FILE_NOT_READY)
    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS1822, sensor_id)
    sensor.get_temperature.when.called_with(W1ThermSensor.DEGREES_C).should.throw(SensorNotReadyError, "Sensor is not yet ready to read temperature")


@mock_kernel_modules
def test_unsupported_unit_error():
    unsupported_unit = 0xFF
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS1822)
    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS1822, sensor_id)
    sensor.get_temperature.when.called_with(unsupported_unit).should.throw(UnsupportedUnitError, "Only Degrees C, F and Kelvin are currently supported")


@mock_kernel_modules
def test_repr():
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    s1 = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    s2 = eval(repr(s1))

    s1.id.should.be.equal(s2.id)
    s1.type.should.be.equal(s2.type)


@mock_kernel_modules
def test_str():
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    s1 = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)

    str(s1).should.be.equal("W1ThermSensor(name='DS18B20', type=40(0x28), id='%s')" % sensor_id)


def test_kernel_module_not_loaded():
    with patch("w1thermsensor.core.os.system"):
        load_kernel_modules.when.called_with().should.throw(KernelModuleLoadError, "Cannot load w1 therm kernel modules")


def test_sensor_does_not_exist_after_init():
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)

    # remove sensor path
    os.remove(sensor.sensorpath)

    try:
        sensor.raw_sensor_value
    except NoSensorFoundError as e:
        if str(e) != "No DS18B20 temperature sensor with id '%s' found" % sensor_id:
            raise RuntimeError("No NoSensorFoundError raised")


@mock_kernel_modules
def test_set_precision():
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)

    with patch("subprocess.call") as mock_call:
        mock_call.return_value = 0
        sensor.set_precision(10)
        mock_call.assert_called_with("echo {0} > {1}".format(
            10, sensor.sensorpath), shell=True)


@mock_kernel_modules
def test_set_precision_and_persist():
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)

    with patch("subprocess.call") as mock_call:
        mock_call.return_value = 0
        sensor.set_precision(10, persist=True)
        mock_call.mock_calls[0][1][0].should.be.equal("echo {0} > {1}".format(
            10, sensor.sensorpath))
        mock_call.mock_calls[1][1][0].should.be.equal("echo 0 > {0}".format(
            sensor.sensorpath))


@mock_kernel_modules
def test_set_precision_failure():
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)

    with patch("subprocess.call") as mock_call:
        mock_call.return_value = 1
        sensor.set_precision.when.called_with(10).should.throw(W1ThermSensorError)


@mock_kernel_modules
def test_set_precision_and_persist_failure():
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)

    with patch("subprocess.call") as mock_call:
        mock_call.side_effect = [0, 1]
        sensor.set_precision.when.called_with(10, persist=True).should.throw(W1ThermSensorError)


@mock_kernel_modules
def test_set_invalid_precision():
    sensor_id = create_w1_therm_sensor(W1ThermSensor.THERM_SENSOR_DS18B20)
    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)

    sensor.set_precision.when.called_with(8).should.throw(ValueError)
    sensor.set_precision.when.called_with(13).should.throw(ValueError)
