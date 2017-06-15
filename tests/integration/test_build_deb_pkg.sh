#!/bin/sh

set -e
set -x

mk-build-deps -r -i -t 'apt-get --yes --no-install-recommends'
# build debian package
debuild -us -uc -b
# install built debian packages
dpkg -i ../*.deb

# check if w1thermsensor module is importable in Python 2 and Python 3
W1THERMSENSOR_NO_KERNEL_MODULE=1 python -c 'import w1thermsensor'
W1THERMSENSOR_NO_KERNEL_MODULE=1 python3 -c 'import w1thermsensor'

# check if CLI tool can be called
W1THERMSENSOR_NO_KERNEL_MODULE=1 w1thermsensor --version

# copy results in output directory
rm -rf deb/
mkdir deb/
mv ../*.deb deb/

# clean build files
dh_clean
rm -rf .pybuild w1thermsensor.egg-info
