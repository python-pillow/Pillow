Installation
============

Warnings
--------

.. warning:: Pillow and PIL cannot co-exist in the same environment. Before installing Pillow, please uninstall PIL.

.. warning:: Pillow >= 1.0 no longer supports "import Image". Please use "from PIL import Image" instead.

.. warning:: Pillow >= 2.1.0 no longer supports "import _imaging". Please use "from PIL.Image import core as _imaging" instead.

Notes
-----

.. note:: Pillow < 2.0.0 supports Python versions 2.4, 2.5, 2.6, 2.7.

.. note:: Pillow >= 2.0.0 < 3.5.0 supports Python versions 2.6, 2.7, 3.2, 3.3, 3.4, 3.5

.. note:: Pillow >= 3.5.0 supports Python versions 2.7, 3.3, 3.4, 3.5, 3.6

Basic Installation
------------------

.. note::

    The following instructions will install Pillow with support for
    most common image formats. See :ref:`external-libraries` for a
    full list of external libraries supported.

.. note::

   The basic installation works on Windows and macOS using the binaries
   from PyPI. Other installations require building from source as
   detailed below.

Install Pillow with :command:`pip`::

    $ pip install Pillow

Or use :command:`easy_install` for installing `Python Eggs
<http://peak.telecommunity.com/DevCenter/PythonEggs>`_ as
:command:`pip` does not support them::

    $ easy_install Pillow


Windows Installation
^^^^^^^^^^^^^^^^^^^^

We provide Pillow binaries for Windows compiled for the matrix of
supported Pythons in both 32 and 64-bit versions in wheel, egg, and
executable installers. These binaries have all of the optional
libraries included::

  > pip install Pillow

or::

  > easy_install Pillow


macOS Installation
^^^^^^^^^^^^^^^^^^

We provide binaries for macOS for each of the supported Python versions
in the wheel format. These include support for all optional libraries
except OpenJPEG::

  $ pip install Pillow

Linux Installation
^^^^^^^^^^^^^^^^^^

We do not provide binaries for Linux. Most major Linux distributions,
including Fedora, Debian/Ubuntu and ArchLinux include Pillow in
packages that previously contained PIL e.g. ``python-imaging``. Please
consider using native operating system packages first to avoid
installation problems and/or missing library support later.

FreeBSD Installation
^^^^^^^^^^^^^^^^^^^^

Pillow can be installed on FreeBSD via the official Ports or Packages systems:

**Ports**::

  $ cd /usr/ports/graphics/py-pillow && make install clean

**Packages**::

  $ pkg install py27-pillow

.. note::

    The `Pillow FreeBSD port
    <https://www.freshports.org/graphics/py-pillow/>`_ and packages
    are tested by the ports team with all supported FreeBSD versions
    and against Python 2.x and 3.x.


Building From Source
--------------------

Download and extract the `compressed archive from PyPI`_.

.. _compressed archive from PyPI: https://pypi.python.org/pypi/Pillow

.. _external-libraries:

External Libraries
^^^^^^^^^^^^^^^^^^

.. note::

    You **do not need to install all supported external libraries** to
    use Pillow's basic features. **Zlib** and **libjpeg** are required
    by default.

.. note::

   There are scripts to install the dependencies for some operating
   systems included in the ``depends`` directory.

Many of Pillow's features require external libraries:

* **libjpeg** provides JPEG functionality.

  * Pillow has been tested with libjpeg versions **6b**, **8**, **9**, **9a**,
    and **9b** and libjpeg-turbo version **8**.
  * Starting with Pillow 3.0.0, libjpeg is required by default, but
    may be disabled with the ``--disable-jpeg`` flag.

* **zlib** provides access to compressed PNGs

  * Starting with Pillow 3.0.0, zlib is required by default, but may
    be disabled with the ``--disable-zlib`` flag.

* **libtiff** provides compressed TIFF functionality

  * Pillow has been tested with libtiff versions **3.x** and **4.0**

* **libfreetype** provides type related services

* **littlecms** provides color management

  * Pillow version 2.2.1 and below uses liblcms1, Pillow 2.3.0 and
    above uses liblcms2. Tested with **1.19** and **2.7**.

* **libwebp** provides the WebP format.

  * Pillow has been tested with version **0.1.3**, which does not read
    transparent WebP files. Versions **0.3.0** and above support
    transparency.

* **tcl/tk** provides support for tkinter bitmap and photo images.

