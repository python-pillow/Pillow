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
if [[ $(uname) != CYGWIN* ]]; then
    aptget_update || aptget_update retry || aptget_update retry
fi

set -e

if [[ $(uname) != CYGWIN* ]]; then
    sudo apt-get -qq install libfreetype6-dev liblcms2-dev libtiff-dev python3-tk\
                             ghostscript libjpeg-turbo8-dev libjxl-dev libopenjp2-7-dev\
                             cmake meson imagemagick libharfbuzz-dev libfribidi-dev\
                             sway wl-clipboard libopenblas-dev nasm
fi

python3 -m pip install --upgrade pip
python3 -m pip install --upgrade wheel
python3 -m pip install coverage
python3 -m pip install defusedxml
python3 -m pip install ipython
python3 -m pip install olefile
python3 -m pip install -U pytest
python3 -m pip install -U pytest-cov
python3 -m pip install -U pytest-timeout
python3 -m pip install pyroma
# optional test dependency, only install if there's a binary package.
# fails on beta 3.14 and PyPy
python3 -m pip install --only-binary=:all: pyarrow || true

if [[ $(uname) != CYGWIN* ]]; then
    python3 -m pip install numpy

    # PyQt6 doesn't support PyPy3
    if [[ $GHA_PYTHON_VERSION == 3.* ]]; then
        sudo apt-get -qq install libegl1 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxkbcommon-x11-0
        # TODO Update condition when pyqt6 supports free-threading
        if ! [[ "$PYTHON_GIL" == "0" ]]; then python3 -m pip install pyqt6 ; fi
    fi

    # Pyroma uses non-isolated build and fails with old setuptools
    if [[ $GHA_PYTHON_VERSION == 3.9 ]]; then
        # To match pyproject.toml
        python3 -m pip install "setuptools>=77"
    fi

    # webp
    pushd depends && ./install_webp.sh && popd

    # libimagequant
    pushd depends && ./install_imagequant.sh && popd

    # raqm
    pushd depends && ./install_raqm.sh && popd

    # libavif
    pushd depends && CMAKE_POLICY_VERSION_MINIMUM=3.5 ./install_libavif.sh && popd

    # extra test images
    pushd depends && ./install_extra_test_images.sh && popd
else
    cd depends && ./install_extra_test_images.sh && cd ..
fi
