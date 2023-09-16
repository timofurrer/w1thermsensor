"""
w1thermsensor
~~~~~~~~~~~~~

A Python package and CLI tool to work with w1 temperature sensors.

:copyright: (c) 2023 by Brett Lounsbury
:license: MIT, see LICENSE for more details.
"""

import pytest

from w1thermsensor.calibration_data import CalibrationData
from w1thermsensor.errors import InvalidCalibrationDataError


@pytest.mark.parametrize(
    "measured_high, measured_low, reference_high, reference_low",
    [
        (None, 0.0, 100.0, 0.0),  # None is not allowed for measured_high
        (100.0, None, 100.0, 0.0),  # None is not allowed for measured_low
        (100.0, 0.0, None, 0.0),  # None is not allowed for reference_high
        (100.0, 0.0, 100.0, None),  # None is not allowed for reference_low
        (0, 100.0, 100.0, 0.0),  # measured_low > measured_high
        (100.0, 0.0, 0.0, 100.0),  # reference_low > reference_high
        (100.0, 100.0, 100.0, 0.0),  # measured_low = measured_high
        (100.0, 0.0, 100.0, 100.0),  # reference_low = reference_high
    ],
)
def test_init_raises_error_on_invalid_input(
    measured_high, measured_low, reference_high, reference_low
):
    with pytest.raises(InvalidCalibrationDataError):
        CalibrationData(
            measured_high_point=measured_high,
            measured_low_point=measured_low,
            reference_high_point=reference_high,
            reference_low_point=reference_low,
        )


@pytest.mark.parametrize(
    "measured_high, measured_low, reference_high, reference_low, correction_function",
    [
        (100.0, 0.0, 100.0, 0.0, lambda x: x),  # Sensor is perfectly calibrated
        (100.0, 1.0, 99.0, 0.0, lambda x: x - 1.0),  # Sensor is 1.0 degree high
        (102.75, 2.75, 100.0, 0.0, lambda x: x - 2.75),  # Sensor is 2.75 degrees high
        (98.0, -1.0, 99.0, 0.0, lambda x: x + 1.0),  # Sensor is 1.0 degrees low
        (97.25, -2.75, 100.0, 0.0, lambda x: x + 2.75),  # Sensor is 2.75 degrees low
        # Sensor is wonky - 1 degree low at the high end, 1 degree high on the low end
        (99.0, 1.0, 100.0, 0.0, lambda x: (x - 1.0) * 100.0 / 98.0),
    ],
)
def test_temperature_correction(
    measured_high, measured_low, reference_high, reference_low, correction_function
):
    calibration_data = CalibrationData(
        measured_high_point=measured_high,
        measured_low_point=measured_low,
        reference_high_point=reference_high,
        reference_low_point=reference_low,
    )

    for i in range(-270, 1800):
        raw_temp = float(i)
        # Floating point math is not exact, so round to 4 digits
        # 4 digits is the accuracy limit of the sensors supported by this library
        expected = correction_function(raw_temp)
        actual = calibration_data.correct_temperature_for_calibration_data(raw_temp)
        assert actual == pytest.approx(expected)
