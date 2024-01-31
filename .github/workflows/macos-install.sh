#!/bin/bash

set -e

brew install \
    freetype \
    ghostscript \
    libimagequant \
    libjpeg \
    libraqm \
    libtiff \
    little-cms2 \
    openjpeg \
    webp
export PKG_CONFIG_PATH="/usr/local/opt/openblas/lib/pkgconfig"

# TODO Update condition when cffi supports 3.13
if ! [[ "$GHA_PYTHON_VERSION" == "3.13" ]]; then PYTHONOPTIMIZE=0 python3 -m pip install cffi ; fi

python3 -m pip install coverage
python3 -m pip install defusedxml
python3 -m pip install olefile
python3 -m pip install -U pytest
python3 -m pip install -U pytest-cov
python3 -m pip install -U pytest-timeout
python3 -m pip install pyroma

# TODO Update condition when NumPy supports 3.13
if ! [[ "$GHA_PYTHON_VERSION" == "3.13" ]]; then python3 -m pip install numpy ; fi

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
