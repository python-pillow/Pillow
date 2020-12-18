#!/bin/bash

# gather the coverage data
pip3 install codecov
if [[ $MATRIX_DOCKER ]]; then
  coverage xml --ignore-errors
else
  coverage xml
fi

codecov --flags GitHubActions

if [ "$GHA_PYTHON_VERSION" == "3.9" ]; then
    # Coverage and quality reports on just the latest diff.
    depends/diffcover-install.sh
    depends/diffcover-run.sh
fi
