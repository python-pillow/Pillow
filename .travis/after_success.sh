#!/bin/bash

# gather the coverage data
sudo apt-get -qq install lcov
lcov --capture --directory . -b . --output-file coverage.info
#  filter to remove system headers
lcov --remove coverage.info '/usr/*' -o coverage.filtered.info
#  convert to json
gem install coveralls-lcov
coveralls-lcov -v -n coverage.filtered.info > coverage.c.json

coverage report
pip install codecov
if [[ $TRAVIS_PYTHON_VERSION != "2.7_with_system_site_packages" ]]; then
    # Not working here. Just skip it, it's being removed soon.
    pip install coveralls-merge
    coveralls-merge coverage.c.json
fi
codecov

if [ "$TRAVIS_PYTHON_VERSION" == "2.7" ] && [ "$DOCKER" == "" ]; then
    # Coverage and quality reports on just the latest diff.
    # (Installation is very slow on Py3, so just do it for Py2.)
    depends/diffcover-install.sh
    depends/diffcover-run.sh
fi
