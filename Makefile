# https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html
.PHONY: clean coverage doc docserve help inplace install install-req release-test sdist test upload upload-test
.DEFAULT_GOAL := release-test

clean:
	python setup.py clean
	rm PIL/*.so || true
	rm -r build || true
	find . -name __pycache__ | xargs rm -r || true

BRANCHES=`git branch -a | grep -v HEAD | grep -v master | grep remote`
co:
	-for i in $(BRANCHES) ; do \
        git checkout -t $$i ; \
    done

coverage: 
	coverage erase
	coverage run --parallel-mode --include=PIL/* selftest.py
	nosetests --with-cov --cov='PIL/' --cov-report=html Tests/test_*.py
# Doesn't combine properly before report, writing report instead of displaying invalid report.
	rm -r htmlcov || true
	coverage combine
	coverage report

doc:
	$(MAKE) -C docs html

docserve:
	cd docs/_build/html && python -mSimpleHTTPServer 2> /dev/null&

help:
	@echo "Welcome to Pillow development. Please use \`make <target>' where <target> is one of"
	@echo "  clean          remove build products"
	@echo "  coverage       run coverage test (in progress)"
	@echo "  doc            make html docs"
	@echo "  docserve       run an http server on the docs directory"
	@echo "  html           to make standalone HTML files"
	@echo "  inplace        make inplace extension" 
	@echo "  install        make and install"
	@echo "  install-req    install documentation and test dependencies"
	@echo "  install-venv   install in virtualenv"
	@echo "  release-test   run code and package tests before release"
	@echo "  test           run tests on installed pillow"
	@echo "  upload         build and upload sdists to PyPI" 
	@echo "  upload-test    build and upload sdists to test.pythonpackages.com"

inplace: clean
	python setup.py build_ext --inplace

install:
	python setup.py install
	python selftest.py --installed

install-req:
	pip install -r requirements.txt

install-venv: 
	virtualenv .
	bin/pip install -r requirements.txt

release-test:
	$(MAKE) install-req
	python setup.py develop
	python selftest.py
	nosetests Tests/test_*.py
	python setup.py install
	python test-installed.py
	check-manifest
	pyroma .
	viewdoc

sdist:
	python setup.py sdist --format=gztar,zip

test:
	python test-installed.py

# https://docs.python.org/2/distutils/packageindex.html#the-pypirc-file
upload-test:
#       [test]
#       username:
#       password:
#       repository = http://test.pythonpackages.com
	python setup.py sdist --format=gztar,zip upload -r test

upload:
	python setup.py sdist --format=gztar,zip upload

readme:
	viewdoc
