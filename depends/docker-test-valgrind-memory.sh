#!/bin/bash

## Run this as the test script in the docker valgrind image.
## Note -- can be included directly into the docker image,
## but requires the currnet python.supp.

source /vpy3/bin/activate
cd /Pillow
make clean
make install
make valgrind-memory
