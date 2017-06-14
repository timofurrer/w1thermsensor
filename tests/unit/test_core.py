# -*- coding: utf-8 -*-

import os

import pytest

from w1thermsensor.core import W1ThermSensor, load_kernel_modules
from w1thermsensor.errors import W1ThermSensorError, KernelModuleLoadError
from w1thermsensor.errors import NoSensorFoundError, SensorNotReadyError, UnsupportedUnitError


@pytest.mark.parametrize('sensors', [
    tuple(),
    (
        {'type': W1ThermSensor.THERM_SENSOR_DS18B20},
    ),
    (
        {'type': W1ThermSensor.THERM_SENSOR_DS18B20},
        {'type': W1ThermSensor.THERM_SENSOR_DS1822},
        {'type': W1ThermSensor.THERM_SENSOR_DS18S20}
    )
], indirect=['sensors'])
def test_get_available_sensors(sensors):
    """Test getting available sensors"""
    # given & when
    available_sensors = W1ThermSensor.get_available_sensors()
    # then
    assert len(available_sensors) == len(sensors)
    assert {t.type for t in available_sensors} == {s['type'] for s in sensors}


@pytest.mark.parametrize('sensors, sensor_types', [
    (
        (
            {'type': W1ThermSensor.THERM_SENSOR_DS18S20},
            {'type': W1ThermSensor.THERM_SENSOR_DS18S20},
            {'type': W1ThermSensor.THERM_SENSOR_DS18B20}
        ), [W1ThermSensor.THERM_SENSOR_DS18S20]
    ),
    (
        (
            {'type': W1ThermSensor.THERM_SENSOR_MAX31850K},
            {'type': W1ThermSensor.THERM_SENSOR_DS18S20},
            {'type': W1ThermSensor.THERM_SENSOR_DS18B20}
        ), [W1ThermSensor.THERM_SENSOR_DS28EA00]
    ),
    (
        (
            {'type': W1ThermSensor.THERM_SENSOR_MAX31850K},
            {'type': W1ThermSensor.THERM_SENSOR_DS18S20},
            {'type': W1ThermSensor.THERM_SENSOR_DS18B20}
        ), [W1ThermSensor.THERM_SENSOR_MAX31850K]
    ),
    (
        (
            {'type': W1ThermSensor.THERM_SENSOR_MAX31850K},
            {'type': W1ThermSensor.THERM_SENSOR_DS18S20},
            {'type': W1ThermSensor.THERM_SENSOR_DS18B20}
        ), [W1ThermSensor.THERM_SENSOR_MAX31850K, W1ThermSensor.THERM_SENSOR_DS18S20]
    ),
    (
        (
            {'type': W1ThermSensor.THERM_SENSOR_MAX31850K},
            {'type': W1ThermSensor.THERM_SENSOR_DS18S20},
            {'type': W1ThermSensor.THERM_SENSOR_DS18B20}
        ), [W1ThermSensor.THERM_SENSOR_MAX31850K, W1ThermSensor.THERM_SENSOR_DS18S20,
            W1ThermSensor.THERM_SENSOR_DS18B20]
    ),
], indirect=['sensors'])
def test_get_available_sensors_of_type(sensors, sensor_types):
    """Test getting available sensors of specific type"""
    # given & when
    available_sensors = W1ThermSensor.get_available_sensors(sensor_types)
    # then
    expected_sensor_amount = len([s for s in sensors if s['type'] in sensor_types])
    assert len(available_sensors) == expected_sensor_amount


@pytest.mark.parametrize('sensors', [
    ({'type': W1ThermSensor.THERM_SENSOR_DS18B20},)
], indirect=['sensors'])
def test_init_first_sensor(sensors):
    """Test that first found sensor is initialized if no sensor specs given"""
    # given
    sensor_id = sensors[0]['id']
    sensor_type = sensors[0]['type']
    # when
    sensor = W1ThermSensor()
    # then
    assert sensor.id == sensor_id
    assert sensor.type == sensor_type


