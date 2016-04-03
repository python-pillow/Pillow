#!/bin/sh

#
# Installs all of the dependencies for Pillow for Debian 8.2
# for both system Pythons 2.7 and 3.4
#
# Also works for Raspbian Jessie
#

sudo apt-get -y install python-dev python-setuptools \
    python3-dev python-virtualenv cmake
sudo apt-get -y install libtiff5-dev libjpeg62-turbo-dev zlib1g-dev \
     libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev \
     python-tk python3-tk

./install_openjpeg.sh
