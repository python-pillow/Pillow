#!/bin/bash

## Run this as the test script in the Docker valgrind image.
## Note -- can be included directly into the Docker image,
## but requires the current python.supp.

source /vpy3/bin/activate
cd /Pillow
make clean
make install

SPLIT_ARGS=""
if [ "${SPLIT_COUNT:-1}" -gt 1 ]; then
    SPLIT_ARGS="--splits ${SPLIT_COUNT} --group ${SPLIT_INDEX} --durations-path /depends/.test_durations"
fi
make valgrind-leak PYTEST_ARGS="$SPLIT_ARGS"
