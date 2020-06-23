"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2020 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import json
from itertools import count

import click

from w1thermsensor.core import Sensor, Unit, W1ThermSensor

#: major click version to compensate API changes
CLICK_MAJOR_VERSION = int(click.__version__.split(".")[0])


def resolve_type_name(ctx, param, value):  # pylint: disable=unused-argument
    """Resolve CLI option type name"""
    if not value:
        return value

    if isinstance(value, tuple):
        return [Sensor[v] for v in value]
    else:
        return Sensor[value]


@click.group()
@click.version_option()
def cli():
    """Get the temperature from your connected w1 therm sensors

    \b
    Available sensors types are:
      - DS18S20
      - DS1822
      - DS18B20
      - DS28EA00
      - DS1825/MAX31850K
    """
    pass


@cli.command()
@click.option(
    "-t",
    "--type",
    "types",
    multiple=True,
    type=click.Choice([s.name for s in Sensor]),
    callback=resolve_type_name,
    help="Show only sensor of this type",
)
@click.option(
    "-j", "--json", "as_json", flag_value=True, help="Output result in JSON format"
)
@click.option(
    "-r",
    "--resolution",
    "resolution",
    is_flag=True,
    help="also display resolution for each sensor",
)
def ls(types, as_json, resolution):  # pylint: disable=invalid-name
    """List all available sensors"""
    sensors = W1ThermSensor.get_available_sensors(types)

    if as_json:
        if resolution:
            data = [
                {
                    "id": i,
                    "hwid": s.id,
                    "type": s.name,
                    "resolution": s.get_resolution(),
                }
                for i, s in enumerate(sensors, 1)
            ]
        else:
            data = [
                {"id": i, "hwid": s.id, "type": s.name}
                for i, s in enumerate(sensors, 1)
            ]
        click.echo(json.dumps(data, indent=4, sort_keys=True))
    else:
        click.echo(
            "Found {0} sensors:".format(click.style(str(len(sensors)), bold=True))
        )
        for i, sensor in enumerate(sensors, 1):
            if resolution:
                click.echo(
                    "  {0}. HWID: {1} Type: {2} Resolution: {3}".format(
                        click.style(str(i), bold=True),
                        click.style(sensor.id, bold=True),
                        click.style(sensor.name, bold=True),
                        click.style(str(sensor.get_resolution()), bold=True),
                    )
                )
            else:
                click.echo(
                    "  {0}. HWID: {1} Type: {2}".format(
                        click.style(str(i), bold=True),
                        click.style(sensor.id, bold=True),
                        click.style(sensor.name, bold=True),
                    )
                )


@cli.command()
@click.option(
    "-t",
    "--type",
    "types",
    multiple=True,
    type=click.Choice([s.name for s in Sensor]),
    callback=resolve_type_name,
    help="Show only sensor of this type",
)
@click.option(
    "-u",
    "--unit",
    default="celsius",
    type=click.Choice([u.value for u in Unit]),
    help="The unit of the temperature. Defaults to Celsius",
)
@click.option(
    "-r",
    "--resolution",
    type=click.IntRange(9, 12),
    help="use the given resolution for this read",
)
@click.option(
    "-j", "--json", "as_json", flag_value=True, help="Output result in JSON format"
)
def all(types, unit, resolution, as_json):  # pylint: disable=redefined-builtin
    """Get temperatures of all available sensors"""
    sensors = W1ThermSensor.get_available_sensors(types)
    temperatures = []
    for sensor in sensors:
        if resolution:
            sensor.set_resolution(resolution, persist=False)

        temperatures.append(sensor.get_temperature(unit))

    if as_json:
        data = [
            {"id": i, "hwid": s.id, "type": s.name, "temperature": t, "unit": unit}
            for i, s, t in zip(count(start=1), sensors, temperatures)
        ]
        click.echo(json.dumps(data, indent=4, sort_keys=True))
    else:
        click.echo(
            "Got temperatures of {0} sensors:".format(
                click.style(str(len(sensors)), bold=True)
            )
        )
        for i, sensor, temperature in zip(count(start=1), sensors, temperatures):
            click.echo(
                "  Sensor {0} ({1}) measured temperature: {2} {3}".format(
                    click.style(str(i), bold=True),
                    click.style(sensor.id, bold=True),
                    click.style(str(round(temperature, 2)), bold=True),
                    click.style(unit, bold=True),
                )
            )


