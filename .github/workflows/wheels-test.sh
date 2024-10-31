#!/bin/bash
set -e

# Ensure fribidi is installed by the system.
if [[ "$OSTYPE" == "darwin"* ]]; then
    # If Homebrew is on the path during the build, it may leak into the wheels.
    # However, we *do* need Homebrew to provide a copy of fribidi for
    # testing purposes so that we can verify the fribidi shim works as expected.
    if [[ "$(uname -m)" == "x86_64" ]]; then
        # Use the "installed" location, rather than /usr/local, for two reasons:
        # firstly, Homebrew allows libraries to be *installed*, but not linked;
        # and secondly, we don't want any *other* leakage from /usr/local.
        HOMEBREW_HOME=/usr/local/Homebrew
    else
        HOMEBREW_HOME=/opt/homebrew
    fi
    $HOMEBREW_HOME/bin/brew install fribidi

    # Add the Homebrew lib folder so that vendored libraries can be found.
    export DYLD_LIBRARY_PATH=$HOMEBREW_HOME/lib
elif [ "${AUDITWHEEL_POLICY::9}" == "musllinux" ]; then
    apk add curl fribidi
else
    yum install -y fribidi
fi

python3 -m pip install numpy

if [ ! -d "test-images-main" ]; then
    curl -fsSL -o pillow-test-images.zip https://github.com/python-pillow/test-images/archive/main.zip
    unzip pillow-test-images.zip
    mv test-images-main/* Tests/images
fi

# Runs tests
python3 selftest.py
python3 -m pytest Tests/check_wheel.py
python3 -m pytest
