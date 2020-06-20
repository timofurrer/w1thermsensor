import functools
import re
from pathlib import Path

from setuptools import find_packages, setup

#: Holds a list of packages to install with the binary distribution
PACKAGES = find_packages(where="src")
META_FILE = Path("src").absolute() / "w1thermsensor" / "__init__.py"
KEYWORDS = ["w1", "w1-therm", "therm", "sensor", "raspberry", "raspberry pi", "gpio", "ds"]
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: Implementation",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

#: Holds the runtime requirements for the end user
INSTALL_REQUIRES = ["click"]
#: Holds runtime requirements and development requirements
EXTRAS_REQUIRES = {}

EXTRAS_REQUIRES["async"] = ["aiofiles"]
EXTRAS_REQUIRES["tests"] = EXTRAS_REQUIRES["async"] + ["coverage[toml]>=5.0.2", "pytest>5", "pytest-mock", "pytest-asyncio"]
EXTRAS_REQUIRES["dev"] = (
    EXTRAS_REQUIRES["tests"] + ["flake8", "black", "check-manifest", "towncrier"]
)

#: Holds the contents of the README file
with open("README.md", encoding="utf-8") as readme:
    __README_CONTENTS__ = readme.read()


@functools.lru_cache()
def read(metafile):
    """
    Return the contents of the given meta data file assuming UTF-8 encoding.
    """
    with metafile.open(encoding="utf-8") as f:
        return f.read()


def get_meta(meta, metafile):
    """
    Extract __*meta*__ from the given metafile.
    """
    contents = read(metafile)
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta), contents, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


setup(
    name="w1thermsensor",
    version=get_meta("version", META_FILE),
    license=get_meta("license", META_FILE),
    description=get_meta("description", META_FILE),
    long_description=__README_CONTENTS__,
    long_description_content_type="text/markdown",
    author=get_meta("author", META_FILE),
    author_email=get_meta("author_email", META_FILE),
    maintainer=get_meta("author", META_FILE),
    maintainer_email=get_meta("author_email", META_FILE),
    platforms=["Linux"],
    url=get_meta("url", META_FILE),
    download_url=get_meta("download_url", META_FILE),
    packages=PACKAGES,
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.5.*",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRES,
    entry_points={
        "console_scripts": ["w1thermsensor = w1thermsensor.cli:cli"]
    },
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
)
