# -*- coding: utf-8 -*-

import json
import itertools

import pytest

from click.testing import CliRunner

from w1thermsensor.cli import cli
from w1thermsensor.core import W1ThermSensor


@pytest.mark.parametrize(
    "sensors",
    [
        tuple(),
        ({"type": W1ThermSensor.THERM_SENSOR_DS18B20},),
        (
            {"type": W1ThermSensor.THERM_SENSOR_DS18B20},
            {"type": W1ThermSensor.THERM_SENSOR_DS1822},
            {"type": W1ThermSensor.THERM_SENSOR_DS18S20},
        ),
    ],
    indirect=["sensors"],
)
def test_list_available_sensors(sensors):
    """Test listing available sensors"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(cli, ["ls"])
    # then
    assert result.exit_code == 0
    # expect the correct amount of sensors being detected
    assert "Found {0} sensors:".format(len(sensors)) in result.output
    # expect every sensor is detected
    for sensor in sensors:
        expected_output = "HWID: {0} Type: {1}".format(
            sensor["id"], W1ThermSensor.TYPE_NAMES[sensor["type"]]
        )
        assert expected_output in result.output


@pytest.mark.parametrize(
    "sensors",
    [
        tuple(),
        ({"type": W1ThermSensor.THERM_SENSOR_DS18B20},),
        (
            {"type": W1ThermSensor.THERM_SENSOR_DS18B20},
            {"type": W1ThermSensor.THERM_SENSOR_DS1822},
            {"type": W1ThermSensor.THERM_SENSOR_DS18S20},
        ),
    ],
    indirect=["sensors"],
)
def test_list_available_sensors_json(sensors):
    """Test listing available sensors in json"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(cli, ["ls", "--json"])
    # then
    assert result.exit_code == 0
    # is valid JSON document
    json_output = json.loads(result.output)
    # expect the correct amount of sensors
    assert len(json_output) == len(sensors)
    # expect every sensor is detected
    for sensor in sensors:
        assert '"hwid": "{0}"'.format(sensor["id"]) in result.output
        assert (
            '"type": "{0}"'.format(W1ThermSensor.TYPE_NAMES[sensor["type"]])
            in result.output
        )


@pytest.mark.parametrize(
    "sensors, sensor_types",
    [
        (tuple(), [W1ThermSensor.THERM_SENSOR_DS18B20]),
        (
            ({"type": W1ThermSensor.THERM_SENSOR_DS18B20},),
            [W1ThermSensor.THERM_SENSOR_DS18B20],
        ),
        (
            (
                {"type": W1ThermSensor.THERM_SENSOR_DS18B20},
                {"type": W1ThermSensor.THERM_SENSOR_DS1822},
                {"type": W1ThermSensor.THERM_SENSOR_DS18S20},
            ),
            [W1ThermSensor.THERM_SENSOR_DS18B20, W1ThermSensor.THERM_SENSOR_DS1822],
        ),
    ],
    indirect=["sensors"],
)
def test_list_available_sensors_by_type(sensors, sensor_types):
    """Test listing available sensors"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(
        cli,
        ["ls"]
        + list(
            itertools.chain.from_iterable(
                ("-t", W1ThermSensor.TYPE_NAMES[x]) for x in sensor_types
            )
        ),
    )
    # then
    assert result.exit_code == 0
    # expect the correct amount of sensors being detected
    expected_sensors = [s for s in sensors if s["type"] in sensor_types]
    assert "Found {0} sensors:".format(len(expected_sensors)) in result.output
    # expect every sensor is detected
    for sensor in expected_sensors:
        expected_output = "HWID: {0} Type: {1}".format(
            sensor["id"], W1ThermSensor.TYPE_NAMES[sensor["type"]]
        )
        assert expected_output in result.output


@pytest.mark.parametrize(
    "sensors",
    [
        tuple(),
        ({"type": W1ThermSensor.THERM_SENSOR_DS18B20, "temperature": 20.0},),
        (
            {"type": W1ThermSensor.THERM_SENSOR_DS18B20, "temperature": 42.0},
            {"type": W1ThermSensor.THERM_SENSOR_DS1822, "temperature": 21.0},
            {"type": W1ThermSensor.THERM_SENSOR_DS18S20, "temperature": -8.0},
        ),
    ],
    indirect=["sensors"],
)
def test_get_temperature_all_sensors(sensors):
    """Test getting temperature from all sensors"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(cli, ["all"])
    # then
    assert result.exit_code == 0
    # expect the correct amount of sensors being detected
    assert "Got temperatures of {0} sensors:".format(len(sensors)) in result.output
    # expect every sensor is detected
    for sensor in sensors:
        expected_output = "({0}) measured temperature: {1} celsius".format(
            sensor["id"], sensor["temperature"]
        )
        assert expected_output in result.output


