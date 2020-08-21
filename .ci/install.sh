#!/bin/bash

aptget_update()
{
    if [ ! -z $1 ]; then
        echo ""
        echo "Retrying apt-get update..."
        echo ""
    fi
    output=`sudo apt-get update 2>&1`
    echo "$output"
    if [[ $output == *[WE]:\ * ]]; then
        return 1
    fi
}
aptget_update || aptget_update retry || aptget_update retry

set -e

sudo apt-get -qq install libfreetype6-dev liblcms2-dev python3-tk\
                         ghostscript libffi-dev libjpeg-turbo-progs libopenjp2-7-dev\
                         cmake imagemagick libharfbuzz-dev libfribidi-dev

pip install --upgrade pip
PYTHONOPTIMIZE=0 pip install cffi
pip install coverage
pip install olefile
pip install -U pytest
pip install -U pytest-cov
pip install pyroma
pip install test-image-results
pip install numpy

# TODO Remove when 3.9-dev includes setuptools 49.3.2+:
if [ "$GHA_PYTHON_VERSION" == "3.9-dev" ]; then pip install -U "setuptools>=49.3.2" ; fi

if [[ $TRAVIS_PYTHON_VERSION == 3.* ]]; then
  # arm64, ppc64le, s390x CPUs:
  # "ERROR: Could not find a version that satisfies the requirement pyqt5"
  if [[ $TRAVIS_CPU_ARCH == "amd64" ]]; then
    sudo apt-get -qq install libxcb-xinerama0 pyqt5-dev-tools
    pip install pyqt5
  fi
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
