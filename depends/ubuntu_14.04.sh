#!/bin/sh

#
# Installs all of the dependencies for Pillow for Ubuntu 14.04
# for both system Pythons 2.7 and 3.4
#

sudo apt-get -y install python-dev python-setuptools \
    python3-dev python-virtualenv cmake
sudo apt-get -y install libtiff5-dev libjpeg8-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev \
    python-tk python3-tk

./install_openjpeg.sh
