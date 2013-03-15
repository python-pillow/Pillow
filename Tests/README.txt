Minimalistic PIL test framework.

Test scripts are named "test_xxx" and are supposed to output "ok". That's it. To run the tests::

    python setup.py develop

Run the tests from the root of the Pillow source distribution:

    python selftest.py
    python Tests/run.py --installed

To run an individual test:

    python Tests/test_image.py
