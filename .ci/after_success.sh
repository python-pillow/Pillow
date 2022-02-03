#!/bin/bash

# gather the coverage data
python3 -m pip install codecov
if [[ $MATRIX_DOCKER ]]; then
  coverage xml --ignore-errors
else
  coverage xml
fi
