"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2023 by Brett Lounsbury
:license: MIT, see LICENSE for more details.
"""

from dataclasses import dataclass

from w1thermsensor.errors import InvalidCalibrationDataError


@dataclass(frozen=True)
class CalibrationData:
    """
    This Class represents the data required for calibrating a temperature sensor and houses the
    logic to correct the temperature sensor's raw readings based on the calibration data.

    The method used for this class requires that you collect temperature readings of the low point
    and high point of water in your location with your sensor (this method obviously requires a
    waterproof sensor).

    To gather the low point: Take a large cup and fill it completely with ice and then add water.
    Submerse your temperature sensor ensuring it does not touch the cup.  Wait 2 minutes, and then
    begin polling the temperature sensor.  Once the temperature stabilizes and stays around the
    same value for 30 seconds, record this as your measured_low_point.

    To gather the high point: Bring a pot of water to a rapid boil.  Submerse your temperature
    sensor ensuring it
    does not touch the pot.   Begin polling the sensor.  Once the temperature stabilizes and
    stays around the same
    value for 30 seconds, record this as your measured_high_point.

    To gather the reference high point: The high point changes significantly with air pressure
    (and therefore altitude).  The easiest way to get the reference data for the high point is to
    find out the   elevation of your location and then find the high point at that elevation.
    This is not perfectly accurate, but it is generally close enough for most use cases.
    You can find this data here:
    https://www.engineeringtoolbox.com/high-points-water-altitude-d_1344.html

    To gather the reference low point: The low point of water does not change significantly with
    altitude like the high point does because it does not involve a gas (water vapor) and therefore
    air pressure is not as big of a factor.  Generally speaking the default value of 0.0 is
    accurate enough.

    You MUST provide the measured_low_point, measured_high_point, and reference_high_point in
    Celsius.

    This class is based on:
    https://www.instructables.com/Calibration-of-DS18B20-Sensor-With-Arduino-UNO/
    """

    measured_high_point: float
    measured_low_point: float
    reference_high_point: float
    reference_low_point: float = 0.0

    def __post_init__(self):
        """
        Validates that the required arguments are set and sanity check that the high points are
        higher than the associated low points.  This method does not sanity check that values make
        sense for high/low point outside of high_point > low_point.
        """

        if self.measured_high_point is None:
            raise InvalidCalibrationDataError(
                "Measured high point must be provided.", self.__str__()
            )

        if self.measured_low_point is None:
            raise InvalidCalibrationDataError(
                "Measured low point must be provided.", self.__str__()
            )

        if self.reference_high_point is None:
            raise InvalidCalibrationDataError(
                "Reference high point must be provided.", self.__str__()
            )

        if self.reference_low_point is None:
            raise InvalidCalibrationDataError(
                "Reference low point must not set to None.", self.__str__()
            )

        if self.measured_low_point >= self.measured_high_point:
            raise InvalidCalibrationDataError(
                "Measured low point must be less than measured high point. Did you reverse the " +
                "values?",
                self.__str__(),
            )

        if self.reference_low_point >= self.reference_high_point:
            raise InvalidCalibrationDataError(
                "Reference low point must be less than reference high point.  Did you reverse " +
                "the values?",
                self.__str__(),
            )

    def correct_temperature_for_calibration_data(self, raw_temperature):
        """
        Correct the temperature based on the calibration data provided.  This is done by taking
        the raw temperature reading and subtracting out the measured low point, scaling that by the
        scaling factor, and then adding back the reference low point.
        """
        reference_range = self.reference_high_point - self.reference_low_point
        measured_range = self.measured_high_point - self.measured_low_point
        scaling_factor = reference_range / measured_range
        return ((raw_temperature - self.measured_low_point) * scaling_factor
                + self.reference_low_point)
