#!/bin/bash

# gather the coverage data
pip install codecov
coverage xml

if [[ $TRAVIS ]]; then
    codecov
fi

if [ "$TRAVIS_PYTHON_VERSION" == "3.8" ]; then
    # Coverage and quality reports on just the latest diff.
    depends/diffcover-install.sh
    depends/diffcover-run.sh
fi