@pytest.mark.parametrize('sensors, sensor_type', [
    (
        (
            {'type': W1ThermSensor.THERM_SENSOR_DS18B20},
        ), W1ThermSensor.THERM_SENSOR_DS18B20
    ),
    (
        (
            {'type': W1ThermSensor.THERM_SENSOR_DS18B20},
            {'type': W1ThermSensor.THERM_SENSOR_DS18S20}
        ), W1ThermSensor.THERM_SENSOR_DS18B20
    )
], indirect=['sensors'])
def test_init_first_sensor_of_type(sensors, sensor_type):
    """Test that first found sensor of specific type is initialized if not sensor specs given"""
    # given
    sensor_id = sensors[0]['id']
    # when
    sensor = W1ThermSensor(sensor_type)
    # then
    assert sensor.id == sensor_id
    assert sensor.type == sensor_type


@pytest.mark.parametrize('sensors, sensor_id', [
    (
        (
            {'id': '1', 'type': W1ThermSensor.THERM_SENSOR_DS18B20},
        ), '1'
    ),
    (
        (
            {'id': '2', 'type': W1ThermSensor.THERM_SENSOR_DS18S20},
            {'id': '1', 'type': W1ThermSensor.THERM_SENSOR_DS18B20}
        ), '2'
    )
], indirect=['sensors'])
def test_init_first_sensor_by_id(sensors, sensor_id):
    """Test that sensor can be initialized by id"""
    # given
    sensor_type = sensors[0]['type']
    # when
    sensor = W1ThermSensor(sensor_id=sensor_id)
    # then
    assert sensor.id == sensor_id
    assert sensor.type == sensor_type


