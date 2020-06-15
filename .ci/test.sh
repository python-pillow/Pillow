#!/bin/bash

set -e

python -m pytest -v -x -W always --cov PIL --cov Tests --cov-report term Tests

# Docs
if [ "$TRAVIS_PYTHON_VERSION" == "3.8" ] && [ "$TRAVIS_CPU_ARCH" == "amd64" ]; then
    make doccheck
fi