@pytest.mark.parametrize(
    "sensors",
    [
        tuple(),
        ({"type": W1ThermSensor.THERM_SENSOR_DS18B20, "temperature": 20.0},),
        (
            {"type": W1ThermSensor.THERM_SENSOR_DS18B20, "temperature": 42.0},
            {"type": W1ThermSensor.THERM_SENSOR_DS1822, "temperature": 21.0},
            {"type": W1ThermSensor.THERM_SENSOR_DS18S20, "temperature": -8.0},
        ),
    ],
    indirect=["sensors"],
)
def test_get_temperature_all_sensors_json(sensors):
    """Test getting temperature from all sensors in json"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(cli, ["all", "--json"])
    # then
    assert result.exit_code == 0
    # is valid JSON document
    json_output = json.loads(result.output)
    # expect the correct amount of sensors
    assert len(json_output) == len(sensors)
    # expect every sensor is detected
    for sensor in sensors:
        assert '"hwid": "{0}"'.format(sensor["id"]) in result.output
        assert (
            '"type": "{0}"'.format(W1ThermSensor.TYPE_NAMES[sensor["type"]])
            in result.output
        )
        assert '"temperature": {0}'.format(sensor["temperature"]) in result.output
        assert '"unit": "celsius"' in result.output


@pytest.mark.parametrize(
    "sensors",
    [
        ({"type": W1ThermSensor.THERM_SENSOR_DS18B20, "temperature": 20.0},),
        (
            {"type": W1ThermSensor.THERM_SENSOR_DS18B20, "temperature": 42.0},
            {"type": W1ThermSensor.THERM_SENSOR_DS1822, "temperature": 21.0},
            {"type": W1ThermSensor.THERM_SENSOR_DS18S20, "temperature": -8.0},
        ),
    ],
    indirect=["sensors"],
)
def test_get_temperature_all_sensors_with_precision(sensors, mocker):
    """Test getting temperature from all sensors"""
    # given
    runner = CliRunner()
    set_precision_mock = mocker.patch("w1thermsensor.W1ThermSensor.set_precision")
    set_precision_mock.return_value = 0
    # when
    result = runner.invoke(cli, ["all", "--precision", "10"])
    # then
    assert result.exit_code == 0
    # expect that set precision was called
    set_precision_mock.assert_called_with(10, persist=False)
    # expect the correct amount of sensors being detected
    assert "Got temperatures of {0} sensors:".format(len(sensors)) in result.output
    # expect every sensor is detected
    for sensor in sensors:
        expected_output = "({0}) measured temperature: {1} celsius".format(
            sensor["id"], sensor["temperature"]
        )
        assert expected_output in result.output


@pytest.mark.parametrize(
    "sensors, sensor_types",
    [
        (tuple(), [W1ThermSensor.THERM_SENSOR_DS18B20]),
        (
            ({"type": W1ThermSensor.THERM_SENSOR_DS18B20, "temperature": 20.0},),
            [W1ThermSensor.THERM_SENSOR_DS18B20],
        ),
        (
            (
                {"type": W1ThermSensor.THERM_SENSOR_DS18B20, "temperature": 42.0},
                {"type": W1ThermSensor.THERM_SENSOR_DS1822, "temperature": 21.0},
                {"type": W1ThermSensor.THERM_SENSOR_DS18S20, "temperature": -8.0},
            ),
            [W1ThermSensor.THERM_SENSOR_DS18B20, W1ThermSensor.THERM_SENSOR_DS1822],
        ),
    ],
    indirect=["sensors"],
)
def test_get_temperature_all_sensors_by_type(sensors, sensor_types):
    """Test getting temperature from all sensors by type"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(
        cli,
        ["all"]
        + list(
            itertools.chain.from_iterable(
                ("-t", W1ThermSensor.TYPE_NAMES[x]) for x in sensor_types
            )
        ),
    )
    # then
    assert result.exit_code == 0
    # expect the correct amount of sensors being detected
    expected_sensors = [s for s in sensors if s["type"] in sensor_types]
    assert (
        "Got temperatures of {0} sensors:".format(len(expected_sensors))
        in result.output
    )
    # expect every sensor is detected
    for sensor in expected_sensors:
        expected_output = "({0}) measured temperature: {1} celsius".format(
            sensor["id"], sensor["temperature"]
        )
        assert expected_output in result.output


