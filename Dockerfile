FROM jsurf/rpi-raspbian
MAINTAINER Timo Furrer <tuxtimo@gmail.com>

ENV QEMU_EXECVE 1
ENV DEBIAN_FRONTEND noninteractive

# update the raspbian
RUN apt-get update && apt-get upgrade --yes

# install debian toolchain
RUN apt-get install --yes --no-install-recommends devscripts equivs build-essential wget

# install unavailable build dependencies from stretch
RUN mkdir /build-deps
WORKDIR /build-deps
RUN wget http://ftp.ch.debian.org/debian/pool/main/p/pytest-mock/python-pytest-mock_1.3.0-1_all.deb
RUN wget http://ftp.ch.debian.org/debian/pool/main/p/pytest-mock/python3-pytest-mock_1.3.0-1_all.deb
RUN dpkg -i python-pytest-mock_1.3.0-1_all.deb python3-pytest-mock_1.3.0-1_all.deb || true
RUN apt-get install --yes -f
RUN rm -rf /build-deps

# add jessie backports for click
RUN echo 'deb ftp://ftp.ch.debian.org/debian jessie-backports main contrib non-free' > /etc/apt/sources.list.d/backports.list
RUN gpg --keyserver pgpkeys.mit.edu --recv-key 8B48AD6246925553 && gpg -a --export 8B48AD6246925553 | apt-key add -
RUN apt-get update

# add current source
VOLUME ["/src"]
WORKDIR /src
