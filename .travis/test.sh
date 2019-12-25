#!/bin/bash

set -e

python -m pytest -v -x --cov PIL --cov Tests --cov-report term Tests

# Docs
if [ "$TRAVIS_PYTHON_VERSION" == "3.8" ]; then make doccheck; fi
