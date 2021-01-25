w1thermsensor 2.0.0 (2021-01-25)
================================

Features
--------

- Refacor Sensor and Unit out of W1ThermSensor class.

  The Sensors are available in the `Sensor` enum:

  .. code-block:: python

      from w1thermsensor import Sensor

      print(Sensor.DS18B20)


  The Units are available in the `Unit` enum:

  .. code-block:: python

      from w1thermsensor import Unit

      print(Unit.DEGREES_F) (#0)

- Add ``AsyncW1ThermSensor`` class to support asyncio interfaces. (#52)

- added option to display resolution in cli ls command. (#86)


Deprecations and Removals
-------------------------

- Drop Python 2 and Python 3.4 support. (#58)

- Replace precision with resolution - in CLI and Python API. (#74)
