Building Pillow on Windows
==========================

.. note:: For most people, the :doc:`installation instructions
          <installation>` should be sufficient

This page will describe a build setup to build Pillow against the
supported Python versions in 32 and 64-bit modes, using freely
available Microsoft compilers.  This has been developed and tested
against 64-bit Windows 7 Professional and Windows Server 2012
64-bit version on Amazon EC2.

Prerequisites
-------------

Extra Build Helpers
^^^^^^^^^^^^^^^^^^^

* Powershell (available by default on Windows Server)
* GitHub client (provides git+bash shell)

Optional:
* GPG (for checking signatures)  (UNDONE -- Python signature checking)


Pythons
^^^^^^^

The build routines expect Python to be installed at C:\PythonXX for
32-bit versions or C:\PythonXXx64 for the 64-bit versions.

Download Python 3.4, install it, and add it to the path. This is the
Python that we will use to bootstrap the build process. (The download
routines are using 3.2+ features, and installing 3.4 gives us pip and
virtualenv as well, reducing the number of packages that we need to
install.)

Download the rest of the Pythons by opening a command window, changing
to the `winbuild` directory, and running `python
get_pythons.py`.

UNDONE -- gpg verify the signatures (note that we can download from
https)

Run each installer and set the proper path to the installation. Don't
set any of them as the default Python, or add them to the path.


Compilers
^^^^^^^^^

Download and install:

* `Microsoft Windows SDK for Windows 7 and .NET Framework 3.5
  SP1 <https://www.microsoft.com/en-us/download/details.aspx?id=3138>`_

* `Microsoft Windows SDK for Windows 7 and .NET Framework
  4 <https://www.microsoft.com/en-us/download/details.aspx?id=8279>`_

* `CMake-2.8.10.2-win32-x86.exe <https://cmake.org/download/>`_

The samples and the .NET SDK portions aren't required, just the
compilers and other tools. UNDONE -- check exact wording.

Dependencies
------------

The script 'build_dep.py' downloads and builds the dependencies.  Open
a command window, change directory into `winbuild` and run `python
build_dep.py`.

This will download libjpeg, libtiff, libz, and freetype. It will then
compile 32 and 64-bit versions of the libraries, with both versions of
the compilers.

UNDONE -- lcms fails.
UNDONE -- webp, jpeg2k not recognized

Building Pillow
---------------

Once the dependencies are built, run `python build.py --clean` to
build and install Pillow in virtualenvs for each python
build. `build.py --dist` will build Windows installers instead of
installing into virtualenvs.

UNDONE -- suppressed output, what about failures.

Testing Pillow
--------------

Build and install Pillow, then run `python test.py` from the
`winbuild` directory.

