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
pip install coveralls-merge
coveralls-merge coverage.c.json

if [ "$DOCKER" == "" ]; then
	pip install pep8 pyflakes
	pep8 --statistics --count PIL/*.py
	pep8 --statistics --count Tests/*.py
	pyflakes *.py       | tee >(wc -l)
	pyflakes PIL/*.py   | tee >(wc -l)
	pyflakes Tests/*.py | tee >(wc -l)
fi

if [ "$TRAVIS_PYTHON_VERSION" == "2.7" ] && [ "$DOCKER" == "" ]; then
	# Coverage and quality reports on just the latest diff.
	# (Installation is very slow on Py3, so just do it for Py2.)
	depends/diffcover-install.sh
	depends/diffcover-run.sh
fi

# after_all

if [ "$TRAVIS_REPO_SLUG" = "python-pillow/Pillow" ] && [ "$TRAVIS_BRANCH" = "master" ] && [ "$TRAVIS_PULL_REQUEST" = "false" ]; then
    curl -Lo travis_after_all.py https://raw.github.com/dmakhno/travis_after_all/master/travis_after_all.py
    python travis_after_all.py
    export $(cat .to_export_back)
    if [ "$BUILD_LEADER" = "YES" ]; then
        if [ "$BUILD_AGGREGATE_STATUS" = "others_succeeded" ]; then
            echo "All jobs succeeded! Triggering macOS build..."
            # Trigger a macOS build at the pillow-wheels repo
            ./build_children.sh
        else
            echo "Some jobs failed"
        fi
    fi
fi
