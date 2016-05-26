#!/bin/sh

#
# Installs all of the dependencies for Pillow for Ubuntu 12.04
# for both system Pythons 2.7 and 3.2
#

sudo apt-get -y install python-dev python-setuptools \
    python3-dev python-virtualenv cmake
sudo apt-get install libtiff4-dev libjpeg8-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev tcl8.5-dev \
    tk8.5-dev python-tk python3-tk


./install_openjpeg.sh
./install_webp.sh
./install_imagequant.sh
