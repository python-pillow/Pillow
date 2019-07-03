#!/bin/bash

set -e

coverage erase
make clean
make install-coverage

python selftest.py
python -m pytest -v -x --cov PIL --cov-report term Tests

# Docs
if [ "$TRAVIS_PYTHON_VERSION" == "2.7" ]; then make doccheck; fi
