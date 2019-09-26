#!/bin/bash

set -e

coverage erase
make clean
make install-coverage

python -m pytest -v -x --cov PIL --cov-report term Tests

# Docs
if [ "$TRAVIS_PYTHON_VERSION" == "3.7" ]; then make doccheck; fi
