"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2020 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import os
import time

import pytest

from w1thermsensor.core import W1ThermSensor
from w1thermsensor.errors import (
    NoSensorFoundError,
    ResetValueError,
    SensorNotReadyError,
    UnsupportedUnitError,
    UnsupportedSensorError,
    W1ThermSensorError
)
from w1thermsensor.sensors import Sensor
from w1thermsensor.units import Unit


@pytest.mark.parametrize(
    "sensors",
    [
        tuple(),
        ({"type": Sensor.DS18B20},),
        ({"type": Sensor.DS18B20}, {"type": Sensor.DS1822}, {"type": Sensor.DS18S20},),
    ],
    indirect=["sensors"],
)
def test_get_available_sensors(sensors):
    """Test getting available sensors"""
    # given & when
    available_sensors = W1ThermSensor.get_available_sensors()
    # then
    assert len(available_sensors) == len(sensors)
    assert {t.type for t in available_sensors} == {s["type"] for s in sensors}


@pytest.mark.parametrize(
    "sensors, sensor_types",
    [
        (
            (
                {"type": Sensor.DS18S20},
                {"type": Sensor.DS18S20},
                {"type": Sensor.DS18B20},
            ),
            [Sensor.DS18S20],
        ),
        (
            (
                {"type": Sensor.MAX31850K},
                {"type": Sensor.DS18S20},
                {"type": Sensor.DS18B20},
            ),
            [Sensor.DS28EA00],
        ),
        (
            (
                {"type": Sensor.MAX31850K},
                {"type": Sensor.DS18S20},
                {"type": Sensor.DS18B20},
            ),
            [Sensor.MAX31850K],
        ),
        (
            (
                {"type": Sensor.MAX31850K},
                {"type": Sensor.DS18S20},
                {"type": Sensor.DS18B20},
            ),
            [Sensor.MAX31850K, Sensor.DS18S20],
        ),
        (
            (
                {"type": Sensor.MAX31850K},
                {"type": Sensor.DS18S20},
                {"type": Sensor.DS18B20},
            ),
            [Sensor.MAX31850K, Sensor.DS18S20, Sensor.DS18B20,],
        ),
    ],
    indirect=["sensors"],
)
def test_get_available_sensors_of_type(sensors, sensor_types):
    """Test getting available sensors of specific type"""
    # given & when
    available_sensors = W1ThermSensor.get_available_sensors(sensor_types)
    # then
    expected_sensor_amount = len([s for s in sensors if s["type"] in sensor_types])
    assert len(available_sensors) == expected_sensor_amount


@pytest.mark.parametrize("sensors", [({"type": Sensor.DS18B20},)], indirect=["sensors"])
def test_get_available_sensor_of_type_by_string_name(sensors):
    # given & when
    available_sensors = W1ThermSensor.get_available_sensors(["DS18B20"])
    # then
    assert len(available_sensors) == 1


@pytest.mark.parametrize("sensors", [({"type": Sensor.DS18B20},)], indirect=["sensors"])
def test_return_no_sensors_for_invalid_type(sensors):
    # given
    not_supported_sensor_name = "NOT-SUPPORTED"

    # then
    with pytest.raises(UnsupportedSensorError):
        # when
        W1ThermSensor.get_available_sensors([not_supported_sensor_name])


@pytest.mark.parametrize("sensors", [({"type": Sensor.DS18B20},)], indirect=["sensors"])
def test_init_first_sensor(sensors):
    """Test that first found sensor is initialized if no sensor specs given"""
    # given
    sensor_id = sensors[0]["id"]
    sensor_type = sensors[0]["type"]
    # when
    sensor = W1ThermSensor()
    # then
    assert sensor.id == sensor_id
    assert sensor.type == sensor_type


@pytest.mark.parametrize(
    "sensors, sensor_type",
    [
        (({"type": Sensor.DS18B20},), Sensor.DS18B20,),
        (({"type": Sensor.DS18B20}, {"type": Sensor.DS18S20},), Sensor.DS18B20,),
    ],
    indirect=["sensors"],
)
def test_init_first_sensor_of_type(sensors, sensor_type):
    """Test that first found sensor of specific type is initialized if not sensor specs given"""
    # given
    sensor_id = sensors[0]["id"]
    # when
    sensor = W1ThermSensor(sensor_type)
    # then
    assert sensor.id == sensor_id
    assert sensor.type == sensor_type


