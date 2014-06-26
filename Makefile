pre:
	bin/python setup.py develop
	bin/python selftest.py
	check-manifest
	pyroma .
	viewdoc
