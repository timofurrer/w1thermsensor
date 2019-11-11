# -*- coding: utf-8 -*-

"""
This module provides exceptions for the w1thermsensor.
"""

import textwrap


class W1ThermSensorError(Exception):
    """Exception base-class for W1ThermSensor errors"""

    pass


class KernelModuleLoadError(W1ThermSensorError):
    """Exception when the w1 therm kernel modules could not be loaded properly"""

    def __init__(self):
        super(KernelModuleLoadError, self).__init__(
            "Cannot load w1 therm kernel modules"
        )


class NoSensorFoundError(W1ThermSensorError):
    """Exception when no sensor is found"""

    def __init__(self, message):
        super(NoSensorFoundError, self).__init__(
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
        super(SensorNotReadyError, self).__init__(
            "Sensor {} is not yet ready to read temperature".format(sensor.id)
        )
        self.sensor = sensor


class UnsupportedUnitError(W1ThermSensorError):
    """Exception when unsupported unit is given"""

    def __init__(self):
        super(UnsupportedUnitError, self).__init__(
            "Only Degrees C, F and Kelvin are currently supported"
        )


class ResetValueError(W1ThermSensorError):
    """Exception when the reset value is yield from the hardware"""

    def __init__(self, sensor):
        super(ResetValueError, self).__init__(
            "Sensor {} yields the reset value of 85 degree millicelsius. "
            "Please check the hardware.".format(sensor.id)
        )
        self.sensor = sensor
