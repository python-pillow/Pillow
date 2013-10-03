pre:
	bin/python setup.py develop
	bin/python selftest.py
	bin/python Tests/run.py
	check-manifest
	pyroma .
	viewdoc