@pytest.mark.parametrize('sensors, sensor_specs', [
    (
        (
            {'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},
        ), {'sensor_type': W1ThermSensor.THERM_SENSOR_DS18B20, 'sensor_id': '1'}
    ),
    (
        (
            {'type': W1ThermSensor.THERM_SENSOR_DS18S20, 'id': '2'},
        ), {'sensor_type': W1ThermSensor.THERM_SENSOR_DS18S20, 'sensor_id': '2'}
    ),
    (
        (
            {'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},
            {'type': W1ThermSensor.THERM_SENSOR_DS18S20, 'id': '2'}
        ), {'sensor_type': W1ThermSensor.THERM_SENSOR_DS18S20, 'sensor_id': '2'}
    )
], indirect=['sensors'])
def test_init_sensor_by_type_and_id(sensors, sensor_specs):
    """Test initialize sensor by given type and id"""
    # when
    sensor = W1ThermSensor(**sensor_specs)
    # then
    assert sensor.id == sensor_specs['sensor_id']
    assert sensor.type == sensor_specs['sensor_type']


@pytest.mark.parametrize('sensors, unit, expected_temperature', [
    (
        ({'temperature': 20.0},), W1ThermSensor.DEGREES_C, 20.0
    ),
    (
        ({'temperature': 42.21},), W1ThermSensor.DEGREES_C, 42.21
    ),
    (
        ({'temperature': 42.21},), W1ThermSensor.DEGREES_F, 107.978
    ),
    (
        ({'temperature': 42.21},), W1ThermSensor.KELVIN, 315.36
    )
], indirect=['sensors'])
def test_get_temperature_for_different_units(sensors, unit, expected_temperature):
    """Test getting a sensor temperature for different units"""
    # given
    sensor = W1ThermSensor()
    # when
    temperature = sensor.get_temperature(unit)
    # then
    assert temperature == pytest.approx(expected_temperature)


@pytest.mark.parametrize('sensors, unit, expected_temperature', [
    (
        ({'temperature': 42.21},), 'celsius', 42.21
    ),
    (
        ({'temperature': 42.21},), 'fahrenheit', 107.978
    ),
    (
        ({'temperature': 42.21},), 'kelvin', 315.36
    )
], indirect=['sensors'])
def test_get_temperature_for_different_units_by_name(sensors, unit, expected_temperature):
    """Test getting a sensor temperature for different units by name"""
    # given
    sensor = W1ThermSensor()
    # when
    temperature = sensor.get_temperature(unit)
    # then
    assert temperature == pytest.approx(expected_temperature)


@pytest.mark.parametrize('sensors, units, expected_temperatures', [
    (
        ({'temperature': 20.0},), [W1ThermSensor.DEGREES_C], [20.0]
    ),
    (
        ({'temperature': 42.21},), [W1ThermSensor.DEGREES_C, W1ThermSensor.DEGREES_F],
        [42.21, 107.978]
    ),
    (
        ({'temperature': 42.21},), [W1ThermSensor.DEGREES_F, W1ThermSensor.KELVIN],
        [107.978, 315.36]
    ),
    (
        ({'temperature': 42.21},), [W1ThermSensor.DEGREES_C, W1ThermSensor.DEGREES_F,
                                    W1ThermSensor.KELVIN], [42.21, 107.978, 315.36]
    )
], indirect=['sensors'])
def test_get_temperature_in_multiple_units(sensors, units, expected_temperatures):
    """Test getting a sensor temperature in multiple units"""
    # given
    sensor = W1ThermSensor()
    # when
    temperatures = sensor.get_temperatures(units)
    # then
    assert temperatures == pytest.approx(expected_temperatures)


@pytest.mark.parametrize('sensors, expected_sensor_name', [
    (({'type': W1ThermSensor.THERM_SENSOR_DS1822},), 'DS1822'),
    # The DS1825 sensor is the same as MAX31850K
    (({'type': W1ThermSensor.THERM_SENSOR_DS1825},), 'MAX31850K'),
    (({'type': W1ThermSensor.THERM_SENSOR_DS18S20},), 'DS18S20'),
    (({'type': W1ThermSensor.THERM_SENSOR_DS18B20},), 'DS18B20'),
    (({'type': W1ThermSensor.THERM_SENSOR_DS28EA00},), 'DS28EA00'),
    (({'type': W1ThermSensor.THERM_SENSOR_MAX31850K},), 'MAX31850K')
], indirect=['sensors'])
def test_sensor_type_name(sensors, expected_sensor_name):
    """Test getting the sensor type name"""
    # given
    sensor = W1ThermSensor()
    # when
    sensor_name = sensor.type_name
    # then
    assert sensor_name == expected_sensor_name


@pytest.mark.parametrize('sensors', [tuple()], indirect=['sensors'])
def test_no_sensor_found(sensors):
    """Test exception when no sensor was found"""
    with pytest.raises(NoSensorFoundError) as exc:
        W1ThermSensor()

    assert str(exc.value) == "No Unknown temperature sensor with id '' found"

    with pytest.raises(NoSensorFoundError) as exc:
        W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS1822, '1')

    assert str(exc.value) == "No DS1822 temperature sensor with id '1' found"


@pytest.mark.parametrize('sensors', [
    ({'ready': False},)
], indirect=['sensors'])
def test_sensor_not_ready(sensors):
    """Test exception when sensor is not ready yet"""
    # given
    sensor = W1ThermSensor()
    # when
    with pytest.raises(SensorNotReadyError) as exc:
        sensor.get_temperature()

    # then
    assert str(exc.value) == 'Sensor is not yet ready to read temperature'


@pytest.mark.parametrize('sensors', [
    # just a sensor
    ({},)
], indirect=['sensors'])
def test_unsupported_unit_error(sensors):
    """Test exception when requested to read temperature in unsupported unit"""
    # given
    sensor = W1ThermSensor()
    # when
    with pytest.raises(UnsupportedUnitError) as exc:
        sensor.get_temperature(unit=0xFF)  # 0xFF is no valid unit id

    # then
    assert str(exc.value) == 'Only Degrees C, F and Kelvin are currently supported'


@pytest.mark.parametrize('sensors', [
    # just a sensor
    ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},)
], indirect=['sensors'])
def test_repr_protocol(sensors):
    """Test the __repr__ protocol of a sensor instance"""
    # given
    sensor = W1ThermSensor()
    # when
    sensor_copy = eval(repr(sensor))
    # then
    assert sensor.id == sensor_copy.id
    assert sensor.type == sensor_copy.type


@pytest.mark.parametrize('sensors', [
    # just a sensor
    ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},)
], indirect=['sensors'])
def test_str_protocol(sensors):
    """Test __str__ protocol of a sensor instance"""
    # given
    sensor = W1ThermSensor()
    # when
    stringyfied = str(sensor)
    # then
    assert stringyfied == "W1ThermSensor(name='DS18B20', type=40(0x28), id='1')"


