Building Pillow on Windows
==========================

.. note:: For most people, the `installation instructions
          <../docs/installation.rst#windows-installation>`_ should
          be sufficient.

This page describes the steps necessary to build Pillow using the same
scripts used on GitHub Actions and AppVeyor CIs.

Prerequisites
-------------


Python
^^^^^^

While the scripts can target any version of Python supported by Pillow,
Python 3.6+ is required to generate valid build scripts.

Compilers
^^^^^^^^^

Download and install:

* `Microsoft Visual Studio 2017 or newer (with C++ component)
  <https://visualstudio.microsoft.com/vs/older-downloads/>`_

* `CMake 3.13 or newer
  <https://cmake.org/download/>`_

* `NASM <https://www.nasm.us/pub/nasm/releasebuilds/?C=M;O=D>`_

Any version of Visual Studio 2017 or newer should be supported,
including Visual Studio 2017 Community.

Paths to CMake and NASM must be added to the ``PATH`` environment variable.

Build configuration
-------------------

The following environment variables, if set, will override the default
behaviour of ``build_prepare.py``:

* ``PYTHON`` + ``EXECUTABLE`` point to the target version of Python.
  If ``PYTHON`` is unset, the version of Python used to run
  ``build_prepare.py`` will be used. If only ``PYTHON`` is set,
  ``EXECUTABLE`` defaults to ``python.exe``.
* ``ARCHITECTURE`` is used to select a ``x86`` or ``x64`` build. By default,
  ``x86`` is used, unless ``PYTHON`` contains ``x64``, in which case ``x64``
  is used.
* ``PILLOW_BUILD`` can be used to override the ``winbuild\build`` directory
  path, used to store generated build scripts and compiled libraries.
  **Warning:** This directory is wiped when ``build_prepare.py`` is run.
* ``PILLOW_DEPS`` points to the directory used to store downloaded
  dependencies. By default ``winbuild\depends`` is used.

Dependencies
------------

Dependencies will be automatically downloaded by ``build_prepare.py``.
By default, downloaded dependencies are stored in ``winbuild\depends``;
set the ``PILLOW_DEPS`` environment variable to override this location.

To build all dependencies, run ``winbuild\build\build_dep_all.cmd``,
or run the individual scripts to build each dependency separately.

Building Pillow
---------------

Once the dependencies are built, run
``winbuild\build\build_pillow.cmd install`` to build and install
Pillow for the selected version of Python.
``winbuild\build\build_pillow.cmd bdist_wheel`` will build wheels
instead of installing Pillow.

Testing Pillow
--------------

Some binary dependencies (e.g. ``libraqm.dll``) will be stored in the
``winbuild\build\bin`` directory; this directory should be added to ``PATH``
before running tests.

Build and install Pillow, then run ``python -m pytest Tests``
from the root Pillow directory.

Example
-------

The following is a simplified version of the script used on AppVeyor:

.. code-block::

    set PYTHON=C:\Python35\bin
    cd /D C:\Pillow\winbuild
    C:\Python37\bin\python.exe build_prepare.py
    build\build_dep_all.cmd
    build\build_pillow.cmd install
    cd ..
    path C:\Pillow\winbuild\build\bin;%PATH%
    %PYTHON%\python.exe selftest.py
    %PYTHON%\python.exe -m pytest -vx --cov PIL --cov Tests --cov-report term --cov-report xml Tests
    build\build_pillow.cmd bdist_wheel
