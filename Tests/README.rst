Pillow Tests
============

Test scripts are named ``test_xxx.py``. Helper classes and functions can be found in ``helper.py``.

Dependencies
------------

Install::

    python3 -m pip install pytest pytest-cov

Execution
---------

To run an individual test::

    pytest Tests/test_image.py

Or::

    pytest -k test_image.py

Run all the tests from the root of the Pillow source distribution::

    pytest

Or with coverage::

    pytest --cov PIL --cov Tests --cov-report term
    coverage html
    open htmlcov/index.html
