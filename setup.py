#!/usr/bin/python
# -*- coding: utf-8 -*-

from imp import load_source
from distutils.core import setup

version = load_source("version", "ds18b20/__init__.py")

setup(
    name="ds18b20",
    version=version.__version__,
    license="MIT",
    description="This little pure python module provides a single class to get the temperature of a DS18B20 sensor",
    author="Timo Furrer",
    author_email="tuxtimo@gmail.com",
    maintainer="Timo Furrer",
    maintainer_email="tuxtimo@gmail.com",
    platforms=["Linux"],
    url="http://github.com/timofurrer/ds18b20",
    download_url="http://github.com/timofurrer/ds18b20",
    packages=["ds18b20"]
)