@cli.command()
@click.argument("id_", metavar="id", required=False, type=click.INT)
@click.option("-h", "--hwid", help="The hardware id of the sensor")
@click.option(
    "-t",
    "--type",
    "type_",
    type=click.Choice([s.name for s in Sensor]),
    callback=resolve_type_name,
    help="The type of the sensor",
)
@click.option(
    "-u",
    "--unit",
    default="celsius",
    type=click.Choice([u.value for u in Unit]),
    help="The unit of the temperature. Defaults to Celsius",
)
@click.option(
    "-r",
    "--resolution",
    type=click.IntRange(9, 12),
    help="use the given resolution for this read",
)
@click.option(
    "-j", "--json", "as_json", flag_value=True, help="Output result in JSON format"
)
@click.option(
    "-o",
    "--offset",
    default=0.0,
    type=click.FLOAT,
    help="Offset the temperature reading by the given offset temperature.",
)
def get(id_, hwid, type_, unit, resolution, as_json, offset):
    """Get temperature of a specific sensor"""
    if id_ and (hwid or type_):
        raise click.BadArgumentUsage(
            "If --id is given --hwid and --type are not allowed."
        )

    if id_:
        try:
            sensor = W1ThermSensor.get_available_sensors()[id_ - 1]
        except IndexError:
            error_msg = (
                "No sensor with id {0} available. ".format(id_)
                + "Use the ls command to show all available sensors."
            )
            if CLICK_MAJOR_VERSION >= 7:  # pragma: no cover
                raise click.BadOptionUsage("--id", error_msg)
            else:  # pragma: no cover
                raise click.BadOptionUsage(error_msg)
    else:
        sensor = W1ThermSensor(type_, hwid)

    if resolution:
        sensor.set_resolution(resolution, persist=False)

    if offset:
        sensor.set_offset(offset, unit)

    temperature = sensor.get_temperature(unit)

    if as_json:
        data = {
            "hwid": sensor.id,
            "offset": offset,
            "type": sensor.name,
            "temperature": temperature,
            "unit": unit,
        }
        click.echo(json.dumps(data, indent=4, sort_keys=True))
    else:
        click.echo(
            "Sensor {0} measured temperature: {1} {2}".format(
                click.style(sensor.id, bold=True),
                click.style(str(temperature), bold=True),
                click.style(unit, bold=True),
            )
        )


@cli.command()
@click.argument("resolution", required=True, type=click.IntRange(9, 12))
@click.argument("id_", metavar="id", required=False, type=click.INT)
@click.option("-h", "--hwid", help="The hardware id of the sensor")
@click.option(
    "-t",
    "--type",
    "type_",
    type=click.Choice([s.name for s in Sensor]),
    callback=resolve_type_name,
    help="The type of the sensor",
)
def resolution(resolution, id_, hwid, type_):
    """Change the resolution for the sensor and persist it in the sensor's EEPROM"""
    if id_ and (hwid or type_):
        raise click.BadArgumentUsage(
            "If --id is given --hwid and --type are not allowed."
        )

    if id_:
        try:
            sensor = W1ThermSensor.get_available_sensors()[id_ - 1]
        except IndexError:
            error_msg = (
                "No sensor with id {0} available. ".format(id_)
                + "Use the ls command to show all available sensors."
            )
            if CLICK_MAJOR_VERSION >= 7:  # pragma: no cover
                raise click.BadOptionUsage("--id", error_msg)
            else:  # pragma: no cover
                raise click.BadOptionUsage(error_msg)
    else:
        sensor = W1ThermSensor(type_, hwid)

    sensor.set_resolution(resolution, persist=True)
