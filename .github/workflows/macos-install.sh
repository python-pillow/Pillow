#!/bin/bash

set -e

brew install libtiff libjpeg openjpeg libimagequant webp little-cms2 freetype libraqm
export PKG_CONFIG_PATH="/usr/local/opt/openblas/lib/pkgconfig"

PYTHONOPTIMIZE=0 python3 -m pip install cffi
python3 -m pip install coverage
python3 -m pip install defusedxml
python3 -m pip install olefile
python3 -m pip install -U pytest
python3 -m pip install -U pytest-cov
python3 -m pip install -U pytest-timeout
python3 -m pip install pyroma

python3 -m pip install numpy

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
