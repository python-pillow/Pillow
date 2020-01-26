#!/bin/bash

# gather the coverage data
pip3 install codecov
if [[ $MATRIX_DOCKER ]]; then
  coverage xml --ignore-errors
else
  coverage xml
fi

if [[ $TRAVIS ]]; then
    codecov --flags TravisCI
fi

if [ "$TRAVIS_PYTHON_VERSION" == "3.8" ]; then
    # Coverage and quality reports on just the latest diff.
    depends/diffcover-install.sh
    depends/diffcover-run.sh
fi
