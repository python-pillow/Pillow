# https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html
# XXX Do we need all these phony targets?
.PHONY: clean coverage docs docserver help inplace install install-req release-test sdist test upload upload-test

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"
	@echo "  clean		remove build products"
	@echo "  install	make and install"
	@echo "  test		run tests on installed pillow"
	@echo "  inplace	make inplace extension" 
	@echo "  coverage	run coverage test (in progress)"
	@echo "  docs		make html docs"
	@echo "  docserver	run an http server on the docs directory"
	@echo "  install-req	install documentation and test dependencies"
	@echo "  upload	    build and upload sdists to PyPI" 
	@echo "  upload-test    build and upload sdists to test.pythonpackages.com"
	@echo "  release-test    run code and package tests before release"

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

clean:
	python setup.py clean
	rm PIL/*.so || true
	rm -r build || true
	find . -name __pycache__ | xargs rm -r || true

install:
	python setup.py install
	python selftest.py --installed

install-req:
	pip install -r requirements.txt

test:
	python test-installed.py

inplace: clean
	python setup.py build_ext --inplace

coverage: 
# requires nose-cov
	coverage erase
	coverage run --parallel-mode --include=PIL/* selftest.py
	nosetests --with-cov --cov='PIL/' --cov-report=html Tests/test_*.py
# doesn't combine properly before report, 
# writing report instead of displaying invalid report
	rm -r htmlcov || true
	coverage combine
	coverage report

docs:
	$(MAKE) -C docs html

docserver:
	cd docs/_build/html && python -mSimpleHTTPServer 2> /dev/null&

# Test sdist upload via test.pythonpackages.com. Create .pypirc first:
#
#    [test]
#    username:
#    password:
#    repository = http://test.pythonpackages.com
#
upload-test:
	python setup.py sdist --format=gztar,zip upload -r test
upload:
	python setup.py sdist --format=gztar,zip upload
sdist:
	python setup.py sdist --format=gztar,zip
