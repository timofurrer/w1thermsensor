#!/bin/sh

set -e
set -x

mk-build-deps -r -i -t 'apt-get --yes --no-install-recommends'
# build debian package
debuild -us -uc -b
# install built debian packages
dpkg -i ../*.deb

# copy results in output directory
rm -rf deb/
mkdir deb/
mv ../*.deb deb/

# clean build files
dh_clean
rm -rf .pybuild w1thermsensor.egg-info
