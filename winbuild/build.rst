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

* `CMake 3.15 or newer <https://cmake.org/download/>`_
  (also available as Visual Studio component C++ CMake tools for Windows)

* `Ninja <https://ninja-build.org/>`_
  (optional, use ``--nmake`` if not available; bundled in Visual Studio CMake component)

* x86/x64: `Netwide Assembler (NASM) <https://www.nasm.us/pub/nasm/releasebuilds/?C=M;O=D>`_

Any version of Visual Studio 2017 or newer should be supported,
including Visual Studio 2017 Community, or Build Tools for Visual Studio 2019.

Paths to CMake (if standalone) and NASM must be added to the ``PATH`` environment variable.
Visual Studio is found automatically with ``vswhere.exe``.

Build configuration
-------------------

Run ``build_prepare.py`` to configure the build::

    usage: winbuild\build_prepare.py [-h] [-v] [-d PILLOW_BUILD]
                                     [--depends PILLOW_DEPS]
                                     [--architecture {x86,x64,ARM64}] [--nmake]
                                     [--no-imagequant] [--no-fribidi]

    Download and generate build scripts for Pillow dependencies.

    options:
      -h, --help            show this help message and exit
      -v, --verbose         print generated scripts
      -d PILLOW_BUILD, --dir PILLOW_BUILD, --build-dir PILLOW_BUILD
                            build directory (default: 'winbuild\build')
      --depends PILLOW_DEPS
                            directory used to store cached dependencies (default:
                            'winbuild\depends')
      --architecture {x86,x64,ARM64}
                            build architecture (default: same as host Python)
      --nmake               build dependencies using NMake instead of Ninja
      --no-imagequant       skip GPL-licensed optional dependency libimagequant
      --no-fribidi, --no-raqm
                            skip LGPL-licensed optional dependency FriBiDi

    Arguments can also be supplied using the environment variables PILLOW_BUILD,
    PILLOW_DEPS, ARCHITECTURE. See winbuild\build.rst for more information.

**Warning:** The build directory is wiped when ``build_prepare.py`` is run.

Dependencies
------------

Dependencies will be automatically downloaded by ``build_prepare.py``.
By default, downloaded dependencies are stored in ``winbuild\depends``;
use the ``--depends`` argument or ``PILLOW_DEPS`` environment variable
to override this location.

To build all dependencies, run ``winbuild\build\build_dep_all.cmd``,
or run the individual scripts in order to build each dependency separately.

Building Pillow
---------------

Once the dependencies are built, make sure the required environment variables
are set by running ``winbuild\build\build_env.cmd`` and install Pillow with pip::

    winbuild\build\build_env.cmd
    python.exe -m pip install -v -C raqm=vendor -C fribidi=vendor .

To build a wheel instead, run::

    winbuild\build\build_env.cmd
    python.exe -m pip wheel -v -C raqm=vendor -C fribidi=vendor .

Testing Pillow
--------------

Some binary dependencies (e.g. ``fribidi.dll``) will be stored in the
``winbuild\build\bin`` directory; this directory should be added to ``PATH``
before running tests.

Build and install Pillow, then run ``python3 -m pytest`` from the root Pillow
directory.

Example
-------

The following is a simplified version of the script used on AppVeyor::

    set PYTHON=C:\Python38\bin
    cd /D C:\Pillow\winbuild
    %PYTHON%\python.exe build_prepare.py -v --depends C:\pillow-depends
    build\build_dep_all.cmd
    build\build_env.cmd
    cd ..
    %PYTHON%\python.exe -m pip install -v -C raqm=vendor -C fribidi=vendor .
    path C:\Pillow\winbuild\build\bin;%PATH%
    %PYTHON%\python.exe selftest.py
    %PYTHON%\python.exe -m pytest -vx --cov PIL --cov Tests --cov-report term --cov-report xml Tests
    %PYTHON%\python.exe -m pip wheel -v -C raqm=vendor -C fribidi=vendor .
