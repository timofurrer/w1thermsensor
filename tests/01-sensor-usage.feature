Feature: Basic Usage
    Scenario Outline: One Sensor (implicit)
        Given the temperature for sensor <sensoridx> is 25.0 C
        Then I expect the temperature for sensor <sensoridx> to return 25.0 C
            and I expect the temperature for sensor <sensoridx> to return 77.0 F
            and I expect the temperature for sensor <sensoridx> to return 298.15 K

        When the temperature for sensor <sensoridx> is increased by 5.51 C
        Then I expect the temperature for sensor <sensoridx> to return 30.51 C
            and I expect the temperature for sensor <sensoridx> to return 86.918 F
            and I expect the temperature for sensor <sensoridx> to return 303.66 K

    Examples:
        | sensoridx |
        | 1        |
        | 2        |
        | 3        |

    Scenario Outline: One Sensor (explicit)
        Given the temperature for sensor <sensorid> is 25.0 C
        Then I expect the temperature for sensor <sensorid> to return 25.0 C
            and I expect the temperature for sensor <sensorid> to return 77.0 F
            and I expect the temperature for sensor <sensorid> to return 298.15 K

        When the temperature for sensor <sensorid> is increased by 5.51 C
        Then I expect the temperature for sensor <sensorid> to return 30.51 C
            and I expect the temperature for sensor <sensorid> to return 86.918 F
            and I expect the temperature for sensor <sensorid> to return 303.66 K

    Examples:
        | sensorid    |
        | 00000000001 |
        | 00000000002 |
        | 00000000003 |
