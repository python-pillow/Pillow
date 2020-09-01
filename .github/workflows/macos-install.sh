#!/bin/bash

set -e

brew install libtiff libjpeg openjpeg libimagequant webp little-cms2 freetype openblas

PYTHONOPTIMIZE=0 pip install cffi
pip install coverage
pip install olefile
pip install -U pytest
pip install -U pytest-cov
pip install pyroma
pip install test-image-results

echo -e "[openblas]\nlibraries = openblas\nlibrary_dirs = /usr/local/opt/openblas/lib" >> ~/.numpy-site.cfg
pip install numpy

# TODO Remove when 3.9-dev includes setuptools 49.3.2+:
if [ "$GHA_PYTHON_VERSION" == "3.9-dev" ]; then pip install -U "setuptools>=49.3.2" ; fi

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
