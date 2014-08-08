Pillow Tests
============

Test scripts are named ``test_xxx.py`` and use the ``unittest`` module. A base class and helper functions can be found in ``helper.py``.

Depedencies
-----------

Install::

    pip install coverage nose


Execution
---------

Run the tests from the root of the Pillow source distribution::

    nosetests Tests/test_*.py

Or with coverage::

    coverage run --append --include=PIL/* -m nose Tests/test_*.py
    coverage report
    coverage html
    open htmlcov/index.html

To run an individual test::

    python Tests/test_image.py