@pytest.mark.parametrize("sensors", [({"type": Sensor.DS1822},)], indirect=["sensors"])
def test_init_first_sensor_of_type_if_not_existent(sensors):
    # then
    with pytest.raises(
        NoSensorFoundError, match="Could not find any sensor of type DS18B20"
    ):
        # when
        W1ThermSensor(Sensor.DS18B20)


@pytest.mark.parametrize(
    "sensors", [({"type": Sensor.DS1822, "id": "1"},)], indirect=["sensors"]
)
def test_init_first_sensor_of_id_if_not_existent(sensors):
    # then
    with pytest.raises(NoSensorFoundError, match="Could not find sensor with id 2"):
        # when
        W1ThermSensor(sensor_id=2)


@pytest.mark.parametrize(
    "sensors, sensor_id",
    [
        (({"id": "1", "type": Sensor.DS18B20},), "1"),
        (
            ({"id": "2", "type": Sensor.DS18S20}, {"id": "1", "type": Sensor.DS18B20},),
            "2",
        ),
    ],
    indirect=["sensors"],
)
def test_init_first_sensor_by_id(sensors, sensor_id):
    """Test that sensor can be initialized by id"""
    # given
    sensor_type = sensors[0]["type"]
    # when
    sensor = W1ThermSensor(sensor_id=sensor_id)
    # then
    assert sensor.id == sensor_id
    assert sensor.type == sensor_type


@pytest.mark.parametrize(
    "sensors, sensor_specs",
    [
        (
            ({"type": Sensor.DS18B20, "id": "1"},),
            {"sensor_type": Sensor.DS18B20, "sensor_id": "1"},
        ),
        (
            ({"type": Sensor.DS18S20, "id": "2"},),
            {"sensor_type": Sensor.DS18S20, "sensor_id": "2"},
        ),
        (
            ({"type": Sensor.DS18B20, "id": "1"}, {"type": Sensor.DS18S20, "id": "2"},),
            {"sensor_type": Sensor.DS18S20, "sensor_id": "2"},
        ),
    ],
    indirect=["sensors"],
)
def test_init_sensor_by_type_and_id(sensors, sensor_specs):
    """Test initialize sensor by given type and id"""
    # when
    sensor = W1ThermSensor(**sensor_specs)
    # then
    assert sensor.id == sensor_specs["sensor_id"]
    assert sensor.type == sensor_specs["sensor_type"]


@pytest.mark.parametrize(
    "sensors, unit, expected_temperature",
    [
        (({"msb": 0x01, "lsb": 0x40, "temperature": 20.0},), Unit.DEGREES_C, 20.0,),
        (({"msb": 0xFF, "lsb": 0xF8, "temperature": -0.5},), Unit.DEGREES_C, -0.5,),
        (({"msb": 0xFC, "lsb": 0x90, "temperature": -55},), Unit.DEGREES_C, -55,),
        (({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},), "celsius", 25.0625),
        (({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},), "fahrenheit", 77.1125),
        (({"msb": 0xFC, "lsb": 0x90, "temperature": -55},), "fahrenheit", -67),
        (({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},), "kelvin", 298.2125),
        (({"msb": 0xFC, "lsb": 0x90, "temperature": -55},), "kelvin", 218.15),
    ],
    indirect=["sensors"],
)
def test_get_temperature_for_different_units(sensors, unit, expected_temperature):
    """Test getting a sensor temperature for different units"""
    # given
    sensor = W1ThermSensor()
    # when
    temperature = sensor.get_temperature(unit)
    # then
    assert temperature == pytest.approx(expected_temperature)


@pytest.mark.parametrize(
    "sensors, unit, expected_temperature",
    [
        (({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},), "celsius", 25.0625),
        (({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},), "fahrenheit", 77.1125),
        (({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},), "kelvin", 298.2125),
    ],
    indirect=["sensors"],
)
def test_get_temperature_for_different_units_by_name(
    sensors, unit, expected_temperature
):
    """Test getting a sensor temperature for different units by name"""
    # given
    sensor = W1ThermSensor()
    # when
    temperature = sensor.get_temperature(unit)
    # then
    assert temperature == pytest.approx(expected_temperature)


