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
	bin/pip install -r requirements.txt
	bin/python setup.py develop
	bin/python selftest.py
	bin/nosetests Tests/test_*.py
	bin/python setup.py install
	bin/python test-installed.py
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
	pip install coveralls nose nose-cov pep8 pyflakes

docs:
	$(MAKE) -C docs html

docserver:
	cd docs/_build/html && python -mSimpleHTTPServer 2> /dev/null&