Building Pillow on Windows
==========================

.. note:: For most people, the `installation instructions
          <../docs/installation.rst#windows-installation>`_ should
          be sufficient.

This page describes the steps necessary to build Pillow using the same
scripts used on GitHub Actions and AppVeyor CIs.

Prerequisites
-------------


Compilers
^^^^^^^^^

Download and install:

* `Microsoft Visual Studio 2017 or newer or Build Tools for Visual Studio 2017 or newer
  <https://visualstudio.microsoft.com/downloads/>`_
  (MSVC C++ build tools, and any Windows SDK version required)

* `CMake 3.12 or newer <https://cmake.org/download/>`_
  (also available as Visual Studio component C++ CMake tools for Windows)

* `NASM <https://www.nasm.us/pub/nasm/releasebuilds/?C=M;O=D>`_

Any version of Visual Studio 2017 or newer should be supported,
including Visual Studio 2017 Community, or Build Tools for Visual Studio 2019.

Paths to CMake (if standalone) and NASM must be added to the ``PATH`` environment variable.
Visual Studio is found automatically with ``vswhere.exe``.

Build configuration
-------------------

The following environment variables, if set, will override the default
behaviour of ``build_prepare.py``:

* ``PYTHON`` + ``EXECUTABLE`` point to the target version of Python.
  If ``PYTHON`` is unset, the version of Python used to run
  ``build_prepare.py`` will be used. If only ``PYTHON`` is set,
  ``EXECUTABLE`` defaults to ``python.exe``.
* ``ARCHITECTURE`` is used to select a ``x86`` or ``x64`` build. By default,
  uses same architecture as the version of Python used to run ``build_prepare.py``.
  is used.
* ``PILLOW_BUILD`` can be used to override the ``winbuild\build`` directory
  path, used to store generated build scripts and compiled libraries.
  **Warning:** This directory is wiped when ``build_prepare.py`` is run.
* ``PILLOW_DEPS`` points to the directory used to store downloaded
  dependencies. By default ``winbuild\depends`` is used.

``build_prepare.py`` also supports the following command line parameters:

* ``-v`` will print generated scripts.
* ``--no-imagequant`` will skip GPL-licensed ``libimagequant`` optional dependency
* ``--no-raqm`` will skip optional dependency Raqm (which itself depends on
  LGPL-licensed ``fribidi``).
* ``--python=<path>`` and ``--executable=<exe>`` override ``PYTHON`` and ``EXECUTABLE``.
* ``--architecture=<arch>`` overrides ``ARCHITECTURE``.
* ``--dir=<path>`` and ``--depends=<path>`` override ``PILLOW_BUILD``
  and ``PILLOW_DEPS``.

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

You can also use ``winbuild\build\build_pillow.cmd --inplace develop`` to build
and install Pillow in develop mode (instead of ``python3 -m pip install --editable``).

Testing Pillow
--------------

Some binary dependencies (e.g. ``fribidi.dll``) will be stored in the
``winbuild\build\bin`` directory; this directory should be added to ``PATH``
before running tests.

Build and install Pillow, then run ``python -m pytest Tests``
from the root Pillow directory.

Example
-------

The following is a simplified version of the script used on AppVeyor:

.. code-block::

    set PYTHON=C:\Python38\bin
    cd /D C:\Pillow\winbuild
    C:\Python37\bin\python.exe build_prepare.py -v --depends=C:\pillow-depends
    build\build_dep_all.cmd
    build\build_pillow.cmd install
    cd ..
    path C:\Pillow\winbuild\build\bin;%PATH%
    %PYTHON%\python.exe selftest.py
    %PYTHON%\python.exe -m pytest -vx --cov PIL --cov Tests --cov-report term --cov-report xml Tests
    build\build_pillow.cmd bdist_wheel
