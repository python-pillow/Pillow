#!/bin/bash

# gather the coverage data
if [[ "$MATRIX_OS" == "macOS-latest" ]]; then
    brew install lcov
else
    sudo apt-get -qq install lcov
fi

lcov --capture --directory . -b . --output-file coverage.info
#  filter to remove system headers
lcov --remove coverage.info '/usr/*' -o coverage.filtered.info

pip install codecov
coverage report

if [[ $TRAVIS ]]; then
    codecov
fi

if [ "$TRAVIS_PYTHON_VERSION" == "3.8" ]; then
    # Coverage and quality reports on just the latest diff.
    depends/diffcover-install.sh
    depends/diffcover-run.sh
fi
