#!/bin/bash

set -e

coverage erase
if [ $(uname) == "Darwin" ]; then
    export CPPFLAGS="-I/usr/local/miniconda/include";
fi
make clean
make install-coverage
