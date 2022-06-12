#!/bin/bash

set -e

python3 -m coverage erase
if [ $(uname) == "Darwin" ]; then
    export CPPFLAGS="-I/usr/local/miniconda/include";
fi
make clean
make install-coverage