@pytest.mark.parametrize(
    "sensors, temperature, unit",
    [
        (
            ({"type": W1ThermSensor.THERM_SENSOR_DS18B20, "temperature": 42.0},),
            315.15,
            "kelvin",
        ),
        (
            ({"type": W1ThermSensor.THERM_SENSOR_DS18B20, "temperature": 42.0},),
            107.6,
            "fahrenheit",
        ),
        (
            ({"type": W1ThermSensor.THERM_SENSOR_DS18B20, "temperature": 42.0},),
            42.0,
            "celsius",
        ),
    ],
    indirect=["sensors"],
)
def test_get_temperature_all_sensors_in_unit(sensors, temperature, unit):
    """Test getting temperature from all sensors in specific unit"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(cli, ["all", "--unit", unit])
    # then
    assert result.exit_code == 0
    # expect the correct amount of sensors being detected
    assert "Got temperatures of {0} sensors:".format(len(sensors)) in result.output
    # expect every sensor is detected
    for sensor in sensors:
        expected_output = "({0}) measured temperature: {1} {2}".format(
            sensor["id"], temperature, unit
        )
        assert expected_output in result.output


@pytest.mark.parametrize(
    "sensors",
    [
        ({"type": W1ThermSensor.THERM_SENSOR_DS18B20, "temperature": 20.0},),
        ({"type": W1ThermSensor.THERM_SENSOR_DS18S20, "temperature": -8.0},),
    ],
    indirect=["sensors"],
)
def test_get_temperature_of_sensor(sensors):
    """Test getting temperature of a single sensor"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(cli, ["get"])
    # then
    assert result.exit_code == 0
    # expect the single sensor to be reported correctly
    sensor = sensors[0]
    expected_output = "Sensor {0} measured temperature: {1} celsius".format(
        sensor["id"], sensor["temperature"]
    )
    assert expected_output in result.output


@pytest.mark.parametrize(
    "sensors",
    [
        ({"type": W1ThermSensor.THERM_SENSOR_DS18B20, "temperature": 20.0},),
        ({"type": W1ThermSensor.THERM_SENSOR_DS18S20, "temperature": -8.0},),
    ],
    indirect=["sensors"],
)
def test_get_temperature_of_sensor_json(sensors):
    """Test getting temperature of a single sensor in json"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(cli, ["get", "--json"])
    # then
    assert result.exit_code == 0
    # is valid JSON document
    json_output = json.loads(result.output)
    # expect the single sensor to be reported correctly
    sensor = sensors[0]
    expected_json_output = {
        "hwid": sensor["id"],
        "offset": 0.0,
        "type": W1ThermSensor.TYPE_NAMES[sensor["type"]],
        "temperature": sensor["temperature"],
        "unit": "celsius",
    }
    assert expected_json_output == json_output


@pytest.mark.parametrize(
    "sensors, hwid",
    [
        (
            (
                {
                    "id": "1",
                    "type": W1ThermSensor.THERM_SENSOR_DS18B20,
                    "temperature": 20.0,
                },
                {
                    "id": "2",
                    "type": W1ThermSensor.THERM_SENSOR_DS18S20,
                    "temperature": -8.0,
                },
            ),
            "1",
        ),
        (
            (
                {
                    "id": "1",
                    "type": W1ThermSensor.THERM_SENSOR_DS18S20,
                    "temperature": -8.0,
                },
                {
                    "id": "2",
                    "type": W1ThermSensor.THERM_SENSOR_DS18S20,
                    "temperature": -8.0,
                },
            ),
            "2",
        ),
    ],
    indirect=["sensors"],
)
def test_get_temperature_of_sensor_by_hwid(sensors, hwid):
    """Test getting temperature of a single sensor by hwid"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(cli, ["get", "--json", "--hwid", hwid])
    # then
    assert result.exit_code == 0
    # is valid JSON document
    json_output = json.loads(result.output)
    # expect the single sensor to be reported correctly
    sensor = [s for s in sensors if s["id"] == hwid][0]
    expected_json_output = {
        "hwid": sensor["id"],
        "offset": 0.0,
        "type": W1ThermSensor.TYPE_NAMES[sensor["type"]],
        "temperature": sensor["temperature"],
        "unit": "celsius",
    }
    assert expected_json_output == json_output


