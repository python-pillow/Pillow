Developer
=========

.. Note:: When committing only trivial changes, please include [ci skip] in the commit message to avoid running tests on Travis-CI. Thank you!

Release
-------

Details about making a Pillow release.

Version number
~~~~~~~~~~~~~~

The version number is currently stored in 3 places::

    PIL/__init__.py _imaging.c setup.py


Read the Docs
~~~~~~~~~~~~~

Make sure the default version for Read the Docs is the latest release version e.g. 3.0.0 not latest.

Release notes
-------------

.. toctree::
   :maxdepth: 2

   releasenotes/index.rst
