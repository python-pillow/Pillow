pre:
	bin/python setup.py develop
	bin/python selftest.py
	bin/nosetests Tests/test_*.py
	check-manifest
	pyroma .
	viewdoc
