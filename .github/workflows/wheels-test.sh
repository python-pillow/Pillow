#!/bin/bash
set -e

if [ "${AUDITWHEEL_POLICY::9}" == "musllinux" ]; then
    apk add curl
elif [ "${AUDITWHEEL_POLICY::9}" == "manylinux" ]; then
    ldconfig
fi

if [ ! -d "test-images-main" ]; then
    curl -fsSL -o pillow-test-images.zip https://github.com/python-pillow/test-images/archive/main.zip
    unzip pillow-test-images.zip
    mv test-images-main/* Tests/images
fi

# Runs tests
python3 selftest.py
python3 -m pytest -vv -x checks/check_wheel.py
python3 -m pytest -vv -x
