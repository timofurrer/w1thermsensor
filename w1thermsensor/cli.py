# -*- coding: utf-8 -*-

"""
    Command Line Interface to get sensor data
"""

import json
from itertools import count

import click

from .core import W1ThermSensor


def resolve_type_name(ctx, param, value):  # pylint: disable=unused-argument
    """Resolve CLI option type name"""
    def _resolve(value):
        """Resolve single type name"""
        value = [type_id for type_id, type_name in W1ThermSensor.TYPE_NAMES.items()
                 if type_name == value][0]
        return value

    if not value:
        return value

    if isinstance(value, tuple):
        return [_resolve(v) for v in value]
    else:
        return _resolve(value)


@click.group()
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
@click.option("-t", "--type", "types", multiple=True,
              type=click.Choice(W1ThermSensor.TYPE_NAMES.values()),
              callback=resolve_type_name,
              help="Show only sensor of this type")
@click.option("-j", "--json", "as_json", flag_value=True,
              help="Output result in JSON format")
def ls(types, as_json):  # pylint: disable=invalid-name
    """List all available sensors"""
    sensors = W1ThermSensor.get_available_sensors(types)

    if as_json:
        data = [{"id": i, "hwid": s.id, "type": s.type_name} for i, s in enumerate(sensors, 1)]
        click.echo(json.dumps(data, indent=4, sort_keys=True))
    else:
        click.echo("Found {0} sensors:".format(click.style(str(len(sensors)), bold=True)))
        for i, sensor in enumerate(sensors, 1):
            click.echo("  {0}. HWID: {1} Type: {2}".format(
                click.style(str(i), bold=True),
                click.style(sensor.id, bold=True),
                click.style(sensor.type_name, bold=True)
            ))


@cli.command()
@click.option("-t", "--type", "types", multiple=True,
              type=click.Choice(W1ThermSensor.TYPE_NAMES.values()),
              callback=resolve_type_name,
              help="Show only sensor of this type")
@click.option("-u", "--unit", default="celsius",
              type=click.Choice(W1ThermSensor.UNIT_FACTOR_NAMES),
              help="The unit of the temperature. Defaults to Celsius")
@click.option("-p", "--precision", type=click.IntRange(9, 12),
              help="use the given precision for this read")
@click.option("-j", "--json", "as_json", flag_value=True,
              help="Output result in JSON format")
def all(types, unit, precision, as_json):  # pylint: disable=redefined-builtin
    """Get temperatures of all available sensors"""
    sensors = W1ThermSensor.get_available_sensors(types)
    temperatures = []
    for sensor in sensors:
        if precision:
            sensor.set_precision(precision, persist=False)

        temperatures.append(sensor.get_temperature(unit))

    if as_json:
        data = [{
            "id": i,
            "hwid": s.id,
            "type": s.type_name,
            "temperature": t,
            "unit": unit
        } for i, s, t in zip(count(start=1), sensors, temperatures)]
        click.echo(json.dumps(data, indent=4, sort_keys=True))
    else:
        click.echo("Got temperatures of {0} sensors:".format(
            click.style(str(len(sensors)), bold=True)))
        for i, sensor, temperature in zip(count(start=1), sensors, temperatures):
            click.echo("  Sensor {0} ({1}) measured temperature: {2} {3}".format(
                click.style(str(i), bold=True),
                click.style(sensor.id, bold=True),
                click.style(str(round(temperature, 2)), bold=True),
                click.style(unit, bold=True)
            ))


@cli.command()
@click.argument("id_", metavar="id", required=False, type=click.INT)
@click.option("-h", "--hwid",
              help="The hardware id of the sensor")
@click.option("-t", "--type", "type_",
              type=click.Choice(W1ThermSensor.TYPE_NAMES.values()),
              callback=resolve_type_name,
              help="The type of the sensor")
@click.option("-u", "--unit", default="celsius",
              type=click.Choice(W1ThermSensor.UNIT_FACTOR_NAMES),
              help="The unit of the temperature. Defaults to Celsius")
@click.option("-p", "--precision", type=click.IntRange(9, 12),
              help="use the given precision for this read")
@click.option("-j", "--json", "as_json", flag_value=True,
              help="Output result in JSON format")
def get(id_, hwid, type_, unit, precision, as_json):
    """Get temperature of a specific sensor"""
    if id_ and (hwid or type_):
        raise click.BadOptionUsage("If --id is given --hwid and --type are not allowed.")

    if id_:
        try:
            sensor = W1ThermSensor.get_available_sensors()[id_ - 1]
        except IndexError:
            raise click.BadOptionUsage(
                "No sensor with id {0} available. "
                "Use the ls command to show all available sensors.".format(id_))
    else:
        sensor = W1ThermSensor(type_, hwid)

    if precision:
        sensor.set_precision(precision, persist=False)

    temperature = sensor.get_temperature(unit)

    if as_json:
        data = {
            "hwid": sensor.id, "type": sensor.type_name,
            "temperature": temperature, "unit": unit
        }
        click.echo(json.dumps(data, indent=4, sort_keys=True))
    else:
        click.echo("Sensor {0} measured temperature: {1} {2}".format(
            click.style(sensor.id, bold=True),
            click.style(str(temperature), bold=True),
            click.style(unit, bold=True)
        ))


@cli.command()
@click.argument("precision", required=True, type=click.IntRange(9, 12))
@click.argument("id_", metavar="id", required=False, type=click.INT)
@click.option("-h", "--hwid",
              help="The hardware id of the sensor")
@click.option("-t", "--type", "type_",
              type=click.Choice(W1ThermSensor.TYPE_NAMES.values()),
              callback=resolve_type_name,
              help="The type of the sensor")
def precision(precision, id_, hwid, type_):
    """Change the precision for the sensor and persist it in the sensor's EEPROM"""
    if id_ and (hwid or type_):
        raise click.BadOptionUsage("If --id is given --hwid and --type are not allowed.")

    if id_:
        try:
            sensor = W1ThermSensor.get_available_sensors()[id_ - 1]
        except IndexError:
            raise click.BadOptionUsage(
                "No sensor with id {0} available. "
                "Use the ls command to show all available sensors.".format(id_))
    else:
        sensor = W1ThermSensor(type_, hwid)

    sensor.set_precision(precision, persist=True)
