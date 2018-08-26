# -*- coding: utf-8 -*-

import io
import os
import sys
import codecs
from shutil import rmtree

from setuptools import find_packages, setup, Command


here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()


if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel upload")
    sys.exit()

required = ["click"]


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPi via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(about["__version__"]))
        os.system("git push --tags")

        sys.exit()


# About dict to store version and package info
about = dict()
with codecs.open(
    os.path.join(here, "w1thermsensor", "__version__.py"), "r", encoding="utf-8"
) as f:
    exec(f.read(), about)


setup_args = dict(
    name="w1thermsensor",
    version=about["__version__"],
    license="MIT",
    description="This little pure python module provides a single class to get the temperature of a w1 sensor",
    long_description=long_description,
    author="Timo Furrer",
    author_email="tuxtimo@gmail.com",
    maintainer="Timo Furrer",
    maintainer_email="tuxtimo@gmail.com",
    platforms=["Linux"],
    url="http://github.com/timofurrer/w1thermsensor",
    download_url="http://github.com/timofurrer/w1thermsensor",
    packages=find_packages(exclude=["*tests*"]),
    install_requires=required,
    include_package_data=True,
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ),
    cmdclass={"upload": UploadCommand},
)

if sys.version_info.major == 3:
    setup_args["entry_points"] = {
        "console_scripts": ["w1thermsensor = w1thermsensor.cli:cli"]
    }

setup(**setup_args)
