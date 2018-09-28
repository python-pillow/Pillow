#!/bin/bash

set -e

sudo apt-get update
sudo apt-get -qq install libfreetype6-dev liblcms2-dev python-tk\
			 python-qt4 ghostscript libffi-dev libjpeg-turbo-progs cmake imagemagick\
             libharfbuzz-dev libfribidi-dev

PYTHONOPTIMIZE=0 pip install cffi
pip install check-manifest
pip install coverage
pip install olefile
pip install -U pytest
pip install -U pytest-cov
pip install pyroma
pip install test-image-results
pip install numpy

# docs only on Python 2.7
if [ "$TRAVIS_PYTHON_VERSION" == "2.7" ]; then pip install -r requirements.txt ; fi

# clean checkout for manifest
mkdir /tmp/check-manifest && cp -a . /tmp/check-manifest

# webp
pushd depends && ./install_webp.sh && popd

# openjpeg
pushd depends && ./install_openjpeg.sh && popd

# libimagequant
pushd depends && ./install_imagequant.sh && popd

# extra test images
pushd depends && ./install_extra_test_images.sh && popd

