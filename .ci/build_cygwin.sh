#!/bin/bash

set -e

python3 -m coverage erase
make clean
CFLAGS="-coverage -Werror=implicit-function-declaration" python3 -m pip install -v --global-option="build_ext" .
python3 selftest.py
