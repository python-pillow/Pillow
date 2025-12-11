#!/bin/bash

set -e

brew install \
    aom \
    dav1d \
    freetype \
    ghostscript \
    jpeg-turbo \
    libimagequant \
    libraqm \
    libtiff \
    little-cms2 \
    openjpeg \
    rav1e \
    svt-av1 \
    webp
export PKG_CONFIG_PATH="/usr/local/opt/openblas/lib/pkgconfig"

python3 -m pip install coverage
python3 -m pip install defusedxml
python3 -m pip install ipython
python3 -m pip install olefile
python3 -m pip install -U pytest
python3 -m pip install -U pytest-cov
python3 -m pip install -U pytest-timeout
python3 -m pip install pyroma
# optional test dependencies, only install if there's a binary package.
python3 -m pip install --only-binary=:all: numpy || true
python3 -m pip install --only-binary=:all: pyarrow || true

# libavif
pushd depends && ./install_libavif.sh && popd

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
