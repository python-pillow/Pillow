#!/bin/bash

set -e

if [[ "$ImageOS" == "macos13" ]]; then
    brew uninstall gradle maven
fi
brew install \
    freetype \
    ghostscript \
    libimagequant \
    libjpeg \
    libtiff \
    little-cms2 \
    openjpeg \
    webp \
    dav1d \
    aom \
    rav1e \
    ninja
if [[ "$ImageOS" == "macos13" ]]; then
    brew install --ignore-dependencies libraqm
else
    brew install libraqm
fi
export PKG_CONFIG_PATH="/usr/local/opt/openblas/lib/pkgconfig"

python3 -m pip install coverage
python3 -m pip install defusedxml
python3 -m pip install ipython
python3 -m pip install olefile
python3 -m pip install -U pytest
python3 -m pip install -U pytest-cov
python3 -m pip install -U pytest-timeout
python3 -m pip install pyroma
python3 -m pip install numpy

# libavif
pushd depends && ./install_libavif.sh && popd

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
