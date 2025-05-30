#!/bin/bash

## Run this as the test script in the Docker valgrind image.
## Note -- can be included directly into the Docker image,
## but requires the current python.supp.

source /vpy3/bin/activate
cd /Pillow
make clean
make install
make valgrind-leak