* **openjpeg** provides JPEG 2000 functionality.

  * Pillow has been tested with openjpeg **2.0.0** and **2.1.0**.
  * Pillow does **not** support the earlier **1.5** series which ships
    with Ubuntu and Debian.

* **libimagequant** provides improved color quantization

  * Pillow has been tested with libimagequant **2.6.0**
  * Libimagequant is licensed GPLv3, which is more restrictive than
    the Pillow license, therefore we will not be distributing binaries
    with libimagequant support enabled.
  * Windows support: Libimagequant requires VS2013/MSVC 18 to compile,
    so it is unlikely to work with any Python prior to 3.5 on Windows.

Once you have installed the prerequisites, run::

    $ pip install Pillow

If the prerequisites are installed in the standard library locations
for your machine (e.g. :file:`/usr` or :file:`/usr/local`), no
additional configuration should be required. If they are installed in
a non-standard location, you may need to configure setuptools to use
those locations by editing :file:`setup.py` or
:file:`setup.cfg`, or by adding environment variables on the command
line::

    $ CFLAGS="-I/usr/pkg/include" pip install pillow

If Pillow has been previously built without the required
prerequisites, it may be necessary to manually clear the pip cache or
build without cache using the ``--no-cache-dir`` option to force a
build with newly installed external libraries.


Build Options
^^^^^^^^^^^^^

* Environment Variable: ``MAX_CONCURRENCY=n``. By default, Pillow will
  use multiprocessing to build the extension on all available CPUs,
  but not more than 4. Setting ``MAX_CONCURRENCY`` to 1 will disable
  parallel building.

* Build flags: ``--disable-zlib``, ``--disable-jpeg``,
  ``--disable-tiff``, ``--disable-freetype``, ``--disable-tcl``,
  ``--disable-tk``, ``--disable-lcms``, ``--disable-webp``,
  ``--disable-webpmux``, ``--disable-jpeg2000``, ``--disable-imagequant``.
  Disable building the corresponding feature even if the development
  libraries are present on the building machine.

* Build flags: ``--enable-zlib``, ``--enable-jpeg``,
  ``--enable-tiff``, ``--enable-freetype``, ``--enable-tcl``,
  ``--enable-tk``, ``--enable-lcms``, ``--enable-webp``,
  ``--enable-webpmux``, ``--enable-jpeg2000``, ``--enable-imagequant``.
  Require that the corresponding feature is built. The build will raise
  an exception if the libraries are not found. Webpmux (WebP metadata)
  relies on WebP support. Tcl and Tk also must be used together.

* Build flag: ``--disable-platform-guessing``. Skips all of the
  platform dependent guessing of include and library directories for
  automated build systems that configure the proper paths in the
  environment variables (e.g. Buildroot).

* Build flag: ``--debug``. Adds a debugging flag to the include and
  library search process to dump all paths searched for and found to
  stdout.


Sample Usage::

    $ MAX_CONCURRENCY=1 python setup.py build_ext --enable-[feature] install

or using pip::

    $ pip install pillow --global-option="build_ext" --global-option="--enable-[feature]"


Building on macOS
^^^^^^^^^^^^^^^^^

The Xcode command line tools are required to compile portions of
Pillow. The tools are installed by running ``xcode-select --install``
from the command line. The command line tools are required even if you
have the full Xcode package installed.  It may be necessary to run
``sudo xcodebuild -license`` to accept the license prior to using the
tools.

The easiest way to install external libraries is via `Homebrew
<http://brew.sh/>`_. After you install Homebrew, run::

    $ brew install libtiff libjpeg webp little-cms2

Install Pillow with::

    $ pip install Pillow

or from within the uncompressed source directory::

    $ python setup.py install

Building on Windows
^^^^^^^^^^^^^^^^^^^

We don't recommend trying to build on Windows. It is a maze of twisty
passages, mostly dead ends. There are build scripts and notes for the
Windows build in the ``winbuild`` directory.

Building on FreeBSD
^^^^^^^^^^^^^^^^^^^

.. Note:: Only FreeBSD 10 tested

Make sure you have Python's development libraries installed.::

    $ sudo pkg install python2

Or for Python 3::

    $ sudo pkg install python3

Prerequisites are installed on **FreeBSD 10** with::

    $ sudo pkg install jpeg tiff webp lcms2 freetype2


Building on Linux
^^^^^^^^^^^^^^^^^

If you didn't build Python from source, make sure you have Python's
development libraries installed.

In Debian or Ubuntu::

    $ sudo apt-get install python-dev python-setuptools

