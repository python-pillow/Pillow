.PHONY: pre clean install test inplace coverage test-dep help docs livedocs

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
	@echo "  test-dep	install coveraget and test dependencies"

pre:
	virtualenv .
	pip install -r requirements.txt
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

test-dep:
	pip install -r requirements.txt

docs:
	$(MAKE) -C docs html

docserver:
	cd docs/_build/html && python -mSimpleHTTPServer 2> /dev/null&

# Test sdist upload via test.pythonpackages.com, no creds required
# .pypirc:
# [test]
# username:
# password:
# repository = http://test.pythonpackages.com
sdisttest:
	python setup.py sdist --format=gztar,zip upload -r test
sdistup:
	python setup.py sdist --format=gztar,zip upload
sdist:
	python setup.py sdist --format=gztar,zip