@pytest.mark.parametrize(
    "sensors, result_unit, offset_unit, offset, expected_offset, expected_temperature",
    [
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},),
            "celsius",
            "celsius",
            10,
            10,
            35.0625,
        ),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},),
            "fahrenheit",
            "celsius",
            10,
            18,
            95.1125,
        ),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},),
            "kelvin",
            "celsius",
            10,
            10,
            308.2125,
        ),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},),
            "celsius",
            "fahrenheit",
            18,
            10,
            35.0625,
        ),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},),
            "fahrenheit",
            "fahrenheit",
            18,
            18,
            95.1125,
        ),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},),
            "kelvin",
            "fahrenheit",
            18,
            10,
            308.2125,
        ),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},),
            "celsius",
            "kelvin",
            10,
            10,
            35.0625,
        ),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},),
            "fahrenheit",
            "kelvin",
            10,
            18,
            95.1125,
        ),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},),
            "kelvin",
            "kelvin",
            10,
            10,
            308.2125,
        ),
    ],
    indirect=["sensors"],
)
def test_get_temperature_for_different_units_by_name_with_offsets(
    sensors, result_unit, offset_unit, offset, expected_offset, expected_temperature
):
    """Test getting offset sensor values for different units"""
    # given
    sensor = W1ThermSensor(Sensor.DS18B20, 0, offset, offset_unit)
    # when
    temperature = sensor.get_temperature(result_unit)
    gotten_offset = sensor.get_offset(result_unit)
    # then
    assert temperature == pytest.approx(expected_temperature)
    assert gotten_offset == expected_offset


@pytest.mark.parametrize(
    "sensors, units, expected_temperatures",
    [
        (({"msb": 0x01, "lsb": 0x40, "temperature": 20.0},), [Unit.DEGREES_C], [20.0],),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},),
            [Unit.DEGREES_C, Unit.DEGREES_F],
            [25.0625, 77.1125],
        ),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.06251},),
            [Unit.DEGREES_F, Unit.KELVIN],
            [77.1125, 298.2125],
        ),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},),
            [Unit.DEGREES_C, Unit.DEGREES_F, Unit.KELVIN],
            [25.0625, 77.1125, 298.2125],
        ),
    ],
    indirect=["sensors"],
)
def test_get_temperature_in_multiple_units(sensors, units, expected_temperatures):
    """Test getting a sensor temperature in multiple units"""
    # given
    sensor = W1ThermSensor()
    # when
    temperatures = sensor.get_temperatures(units)
    # then
    assert temperatures == pytest.approx(expected_temperatures)


@pytest.mark.parametrize(
    "sensors, units, offset, expected_temperatures",
    [
        (
            ({"msb": 0x01, "lsb": 0x40, "temperature": 20.0},),
            [Unit.DEGREES_C],
            -10,
            [10.0],
        ),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},),
            [Unit.DEGREES_C, Unit.DEGREES_F],
            10,
            [35.0625, 95.1125],
        ),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.06251},),
            [Unit.DEGREES_F, Unit.KELVIN],
            10,
            [95.1125, 308.2125],
        ),
        (
            ({"msb": 0x01, "lsb": 0x91, "temperature": 25.0625},),
            [Unit.DEGREES_C, Unit.DEGREES_F, Unit.KELVIN],
            10,
            [35.0625, 95.1125, 308.2125],
        ),
    ],
    indirect=["sensors"],
)
def test_get_temperature_in_multiple_units_with_offsets(
    sensors, units, offset, expected_temperatures
):
    """Test getting a sensor temperature in multiple units"""
    # given
    sensor = W1ThermSensor()
    # when
    sensor.set_offset(offset)
    temperatures = sensor.get_temperatures(units)
    # then
    assert temperatures == pytest.approx(expected_temperatures)


@pytest.mark.parametrize(
    "sensors, expected_sensor_name",
    [
        (({"type": Sensor.DS1822},), "DS1822"),
        (({"type": Sensor.DS1825},), "DS1825"),
        (({"type": Sensor.DS18S20},), "DS18S20"),
        (({"type": Sensor.DS18B20},), "DS18B20"),
        (({"type": Sensor.DS28EA00},), "DS28EA00"),
        # The MAX31850K sensor is the same as DS1825
        (({"type": Sensor.MAX31850K},), "DS1825"),
    ],
    indirect=["sensors"],
)
def test_sensor_type_name(sensors, expected_sensor_name):
    """Test getting the sensor type name"""
    # given
    sensor = W1ThermSensor()
    # when
    sensor_name = sensor.name
    # then
    assert sensor_name == expected_sensor_name