Or for Python 3::

    $ sudo apt-get install python3-dev python3-setuptools

In Fedora, the command is::

    $ sudo dnf install python-devel redhat-rpm-config

Or for Python 3::

    $ sudo dnf install python3-devel redhat-rpm-config

.. Note:: ``redhat-rpm-config`` is required on Fedora 23, but not earlier versions.

Prerequisites are installed on **Ubuntu 12.04 LTS** or **Raspian Wheezy
7.0** with::

    $ sudo apt-get install libtiff4-dev libjpeg8-dev zlib1g-dev \
        libfreetype6-dev liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev python-tk

Prerequisites are installed on **Ubuntu 14.04 LTS** with::

    $ sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev \
        libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk

Prerequisites are installed on **Fedora 23** with::

    $ sudo dnf install libtiff-devel libjpeg-devel zlib-devel freetype-devel \
        lcms2-devel libwebp-devel tcl-devel tk-devel



Platform Support
----------------

Current platform support for Pillow. Binary distributions are contributed for
each release on a volunteer basis, but the source should compile and run
everywhere platform support is listed. In general, we aim to support all
current versions of Linux, macOS, and Windows.

.. note::

    Contributors please test Pillow on your platform then update this
    document and send a pull request.

+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
|**Operating system**              |**Supported**|**Tested Python versions**    |**Latest tested Pillow version**|**Tested processors**  |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Mac OS X 10.11 El Capitan        |Yes          | 2.7,3.3,3.4,3.5              | 3.4.1                          |x86-64                 |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Mac OS X 10.10 Yosemite          |Yes          | 2.7,3.3,3.4                  | 3.0.0                          |x86-64                 |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Mac OS X 10.9 Mavericks          |Yes          | 2.7,3.2,3.3,3.4              | 3.0.0                          |x86-64                 |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Mac OS X 10.8 Mountain Lion      |Yes          | 2.6,2.7,3.2,3.3              |                                |x86-64                 |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Redhat Linux 6                   |Yes          | 2.6                          |                                |x86                    |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| CentOS 6.3                       |Yes          | 2.7,3.3                      |                                |x86                    |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Fedora 23                        |Yes          | 2.7,3.4                      | 3.1.0                          |x86-64                 |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Ubuntu Linux 10.04 LTS           |Yes          | 2.6                          | 2.3.0                          |x86,x86-64             |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Ubuntu Linux 12.04 LTS           |Yes          | 2.6,2.7,3.2,3.3,3.4,3.5      | 3.4.1 (CI target)              |x86,x86-64             |
|                                  |             | PyPy5.3.1,PyPy3 v2.4.0       |                                |                       |
|                                  |             |                              |                                |                       |
|                                  |             | 2.7,3.2                      | 3.4.1                          |ppc                    |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Ubuntu Linux 14.04 LTS           |Yes          | 2.7,3.4                      | 3.1.0                          |x86-64                 |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Debian 8.2 Jessie                |Yes          | 2.7,3.4                      | 3.1.0                          |x86-64                 |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Raspian Jessie                   |Yes          | 2.7,3.4                      | 3.1.0                          |arm                    |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Gentoo Linux                     |Yes          | 2.7,3.2                      | 2.1.0                          |x86-64                 |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Arch Linux                       |Yes          | 2.7,3.5                      | 3.4.1                          |x86,x86-64             |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| FreeBSD 10.2                     |Yes          | 2.7,3.4                      | 3.1.0                          |x86-64                 |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Windows 7 Pro                    |Yes          | 2.7,3.2,3.3                  | 3.4.1                          |x86-64                 |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Windows Server 2008 R2 Enterprise|Yes          | 3.3                          |                                |x86-64                 |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Windows Server 2012 R2           |Yes          | 2.7,3.3,3.4                  | 3.4.1 (CI target)              |x86,x86-64             |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Windows 8 Pro                    |Yes          | 2.6,2.7,3.2,3.3,3.4a3        | 2.2.0                          |x86,x86-64             |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+
| Windows 8.1 Pro                  |Yes          | 2.6,2.7,3.2,3.3,3.4          | 2.4.0                          |x86,x86-64             |
+----------------------------------+-------------+------------------------------+--------------------------------+-----------------------+

Old Versions
------------

You can download old distributions from `PyPI
<https://pypi.python.org/pypi/Pillow>`_. Only the latest major
releases for Python 2.x and 3.x are visible, but all releases are
available by direct URL access
e.g. https://pypi.python.org/pypi/Pillow/1.0.
