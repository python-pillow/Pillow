#!/bin/bash
set -e

EXP_CODECS="jpg jpg_2000 libtiff zlib"
EXP_MODULES="freetype2 littlecms2 pil tkinter webp"
EXP_FEATURES="fribidi harfbuzz libjpeg_turbo raqm transp_webp webp_anim webp_mux xcb"

if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install fribidi
    export PKG_CONFIG_PATH="/usr/local/opt/openblas/lib/pkgconfig"
elif [ "${AUDITWHEEL_POLICY::9}" == "musllinux" ]; then
    apk add curl fribidi
else
    yum install -y fribidi
fi
if [ "${AUDITWHEEL_POLICY::9}" != "musllinux" ]; then
    python3 -m pip install numpy
fi

if [ ! -d "test-images-main" ]; then
    curl -fsSL -o pillow-test-images.zip https://github.com/python-pillow/test-images/archive/main.zip
    unzip pillow-test-images.zip
    mv test-images-main/* Tests/images
fi

# Runs tests
python3 selftest.py
python3 -m pytest

# Test against expected codecs, modules and features
codecs=$(python3 -c 'from PIL.features import *; print(" ".join(sorted(get_supported_codecs())))')
if [ "$codecs" != "$EXP_CODECS" ]; then
    echo "Codecs should be: '$EXP_CODECS'; but are '$codecs'"
    exit 1
fi
modules=$(python3 -c 'from PIL.features import *; print(" ".join(sorted(get_supported_modules())))')
if [ "$modules" != "$EXP_MODULES" ]; then
    echo "Modules should be: '$EXP_MODULES'; but are '$modules'"
    exit 1
fi
features=$(python3 -c 'from PIL.features import *; print(" ".join(sorted(get_supported_features())))')
if [ "$features" != "$EXP_FEATURES" ]; then
    echo "Features should be: '$EXP_FEATURES'; but are '$features'"
    exit 1
fi
