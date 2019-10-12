#!/bin/bash

set -e

sudo installer -pkg /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg -target /

brew install libtiff libjpeg webp little-cms2

PYTHONOPTIMIZE=0 pip install cffi
pip install coverage
pip install olefile
pip install -U pytest
pip install -U pytest-cov
pip install pyroma
pip install test-image-results
pip install numpy

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
