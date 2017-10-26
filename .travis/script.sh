#!/bin/bash

set -e

coverage erase
python setup.py clean
CFLAGS="-coverage" python setup.py build_ext --inplace

coverage run --append --include=PIL/* selftest.py
# coverage run --append --include=PIL/* -m nose -vx Tests/test_*.py TODO remove
py.test -v --cov PIL --cov-report term Tests
pushd /tmp/check-manifest && check-manifest --ignore ".coveragerc,.editorconfig,*.yml,*.yaml,tox.ini" && popd

# Docs
if [ "$TRAVIS_PYTHON_VERSION" == "2.7" ]; then make install && make doccheck; fi
