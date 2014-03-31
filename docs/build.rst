Building Pillow on Windows
==========================

.. note:: For most people, the :doc:`installation instructions
          <installation>` should be sufficient

This page will describe a build setup to build Pillow against the
supported python versions in 32 and 64 bit modes, using freely
availble Microsoft compilers.  This has been developed and tested
against a bare Windows Server 2012 64bit RTM version on Amazon EC2.

Prerequsites
------------

Extra Build Helpers
^^^^^^^^^^^^^^^^^^^

* Google Chrome (optional - for sanity)
* GPG (for checking signatures)  (UNDONE -- python signature checking)
* Powershell (available by default on Windows Server)
* Github client (provides git+bash shell)

Pythons
^^^^^^^

Download and install Python 2.6, 2.7, 3.2, 3.3, and 3.4, both 32 and
64 bit versions. There is a python script that will download the
installers in `winbuild/get_pythons.py`. It requires python to run, so
download and install one of them first. 

::

   for version in ['2.6.5', '2.7.6', '3.2.5', '3.3.5', '3.4.0']:
        for platform in ['', '.amd64']:
            for extension in ['','.asc']:
                fetch('https://www.python.org/ftp/python/%s/python-%s%s.msi%s' %(
                    version, version, platform, extension))

UNDONE -- gpg verify the signatures (note that we can download from https)

We also need virtualenv and setuptools in at least one of the pythons
to build testing versions. 

Python 3.4 comes with pip. That makes it an ideal python to install
first. 

Compilers
^^^^^^^^^

Download and install:

* `Microsoft Windows SDK for Windows 7 and .NET Framework 3.5
  SP1 <http://www.microsoft.com/en-us/download/details.aspx?id=3138>`_

* `Microsoft Windows SDK for Windows 7 and .NET Framework
  4 <http://www.microsoft.com/en-us/download/details.aspx?id=8279>`_

* `CMake-2.8.10.2-win32-x86.exe <http://www.cmake.org/cmake/resources/software.html>`_

The samples and the .NET SDK portions aren't required, just the
compilers and other tools. UNDONE -- check exact wording.

Dependencies
------------

Run `winbuild/build_dep.cmd` in a command window. There are times when
the output clears the terminal, so it's best to run it in the
Powershell IDE, which has a more powerful terminal than the standard
Powershell window. 

This will download libjpeg, libtiff, libz, and freetype. It will then
compile 32 and 64 bit versions of the libraries, with both versions of
the compilers. 

UNDONE -- lcms fails. 
UNDONE -- webp not included yet. 

Testing Builds
--------------

Use the script UNDONE to build, install, selftest, and test Pillow in
virtualenvs for each Python that is installed. 

Installer Builds
----------------
 
Run `winbuild/build.cmd` in a powershell terminal to build Pillow
installers against each of the Pythons. 
