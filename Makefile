# https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html
.PHONY: clean coverage doc docserve help inplace install install-req release-test sdist test upload upload-test
.DEFAULT_GOAL := release-test

clean:
	python3 setup.py clean
	rm src/PIL/*.so || true
	rm -r build || true
	find . -name __pycache__ | xargs rm -r || true

BRANCHES=`git branch -a | grep -v HEAD | grep -v master | grep remote`
co:
	-for i in $(BRANCHES) ; do \
        git checkout -t $$i ; \
    done

coverage:
	python3 selftest.py
	python3 setup.py test
	rm -r htmlcov || true
	coverage report

doc:
	$(MAKE) -C docs html

doccheck:
	$(MAKE) -C docs html
# Don't make our tests rely on the links in the docs being up every single build.
# We don't control them.  But do check, and update them to the target of their redirects.
	$(MAKE) -C docs linkcheck || true

docserve:
	cd docs/_build/html && python3 -mSimpleHTTPServer 2> /dev/null&

help:
	@echo "Welcome to Pillow development. Please use \`make <target>\` where <target> is one of"
	@echo "  clean              remove build products"
	@echo "  coverage           run coverage test (in progress)"
	@echo "  doc                make html docs"
	@echo "  docserve           run an http server on the docs directory"
	@echo "  html               to make standalone HTML files"
	@echo "  inplace            make inplace extension"
	@echo "  install            make and install"
	@echo "  install-coverage   make and install with C coverage"
	@echo "  install-req        install documentation and test dependencies"
	@echo "  install-venv       install in virtualenv"
	@echo "  release-test       run code and package tests before release"
	@echo "  test               run tests on installed pillow"
	@echo "  upload             build and upload sdists to PyPI"
	@echo "  upload-test        build and upload sdists to test.pythonpackages.com"

inplace: clean
	python3 setup.py develop build_ext --inplace

install:
	python3 setup.py install
	python3 selftest.py

install-coverage:
	CFLAGS="-coverage" python3 setup.py build_ext install
	python3 selftest.py

debug:
# make a debug version if we don't have a -dbg python. Leaves in symbols
# for our stuff, kills optimization, and redirects to dev null so we
# see any build failures.
	make clean > /dev/null
	CFLAGS='-g -O0' python3 setup.py build_ext install > /dev/null

install-req:
	pip install -r requirements.txt

install-venv:
	virtualenv .
	bin/pip install -r requirements.txt

release-test:
	$(MAKE) install-req
	python3 setup.py develop
	python3 selftest.py
	python3 -m pytest Tests
	python3 setup.py install
	python3 -m pytest -qq
	check-manifest
	pyroma .
	viewdoc

sdist:
	python3 setup.py sdist --format=gztar

test:
	pytest -qq

# https://docs.python.org/3/distutils/packageindex.html#the-pypirc-file
upload-test:
#       [test]
#       username:
#       password:
#       repository = http://test.pythonpackages.com
	python3 setup.py sdist --format=gztar upload -r test

upload:
	python3 setup.py sdist --format=gztar upload

readme:
	viewdoc