@pytest.mark.parametrize("sensors", [tuple()], indirect=["sensors"])
def test_no_sensor_found(sensors, monkeypatch):
    """Test exception when no sensor was found"""
    monkeypatch.setattr(time, "sleep", lambda x: True)

    with pytest.raises(NoSensorFoundError, match="Could not find any sensor"):
        W1ThermSensor()

    with pytest.raises(
        NoSensorFoundError, match="Could not find sensor of type DS1822 with id 1"
    ):
        W1ThermSensor(Sensor.DS1822, "1")


@pytest.mark.parametrize("sensors", [({"ready": False},)], indirect=["sensors"])
def test_sensor_not_ready(sensors):
    """Test exception when sensor is not ready yet"""
    # given
    sensor = W1ThermSensor()
    expected_error_msg = "Sensor {} is not yet ready to read temperature".format(
        sensor.id
    )

    # when & then
    with pytest.raises(SensorNotReadyError, match=expected_error_msg):
        sensor.get_temperature()


@pytest.mark.parametrize(
    "sensors",
    [
        # just a sensor
        ({},)
    ],
    indirect=["sensors"],
)
def test_unsupported_unit_error(sensors):
    """Test exception when requested to read temperature in unsupported unit"""
    # given
    sensor = W1ThermSensor()
    expected_error_msg = "Only Degrees C, F and Kelvin are currently supported"

    # when & then
    with pytest.raises(UnsupportedUnitError, match=expected_error_msg):
        sensor.get_temperature(unit=0xFF)  # 0xFF is no valid unit id


@pytest.mark.parametrize(
    "sensors",
    [
        # just a sensor
        ({"type": Sensor.DS18B20, "id": "1"},)
    ],
    indirect=["sensors"],
)
def test_repr_protocol(sensors):
    """Test the __repr__ protocol of a sensor instance"""
    # given
    sensor = W1ThermSensor()
    # when
    sensor_copy = eval(repr(sensor))
    # then
    assert sensor.id == sensor_copy.id
    assert sensor.type == sensor_copy.type


@pytest.mark.parametrize(
    "sensors",
    [
        # just a sensor
        ({"type": Sensor.DS18B20, "id": "1"},)
    ],
    indirect=["sensors"],
)
def test_str_protocol(sensors):
    """Test __str__ protocol of a sensor instance"""
    # given
    sensor = W1ThermSensor()
    # when
    stringyfied = str(sensor)
    # then
    assert stringyfied == "W1ThermSensor(name='DS18B20', type=40(0x28), id='1')"


@pytest.mark.parametrize(
    "sensors", [({"type": Sensor.DS18B20, "id": "1"},)], indirect=["sensors"],
)
def test_sensor_disconnect_after_init(sensors):
    """Test exception when sensor is disconnected after initialization"""
    # given
    sensor = W1ThermSensor()
    expected_error_msg = "Could not find sensor of type DS18B20 with id 1"

    # disconnect sensor
    os.remove(str(sensor.sensorpath))  # cast to str explicitly for Python 3.5

    # when & then
    with pytest.raises(NoSensorFoundError, match=expected_error_msg):
        sensor.get_raw_sensor_strings()


@pytest.mark.parametrize(
    "sensors, resolution",
    [
        (({"type": Sensor.DS18B20, "id": "1"},), 9),
        (({"type": Sensor.DS18B20, "id": "1"},), 10),
        (({"type": Sensor.DS18B20, "id": "1"},), 11),
        (({"type": Sensor.DS18B20, "id": "1"},), 12),
    ],
    indirect=["sensors"],
)
def test_setting_sensor_resolution(sensors, resolution, mocker):
    """Test setting sensor resolution"""
    # given
    sensor = W1ThermSensor()
    # mock subprocess.call
    subprocess_call = mocker.patch("subprocess.call")
    subprocess_call.return_value = 0
    # when
    sensor.set_resolution(resolution)
    # then
    subprocess_call.assert_called_with(
        "echo {0} > {1}".format(resolution, sensor.sensorpath), shell=True
    )


