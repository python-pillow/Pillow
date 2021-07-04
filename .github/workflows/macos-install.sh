#!/bin/bash

set -e

brew install libtiff libjpeg openjpeg libimagequant webp little-cms2 freetype openblas libraqm

PYTHONOPTIMIZE=0 python3 -m pip install cffi
python3 -m pip install coverage
python3 -m pip install defusedxml
python3 -m pip install olefile
python3 -m pip install -U pytest
python3 -m pip install -U pytest-cov
python3 -m pip install -U pytest-timeout
python3 -m pip install pyroma
python3 -m pip install test-image-results

echo -e "[openblas]\nlibraries = openblas\nlibrary_dirs = /usr/local/opt/openblas/lib" >> ~/.numpy-site.cfg
# TODO Remove condition when numpy supports 3.10
if ! [ "$GHA_PYTHON_VERSION" == "3.10-dev" ]; then python3 -m pip install numpy ; fi

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
