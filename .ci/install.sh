#!/bin/bash

aptget_update()
{
    if [ -n "$1" ]; then
        echo ""
        echo "Retrying apt-get update..."
        echo ""
    fi
    output=$(sudo apt-get update 2>&1)
    echo "$output"
    if [[ $output == *[WE]:\ * ]]; then
        return 1
    fi
}
aptget_update || aptget_update retry || aptget_update retry

set -e

packages=(
    cmake
    ghostscript
    imagemagick  # ImageMagick is used by Tests/test_file_palm.py
    libfreetype6-dev
    libharfbuzz-dev
    libjpeg-turbo8-dev
    liblcms2-dev
    libopenjp2-7-dev
    libtiff-dev
    meson
    nasm
    netpbm  # netpbm provides ppmquant and ppmtogif for GifImagePlugin._save_netpbm
    python3-tk
    sway
    wl-clipboard
)
sudo apt-get -qq install --no-install-recommends "${packages[@]}"

python3 -m pip install --upgrade pip
python3 -m pip install --upgrade coverage defusedxml ipython olefile pytest pytest-cov pytest-timeout

# optional test dependencies, only install if there's a binary package.
python3 -m pip install --only-binary=:all: numpy || true
python3 -m pip install --only-binary=:all: pyarrow || true

# PyQt6 doesn't support PyPy3
if [[ $GHA_PYTHON_VERSION == 3.* ]]; then
    # pyqt6 doesn't yet support free-threading; only install if a wheel is available
    python3 -m pip install --only-binary=:all: pyqt6 || true
fi

# webp
pushd depends && ./install_webp.sh && popd

# libimagequant
pushd depends && ./install_imagequant.sh && popd

# raqm
pushd depends && sudo ./install_sheenbidi.sh && sudo ./install_raqm.sh && popd

# libavif
pushd depends && ./install_libavif.sh && popd

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
