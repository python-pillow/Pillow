Pillow Tests
============

Test scripts are named ``test_xxx.py`` and use the ``unittest`` module. A base class and helper functions can be found in ``helper.py``.

Dependencies
-----------

Install::

    pip install pytest pytest-cov

Execution
---------

**If Pillow has been built in-place**

To run an individual test::

    python Tests/test_image.py

Run all the tests from the root of the Pillow source distribution::

    pytest -vx Tests

Or with coverage::

    pytest -vx --cov PIL --cov-report term Tests
    coverage html
    open htmlcov/index.html

**If Pillow has been installed**

To run an individual test::

    pytest -k Tests/test_image.py

Run all the tests from the root of the Pillow source distribution::

    pytest
