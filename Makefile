pre:
	bin/python setup.py develop
	bin/python selftest.py
	bin/nosetests Tests/test_*.py
	bin/python setup.py install
	bin/python test-installed.py
	check-manifest
	pyroma .
	viewdoc
