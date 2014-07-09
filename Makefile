

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

test: install
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
