#!/bin/bash

set -e

brew bundle --file=.github/workflows/Brewfile

python3 -m pip install --upgrade ipython

# optional test dependencies, only install if there's a binary package.
python3 -m pip install --only-binary=:all: numpy || true
python3 -m pip install --only-binary=:all: pyarrow || true

# libavif
pushd depends && ./install_libavif.sh && popd

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
