#!/bin/bash

set -e

python3 -m coverage erase
make clean
make install-coverage