@pytest.mark.parametrize(
    "sensors",
    [
        ({"type": W1ThermSensor.THERM_SENSOR_DS18B20, "temperature": 20.0},),
        ({"type": W1ThermSensor.THERM_SENSOR_DS18S20, "temperature": -8.0},),
    ],
    indirect=["sensors"],
)
def test_get_temperature_of_sensor_with_precision(sensors, mocker):
    """Test getting temperature of a single sensor with precision"""
    # given
    runner = CliRunner()
    set_precision_mock = mocker.patch("w1thermsensor.W1ThermSensor.set_precision")
    set_precision_mock.return_value = 0
    # when
    result = runner.invoke(cli, ["get", "--precision", "10"])
    # then
    assert result.exit_code == 0
    # expect that precision was called
    set_precision_mock.assert_called_with(10, persist=False)
    # expect the single sensor to be reported correctly
    sensor = sensors[0]
    expected_output = "Sensor {0} measured temperature: {1} celsius".format(
        sensor["id"], sensor["temperature"]
    )
    assert expected_output in result.output


@pytest.mark.parametrize(
    "sensors, offset, expected_temperature",
    [
        (({"type": W1ThermSensor.THERM_SENSOR_DS18B20, "temperature": 20.0},), 10, 30.0,),
        (({"type": W1ThermSensor.THERM_SENSOR_DS18S20, "temperature": -8.0},), 10, 2.0,),
    ],
    indirect=["sensors"],
)
def test_get_temperature_of_sensor_with_offset(
        sensors, offset, expected_temperature, mocker
):
    """Test getting temperature of a single sensor with an offset"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(cli, ["get", "--offset", offset])
    # then
    assert result.exit_code == 0
    # expect the single sensor to be reported correctly, with offset applied
    sensor = sensors[0]
    expected_output = "Sensor {0} measured temperature: {1} celsius".format(
        sensor["id"], expected_temperature
    )
    assert expected_output in result.output


def test_get_temperature_of_sensor_with_invalid_options():
    """Test exception which is raised when passing incompatible options to get sensor"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(
        cli, ["get", "--json", "1", "--type", "DS18B20", "--hwid", "1"]
    )
    # then
    assert result.exit_code != 0
    assert result.exception
    assert "If --id is given --hwid and --type are not allowed." in result.output


@pytest.mark.parametrize("sensors", [tuple()], indirect=["sensors"])
def test_get_temperature_of_sensor_with_invalid_id(sensors):
    """Test exception which is raised when passing invalid sensor id options to get sensor"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(cli, ["get", "--json", "1"])
    # then
    assert result.exit_code != 0
    assert result.exception
    assert (
        "No sensor with id 1 available. "
        "Use the ls command to show all available sensors." in result.output
    )


def test_set_precision_of_sensor_with_invalid_options():
    """Test exception which is raised when passing incompatible options to preicison sensor cmd"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(
        cli, ["precision", "10", "1", "--type", "DS18B20", "--hwid", "1"]
    )
    # then
    assert result.exit_code != 0
    assert result.exception
    assert "If --id is given --hwid and --type are not allowed." in result.output


@pytest.mark.parametrize(
    "sensors, hwid",
    [
        (
            (
                {
                    "id": "1",
                    "type": W1ThermSensor.THERM_SENSOR_DS18B20,
                    "temperature": 20.0,
                },
                {
                    "id": "2",
                    "type": W1ThermSensor.THERM_SENSOR_DS18S20,
                    "temperature": -8.0,
                },
            ),
            "1",
        ),
        (
            (
                {
                    "id": "1",
                    "type": W1ThermSensor.THERM_SENSOR_DS18S20,
                    "temperature": -8.0,
                },
                {
                    "id": "2",
                    "type": W1ThermSensor.THERM_SENSOR_DS18S20,
                    "temperature": -8.0,
                },
            ),
            "2",
        ),
    ],
    indirect=["sensors"],
)
def test_set_precision_of_sensor_by_hwid(sensors, hwid):
    """Test setting temperature precision of a single sensor by hwid"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(cli, ["precision", "9", "--hwid", hwid])
    # then
    assert result.exit_code == 0


@pytest.mark.parametrize("sensors", [tuple()], indirect=["sensors"])
def test_set_precision_of_sensor_with_invalid_id(sensors):
    """Test exception which is raised when passing invalid sensor id options to get sensor"""
    # given
    runner = CliRunner()
    # when
    result = runner.invoke(cli, ["precision", "9", "1"])
    # then
    assert result.exit_code != 0
    assert result.exception
    assert (
        "No sensor with id 1 available. "
        "Use the ls command to show all available sensors." in result.output
    )
