"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2020 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import textwrap


class W1ThermSensorError(Exception):
    """Exception base-class for W1ThermSensor errors"""

    pass


class KernelModuleLoadError(W1ThermSensorError):
    """Exception when the w1 therm kernel modules could not be loaded properly"""

    def __init__(self):
        super().__init__("Cannot load w1 therm kernel modules")


class NoSensorFoundError(W1ThermSensorError):
    """Exception when no sensor is found"""

    def __init__(self, message):
        super().__init__(
            textwrap.dedent(
                """
            {}
            Please check cabling and check your /boot/config.txt for
            dtoverlay=w1-gpio
            """.format(
                    message
                )
            ).rstrip()
        )


class SensorNotReadyError(W1ThermSensorError):
    """Exception when the sensor is not ready yet"""

    def __init__(self, sensor):
        super().__init__(
            "Sensor {} is not yet ready to read temperature".format(sensor.id)
        )
        self.sensor = sensor


class UnsupportedUnitError(W1ThermSensorError):
    """Exception when unsupported unit is given"""

    def __init__(self):
        super().__init__("Only Degrees C, F and Kelvin are currently supported")


class UnsupportedSensorError(W1ThermSensorError):
    """Exception when unsupported sensor is given"""

    def __init__(self, sensor_name, supported_sensors):
        super().__init__("The sensor {} is not supported. Use one of: {}".format(
            sensor_name, ", ".join(supported_sensors)))


class ResetValueError(W1ThermSensorError):
    """Exception when the reset value is yield from the hardware"""

    def __init__(self, sensor_id):
        super().__init__(
            "Sensor {} yields the reset value of 85 degree millicelsius. "
            "Please check the power-supply for the sensor.".format(sensor_id)
        )
