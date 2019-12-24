#!/bin/bash

set -e

sudo apt-get update
sudo apt-get -qq install libfreetype6-dev liblcms2-dev python3-tk\
                         ghostscript libffi-dev libjpeg-turbo-progs libopenjp2-7-dev\
                         cmake imagemagick libharfbuzz-dev libfribidi-dev

PYTHONOPTIMIZE=0 pip install cffi
pip install coverage
pip install olefile
pip install -U pytest
pip install -U pytest-cov
pip install pyroma
pip install test-image-results
pip install numpy
if [[ $TRAVIS_PYTHON_VERSION == 3.* ]]; then
    sudo apt-get -qq install pyqt5-dev-tools
    pip install pyqt5
fi

# docs only on Python 3.8
if [ "$TRAVIS_PYTHON_VERSION" == "3.8" ]; then pip install -r requirements.txt ; fi

# webp
pushd depends && ./install_webp.sh && popd

# libimagequant
pushd depends && ./install_imagequant.sh && popd

# raqm
pushd depends && ./install_raqm.sh && popd

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
