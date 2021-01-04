#!/bin/bash

# gather the coverage data
pip3 install codecov
if [[ $MATRIX_DOCKER ]]; then
  coverage xml --ignore-errors
else
  coverage xml
fi