@pytest.mark.parametrize(
    "sensors, resolution",
    [
        (({"type": Sensor.DS18B20, "id": "1"},), 9),
        (({"type": Sensor.DS18B20, "id": "1"},), 10),
        (({"type": Sensor.DS18B20, "id": "1"},), 11),
        (({"type": Sensor.DS18B20, "id": "1"},), 12),
    ],
    indirect=["sensors"],
)
def test_setting_and_persisting_sensor_resolution(sensors, resolution, mocker):
    """Test setting and persisting sensor resolution"""
    # given
    sensor = W1ThermSensor()
    # mock subprocess.call
    subprocess_call = mocker.patch("subprocess.call")
    subprocess_call.return_value = 0
    # when
    sensor.set_resolution(resolution, persist=True)
    expected_calls = [
        mocker.call("echo {0} > {1}".format(resolution, sensor.sensorpath), shell=True),
        mocker.call("echo 0 > {0}".format(sensor.sensorpath), shell=True),
    ]
    # then
    subprocess_call.assert_has_calls(expected_calls)


@pytest.mark.parametrize(
    "sensors, resolution",
    [
        (({"type": Sensor.DS18B20, "id": "1"},), 9),
        (({"type": Sensor.DS18B20, "id": "1"},), 10),
        (({"type": Sensor.DS18B20, "id": "1"},), 11),
        (({"type": Sensor.DS18B20, "id": "1"},), 12),
    ],
    indirect=["sensors"],
)
def test_setting_sensor_resolution_failure(sensors, resolution, mocker):
    """Test setting sensor resolution failure"""
    # given
    sensor = W1ThermSensor()
    expected_error_msg = (
        "Failed to change resolution to {0} bit. "
        "You might have to be root to change the resolution".format(resolution)
    )

    # mock subprocess.call
    subprocess_call = mocker.patch("subprocess.call")
    subprocess_call.return_value = 1

    # when & then
    with pytest.raises(W1ThermSensorError, match=expected_error_msg):
        sensor.set_resolution(resolution)


@pytest.mark.parametrize(
    "sensors, resolution",
    [
        (({"type": Sensor.DS18B20, "id": "1"},), 9),
        (({"type": Sensor.DS18B20, "id": "1"},), 10),
        (({"type": Sensor.DS18B20, "id": "1"},), 11),
        (({"type": Sensor.DS18B20, "id": "1"},), 12),
    ],
    indirect=["sensors"],
)
def test_setting_and_persisting_sensor_resolution_failure(sensors, resolution, mocker):
    """Test setting and persisting sensor resolution failure"""
    # given
    sensor = W1ThermSensor()
    expected_error_msg = "Failed to write resolution configuration to sensor EEPROM"

    # mock subprocess.call
    subprocess_call = mocker.patch("subprocess.call")
    subprocess_call.side_effect = [0, 1]

    # when & then
    with pytest.raises(W1ThermSensorError, match=expected_error_msg):
        sensor.set_resolution(resolution, persist=True)


@pytest.mark.parametrize(
    "sensors, resolution",
    [
        (({"type": Sensor.DS18B20, "id": "1"},), 8),
        (({"type": Sensor.DS18B20, "id": "1"},), 13),
    ],
    indirect=["sensors"],
)
def test_setting_invalid_resolution(sensors, resolution):
    """Test setting invalid resolution for sensor"""
    # given
    sensor = W1ThermSensor()
    expected_error_msg = r"The given sensor resolution '{}' is out of range \(9-12\)".format(
        resolution
    )

    # when & then
    with pytest.raises(ValueError, match=expected_error_msg):
        sensor.set_resolution(resolution)


@pytest.mark.parametrize(
    "sensors, expected_resolution",
    [
        (({"config": 0x1F},), 9),
        (({"config": 0x3F},), 10),
        (({"config": 0x5F},), 11),
        (({"config": 0x7F},), 12),
    ],
    indirect=["sensors"],
)
def test_get_resolution(sensors, expected_resolution):
    """Test getting the sensor precison"""
    # given
    sensor = W1ThermSensor()
    # when
    resolution = sensor.get_resolution()
    # then
    assert resolution == pytest.approx(expected_resolution)


@pytest.mark.parametrize(
    "sensors",
    [(({"msb": 0x05, "lsb": 0x50, "temperature": 85.00},))],
    indirect=["sensors"],
)
def test_handling_reset_value(sensors):
    """Test handling the reset value from a sensor reading"""
    # given
    sensor = W1ThermSensor()
    expected_error_msg = (
        "Sensor {} yields the reset value of 85 degree millicelsius. "
        "Please check the power-supply for the sensor.".format(sensor.id)
    )

    # when & then
    with pytest.raises(ResetValueError, match=expected_error_msg):
        sensor.get_temperature()
