#!/bin/bash

set -e

coverage erase
python setup.py clean
CFLAGS="-coverage" python setup.py build_ext --inplace

python selftest.py
python setup.py test
pushd /tmp/check-manifest && check-manifest --ignore ".coveragerc,.editorconfig,*.yml,*.yaml,tox.ini" && popd

# Docs
if [ "$TRAVIS_PYTHON_VERSION" == "2.7" ]; then make install && make doccheck; fi
