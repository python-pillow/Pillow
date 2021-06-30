.DEFAULT_GOAL := help

.PHONY: clean
clean:
	python3 setup.py clean
	rm src/PIL/*.so || true
	rm -r build || true
	find . -name __pycache__ | xargs rm -r || true

.PHONY: coverage
coverage:
	pytest -qq
	rm -r htmlcov || true
	coverage report

.PHONY: doc
doc:
	$(MAKE) -C docs html

.PHONY: doccheck
doccheck:
	$(MAKE) -C docs html
# Don't make our tests rely on the links in the docs being up every single build.
# We don't control them.  But do check, and update them to the target of their redirects.
	$(MAKE) -C docs linkcheck || true

.PHONY: docserve
docserve:
	cd docs/_build/html && python3 -m http.server 2> /dev/null&

.PHONY: help
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
	@echo "  install-venv       (deprecated) install in virtualenv"
	@echo "  lint               run the lint checks"
	@echo "  lint-fix           run black and isort to (mostly) fix lint issues."
	@echo "  release-test       run code and package tests before release"
	@echo "  test               run tests on installed pillow"
	@echo "  upload             build and upload sdists to PyPI"
	@echo "  upload-test        build and upload sdists to test.pythonpackages.com"

.PHONY: inplace
inplace: clean
	python3 setup.py develop build_ext --inplace

.PHONY: install
install:
	python3 setup.py install
	python3 selftest.py

.PHONY: install-coverage
install-coverage:
	CFLAGS="-coverage -Werror=implicit-function-declaration" python3 setup.py build_ext install
	python3 selftest.py

.PHONY: debug
debug:
# make a debug version if we don't have a -dbg python. Leaves in symbols
# for our stuff, kills optimization, and redirects to dev null so we
# see any build failures.
	make clean > /dev/null
	CFLAGS='-g -O0' python3 setup.py build_ext install > /dev/null

.PHONY: install-req
install-req:
	python3 -m pip install -r requirements.txt

.PHONY: install-venv
install-venv:
	echo "'install-venv' is deprecated and will be removed in a future Pillow release"
	virtualenv .
	bin/pip install -r requirements.txt

.PHONY: release-test
release-test:
	$(MAKE) install-req
	python3 setup.py develop
	python3 selftest.py
	python3 -m pytest Tests
	python3 setup.py install
	-rm dist/*.egg
	-rmdir dist
	python3 -m pytest -qq
	check-manifest
	pyroma .
	$(MAKE) readme

.PHONY: sdist
sdist:
	python3 setup.py sdist --format=gztar

.PHONY: test
test:
	pytest -qq

.PHONY: valgrind
valgrind:
	python3 -c "import pytest_valgrind" || pip3 install pytest-valgrind
	PYTHONMALLOC=malloc valgrind --suppressions=Tests/oss-fuzz/python.supp --leak-check=no \
            --log-file=/tmp/valgrind-output \
            python3 -m pytest --no-memcheck -vv --valgrind --valgrind-log=/tmp/valgrind-output

.PHONY: readme
readme:
	python3 setup.py --long-description | markdown2 > .long-description.html && open .long-description.html


.PHONY: lint
lint:
	tox --help > /dev/null || python3 -m pip install tox
	tox -e lint

.PHONY: lint-fix
lint-fix:
	black --target-version py36 .
	isort .
