# -*- coding: utf-8 -*-

import sys
from imp import load_source
from setuptools import setup

core = load_source("core", "w1thermsensor/__init__.py")

setup_args=dict(
    name="w1thermsensor",
    version=core.__version__,
    license="MIT",
    description="This little pure python module provides a single class to get the temperature of a w1 sensor",
    author=core.__author__,
    author_email=core.__email__,
    maintainer=core.__author__,
    maintainer_email=core.__email__,
    platforms=["Linux"],
    url="http://github.com/timofurrer/w1thermsensor",
    download_url="http://github.com/timofurrer/w1thermsensor",
    packages=["w1thermsensor"],
    install_requires=["click"],
)

if sys.version_info.major == 3:
    setup_args["entry_points"] = {"console_scripts": ["w1thermsensor = w1thermsensor.cli:cli"]}

setup(**setup_args)
