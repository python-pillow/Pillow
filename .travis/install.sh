#!/bin/bash

set -e

sudo apt-get update
sudo apt-get -qq install libfreetype6-dev liblcms2-dev python-tk\
			 python-qt4 ghostscript libffi-dev libjpeg-turbo-progs cmake imagemagick\
             libharfbuzz-dev libfribidi-dev

pip install cffi
pip install nose
pip install check-manifest
pip install olefile
pip install pyroma
pip install coverage

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

