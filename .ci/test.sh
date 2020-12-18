#!/bin/bash

set -e

python -bb -m pytest -v -x -W always --cov PIL --cov Tests --cov-report term Tests

# Docs
if [ "$GHA_PYTHON_VERSION" == "3.9" ] && [ "$GHA_OS" == "ubuntu-latest" ]; then
    make doccheck
fi
