Pillow Tests
============

Test scripts are named ``test_xxx.py`` and use the ``unittest`` module. A base class and helper functions can be found in ``helper.py``.

Dependencies
-----------

Install::

    pip install coverage nose

Execution
---------

**If Pillow has been built in-place**

To run an individual test::

    python Tests/test_image.py

Run all the tests from the root of the Pillow source distribution::

    nosetests -vx Tests/test_*.py

Or with coverage::

    coverage run --append --include=PIL/* -m nose -vx Tests/test_*.py
    coverage report
    coverage html
    open htmlcov/index.html

**If Pillow has been installed**

To run an individual test::

    ./test-installed.py Tests/test_image.py

Run all the tests from the root of the Pillow source distribution::

    ./test-installed.py