@pytest.mark.parametrize('sensors', [
    ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},)
], indirect=['sensors'])
def test_sensor_disconnect_after_init(sensors):
    """Test exception when sensor is disconnected after initialization"""
    # given
    sensor = W1ThermSensor()
    # disconnect sensor
    os.remove(sensor.sensorpath)
    # when
    with pytest.raises(NoSensorFoundError) as exc:
        sensor.raw_sensor_value
    # then
    assert str(exc.value) == "No DS18B20 temperature sensor with id '{0}' found".format(sensor.id)


@pytest.mark.parametrize('sensors, precision', [
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 9
    ),
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 10
    ),
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 11
    ),
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 12
    ),
], indirect=['sensors'])
def test_setting_sensor_precision(sensors, precision, mocker):
    """Test setting sensor precision"""
    # given
    sensor = W1ThermSensor()
    # mock subprocess.call
    subprocess_call = mocker.patch('subprocess.call')
    subprocess_call.return_value = 0
    # when
    sensor.set_precision(precision)
    # then
    subprocess_call.assert_called_with('echo {0} > {1}'.format(
        precision, sensor.sensorpath), shell=True)


@pytest.mark.parametrize('sensors, precision', [
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 9
    ),
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 10
    ),
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 11
    ),
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 12
    ),
], indirect=['sensors'])
def test_setting_and_persisting_sensor_precision(sensors, precision, mocker):
    """Test setting and persisting sensor precision"""
    # given
    sensor = W1ThermSensor()
    # mock subprocess.call
    subprocess_call = mocker.patch('subprocess.call')
    subprocess_call.return_value = 0
    # when
    sensor.set_precision(precision, persist=True)
    expected_calls = [
        mocker.call('echo {0} > {1}'.format(precision, sensor.sensorpath), shell=True),
        mocker.call('echo 0 > {0}'.format(sensor.sensorpath), shell=True),
    ]
    # then
    subprocess_call.assert_has_calls(expected_calls)


@pytest.mark.parametrize('sensors, precision', [
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 9
    ),
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 10
    ),
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 11
    ),
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 12
    ),
], indirect=['sensors'])
def test_setting_sensor_precision_failure(sensors, precision, mocker):
    """Test setting sensor precision failure"""
    # given
    sensor = W1ThermSensor()
    # mock subprocess.call
    subprocess_call = mocker.patch('subprocess.call')
    subprocess_call.return_value = 1
    # when
    with pytest.raises(W1ThermSensorError) as exc:
        sensor.set_precision(precision)
    # then
    assert str(exc.value) == 'Failed to change resolution to {0} bit'.format(precision)


@pytest.mark.parametrize('sensors, precision', [
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 9
    ),
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 10
    ),
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 11
    ),
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 12
    ),
], indirect=['sensors'])
def test_setting_and_persisting_sensor_precision_failure(sensors, precision, mocker):
    """Test setting and persisting sensor precision failure"""
    # given
    sensor = W1ThermSensor()
    # mock subprocess.call
    subprocess_call = mocker.patch('subprocess.call')
    subprocess_call.side_effect = [0, 1]
    # when
    with pytest.raises(W1ThermSensorError) as exc:
        sensor.set_precision(precision, persist=True)
    # then
    assert str(exc.value) == 'Failed to write precision configuration to sensor EEPROM'


@pytest.mark.parametrize('sensors, precision', [
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 8
    ),
    (
        ({'type': W1ThermSensor.THERM_SENSOR_DS18B20, 'id': '1'},), 13
    )
], indirect=['sensors'])
def test_setting_invalid_precision(sensors, precision):
    """Test setting invalid precision for sensor"""
    # given
    sensor = W1ThermSensor()
    # when
    with pytest.raises(ValueError) as exc:
        sensor.set_precision(precision)
    # then
    assert str(exc.value) == "The given sensor precision '{0}' is out of range (9-12)".format(
        precision)


def test_kernel_module_load_error(monkeypatch):
    """Test exception if kernel modules cannot be loaded"""
    # given
    # prevent os.system calls
    monkeypatch.setattr(os, 'system', lambda x: True)
    # when
    with pytest.raises(KernelModuleLoadError) as exc:
        load_kernel_modules()
    # then
    assert str(exc.value) == 'Cannot load w1 therm kernel modules'
