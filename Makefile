.DEFAULT_GOAL := help

.PHONY: clean
clean:
	rm src/PIL/*.so || true
	rm -r build || true
	find . -name __pycache__ | xargs rm -r || true

.PHONY: coverage
coverage:
	python3 -c "import pytest" > /dev/null 2>&1 || python3 -m pip install pytest
	python3 -m pytest -qq
	rm -r htmlcov || true
	python3 -c "import coverage" > /dev/null 2>&1 || python3 -m pip install coverage
	python3 -m coverage report

.PHONY: doc
.PHONY: html
doc html:
	$(MAKE) -C docs html

.PHONY: htmlview
htmlview:
	$(MAKE) -C docs htmlview

.PHONY: htmllive
htmllive:
	$(MAKE) -C docs htmllive

.PHONY: doccheck
doccheck:
	$(MAKE) doc
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
	@echo "  doc                make HTML docs"
	@echo "  docserve           run an HTTP server on the docs directory"
	@echo "  html               make HTML docs"
	@echo "  htmlview           open the index page built by the html target in your browser"
	@echo "  htmllive           rebuild and reload HTML files in your browser"
	@echo "  install            make and install"
	@echo "  install-coverage   make and install with C coverage"
	@echo "  lint               run the lint checks"
	@echo "  lint-fix           run Ruff to (mostly) fix lint issues"
	@echo "  release-test       run code and package tests before release"
	@echo "  test               run tests on installed Pillow"

.PHONY: install
install:
	python3 -m pip -v install .
	python3 selftest.py

.PHONY: install-coverage
install-coverage:
	CFLAGS="-coverage -Werror=implicit-function-declaration" python3 -m pip -v install .
	python3 selftest.py

.PHONY: debug
debug:
# make a debug version if we don't have a -dbg python. Leaves in symbols
# for our stuff, kills optimization, and redirects to dev null so we
# see any build failures.
	make clean > /dev/null
	CFLAGS='-g -O0' python3 -m pip -v install . > /dev/null

.PHONY: release-test
release-test:
	python3 checks/check_release_notes.py
	python3 -m pip install -e .[tests]
	python3 selftest.py
	python3 -m pytest Tests
	python3 -m pip install .
	python3 -m pytest -qq
	python3 -m check_manifest
	python3 -m pyroma .
	$(MAKE) readme

.PHONY: sdist
sdist:
	python3 -m build --help > /dev/null 2>&1 || python3 -m pip install build
	python3 -m build --sdist
	python3 -m twine --help > /dev/null 2>&1 || python3 -m pip install twine
	python3 -m twine check --strict dist/*

.PHONY: test
test:
	python3 -c "import pytest" > /dev/null 2>&1 || python3 -m pip install pytest
	python3 -m pytest -qq

.PHONY: test-p
test-p:
	python3 -c "import xdist" > /dev/null 2>&1 || python3 -m pip install pytest-xdist
	python3 -m pytest -qq -n auto


.PHONY: valgrind
valgrind:
	python3 -c "import pytest_valgrind" > /dev/null 2>&1 || python3 -m pip install pytest-valgrind
	PILLOW_VALGRIND_TEST=true PYTHONMALLOC=malloc valgrind --suppressions=Tests/oss-fuzz/python.supp --leak-check=no \
            --log-file=/tmp/valgrind-output \
            python3 -m pytest --no-memcheck -vv --valgrind --valgrind-log=/tmp/valgrind-output

.PHONY: valgrind-leak
valgrind-leak:
	python3 -c "import pytest_valgrind" > /dev/null 2>&1 || python3 -m pip install pytest-valgrind
	PILLOW_VALGRIND_TEST=true PYTHONMALLOC=malloc valgrind --suppressions=Tests/oss-fuzz/python.supp \
	    --leak-check=full --show-leak-kinds=definite --errors-for-leak-kinds=definite \
            --log-file=/tmp/valgrind-output \
            python3 -m pytest -vv --valgrind --valgrind-log=/tmp/valgrind-output

.PHONY: readme
readme:
	python3 -c "import markdown2" > /dev/null 2>&1 || python3 -m pip install markdown2
	python3 -m markdown2 README.md > .long-description.html && open .long-description.html


.PHONY: lint
lint:
	python3 -c "import tox" > /dev/null 2>&1 || python3 -m pip install tox
	python3 -m tox -e lint

.PHONY: lint-fix
lint-fix:
	python3 -c "import black" > /dev/null 2>&1 || python3 -m pip install black
	python3 -m black .
	python3 -c "import ruff" > /dev/null 2>&1 || python3 -m pip install ruff
	python3 -m ruff check --fix .

.PHONY: mypy
mypy:
	python3 -c "import tox" > /dev/null 2>&1 || python3 -m pip install tox
	python3 -m tox -e mypy
