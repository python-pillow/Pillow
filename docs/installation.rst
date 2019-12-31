Installation
============

Warnings
--------

.. warning:: Pillow and PIL cannot co-exist in the same environment. Before installing Pillow, please uninstall PIL.

.. warning:: Pillow >= 1.0 no longer supports "import Image". Please use "from PIL import Image" instead.

.. warning:: Pillow >= 2.1.0 no longer supports "import _imaging". Please use "from PIL.Image import core as _imaging" instead.

Notes
-----

.. note:: Pillow is supported on the following Python versions


+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
|**Python**         |**3.8**|**3.7**|**3.6**|**3.5**|**3.4**|**3.3**|**3.2**|**2.7**|**2.6**|**2.5**|**2.4**|
+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
|Pillow >= 7        |  Yes  |  Yes  |  Yes  |  Yes  |       |       |       |       |       |       |       |
+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
|Pillow 6.2.1       |  Yes  |  Yes  |  Yes  |  Yes  |       |       |       |  Yes  |       |       |       |
+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
|Pillow 6.0 - 6.2.0 |       |  Yes  |  Yes  |  Yes  |       |       |       |  Yes  |       |       |       |
+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
|Pillow 5.2 - 5.4   |       |  Yes  |  Yes  |  Yes  |  Yes  |       |       |  Yes  |       |       |       |
+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
|Pillow 5.0 - 5.1   |       |       |  Yes  |  Yes  |  Yes  |       |       |  Yes  |       |       |       |
+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
|Pillow 4           |       |       |  Yes  |  Yes  |  Yes  |  Yes  |       |  Yes  |       |       |       |
+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
|Pillow 2 - 3       |       |       |       |  Yes  |  Yes  |  Yes  |  Yes  |  Yes  |  Yes  |       |       |
+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
|Pillow < 2         |       |       |       |       |       |       |       |  Yes  |  Yes  |  Yes  |  Yes  |
+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+

Basic Installation
------------------

.. note::

    The following instructions will install Pillow with support for
    most common image formats. See :ref:`external-libraries` for a
    full list of external libraries supported.

Install Pillow with :command:`pip`::

    python -m pip install pip
    python -m pip install Pillow


Windows Installation
^^^^^^^^^^^^^^^^^^^^

We provide Pillow binaries for Windows compiled for the matrix of
supported Pythons in both 32 and 64-bit versions in wheel, egg, and
executable installers. These binaries have all of the optional
libraries included except for raqm and libimagequant::

    python -m pip install pip
    python -m pip install Pillow


macOS Installation
^^^^^^^^^^^^^^^^^^

We provide binaries for macOS for each of the supported Python
versions in the wheel format. These include support for all optional
libraries except libimagequant.  Raqm support requires libraqm,
fribidi, and harfbuzz to be installed separately::

    python -m pip install pip
    python -m pip install Pillow

Linux Installation
^^^^^^^^^^^^^^^^^^

We provide binaries for Linux for each of the supported Python
versions in the manylinux wheel format. These include support for all
optional libraries except libimagequant. Raqm support requires
libraqm, fribidi, and harfbuzz to be installed separately::

    python -m pip install pip
    python -m pip install Pillow

Most major Linux distributions, including Fedora, Debian/Ubuntu and
ArchLinux also include Pillow in packages that previously contained
PIL e.g. ``python-imaging``.

FreeBSD Installation
^^^^^^^^^^^^^^^^^^^^

Pillow can be installed on FreeBSD via the official Ports or Packages systems:

**Ports**::

  cd /usr/ports/graphics/py-pillow && make install clean

**Packages**::

  pkg install py36-pillow

.. note::

    The `Pillow FreeBSD port
    <https://www.freshports.org/graphics/py-pillow/>`_ and packages
    are tested by the ports team with all supported FreeBSD versions.


Building From Source
--------------------

Download and extract the `compressed archive from PyPI`_.

.. _compressed archive from PyPI: https://pypi.org/project/Pillow/

.. _external-libraries:

External Libraries
^^^^^^^^^^^^^^^^^^

.. note::

    You **do not need to install all supported external libraries** to
    use Pillow's basic features. **Zlib** and **libjpeg** are required
    by default.

.. note::

   There are Dockerfiles in our `Docker images repo
   <https://github.com/python-pillow/docker-images>`_ to install the
   dependencies for some operating systems.

Many of Pillow's features require external libraries:

* **libjpeg** provides JPEG functionality.

  * Pillow has been tested with libjpeg versions **6b**, **8**, **9-9c** and
    libjpeg-turbo version **8**.
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
    above uses liblcms2. Tested with **1.19** and **2.7-2.9**.

* **libwebp** provides the WebP format.

  * Pillow has been tested with version **0.1.3**, which does not read
    transparent WebP files. Versions **0.3.0** and above support
    transparency.

* **tcl/tk** provides support for tkinter bitmap and photo images.

* **openjpeg** provides JPEG 2000 functionality.

  * Pillow has been tested with openjpeg **2.0.0**, **2.1.0** and **2.3.1**.
  * Pillow does **not** support the earlier **1.5** series which ships
    with Debian Jessie.

* **libimagequant** provides improved color quantization

  * Pillow has been tested with libimagequant **2.6-2.12.6**
  * Libimagequant is licensed GPLv3, which is more restrictive than
    the Pillow license, therefore we will not be distributing binaries
    with libimagequant support enabled.

* **libraqm** provides complex text layout support.

  * libraqm provides bidirectional text support (using FriBiDi),
    shaping (using HarfBuzz), and proper script itemization. As a
    result, Raqm can support most writing systems covered by Unicode.
  * libraqm depends on the following libraries: FreeType, HarfBuzz,
    FriBiDi, make sure that you install them before installing libraqm
    if not available as package in your system.
  * setting text direction or font features is not supported without
    libraqm.
  * libraqm is dynamically loaded in Pillow 5.0.0 and above, so support
    is available if all the libraries are installed.
  * Windows support: Raqm is not included in prebuilt wheels

Once you have installed the prerequisites, run::

    python -m pip install pip
    python -m pip install Pillow

If the prerequisites are installed in the standard library locations
for your machine (e.g. :file:`/usr` or :file:`/usr/local`), no
additional configuration should be required. If they are installed in
a non-standard location, you may need to configure setuptools to use
those locations by editing :file:`setup.py` or
:file:`setup.cfg`, or by adding environment variables on the command
line::

    CFLAGS="-I/usr/pkg/include" python -m pip install pillow

If Pillow has been previously built without the required
prerequisites, it may be necessary to manually clear the pip cache or
build without cache using the ``--no-cache-dir`` option to force a
build with newly installed external libraries.


Build Options
^^^^^^^^^^^^^

* Environment variable: ``MAX_CONCURRENCY=n``. Pillow can use
  multiprocessing to build the extension. Setting ``MAX_CONCURRENCY``
  sets the number of CPUs to use, or can disable parallel building by
  using a setting of 1. By default, it uses 4 CPUs, or if 4 are not
  available, as many as are present.

* Build flags: ``--disable-zlib``, ``--disable-jpeg``,
  ``--disable-tiff``, ``--disable-freetype``, ``--disable-lcms``,
  ``--disable-webp``, ``--disable-webpmux``, ``--disable-jpeg2000``,
  ``--disable-imagequant``.
  Disable building the corresponding feature even if the development
  libraries are present on the building machine.

* Build flags: ``--enable-zlib``, ``--enable-jpeg``,
  ``--enable-tiff``, ``--enable-freetype``, ``--enable-lcms``,
  ``--enable-webp``, ``--enable-webpmux``, ``--enable-jpeg2000``,
  ``--enable-imagequant``.
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


Sample usage::

    MAX_CONCURRENCY=1 python setup.py build_ext --enable-[feature] install

or using pip::

    python -m pip install pillow --global-option="build_ext" --global-option="--enable-[feature]"


Building on macOS
^^^^^^^^^^^^^^^^^

The Xcode command line tools are required to compile portions of
Pillow. The tools are installed by running ``xcode-select --install``
from the command line. The command line tools are required even if you
have the full Xcode package installed.  It may be necessary to run
``sudo xcodebuild -license`` to accept the license prior to using the
tools.

The easiest way to install external libraries is via `Homebrew
<https://brew.sh/>`_. After you install Homebrew, run::

    brew install libtiff libjpeg webp little-cms2

To install libraqm on macOS use Homebrew to install its dependencies::

    brew install freetype harfbuzz fribidi

Then see ``depends/install_raqm_cmake.sh`` to install libraqm.

Now install Pillow with::

    python -m pip install pip
    python -m pip install Pillow

or from within the uncompressed source directory::

    python setup.py install

Building on Windows
^^^^^^^^^^^^^^^^^^^

We don't recommend trying to build on Windows. It is a maze of twisty
passages, mostly dead ends. There are build scripts and notes for the
Windows build in the ``winbuild`` directory.

Building on FreeBSD
^^^^^^^^^^^^^^^^^^^

.. Note:: Only FreeBSD 10 and 11 tested

Make sure you have Python's development libraries installed::

    sudo pkg install python2

Or for Python 3::

    sudo pkg install python3

Prerequisites are installed on **FreeBSD 10 or 11** with::

    sudo pkg install jpeg-turbo tiff webp lcms2 freetype2 openjpeg harfbuzz fribidi

Then see ``depends/install_raqm_cmake.sh`` to install libraqm.


Building on Linux
^^^^^^^^^^^^^^^^^

If you didn't build Python from source, make sure you have Python's
development libraries installed.

In Debian or Ubuntu::

    sudo apt-get install python-dev python-setuptools

Or for Python 3::

    sudo apt-get install python3-dev python3-setuptools

In Fedora, the command is::

    sudo dnf install python-devel redhat-rpm-config

Or for Python 3::

    sudo dnf install python3-devel redhat-rpm-config

.. Note:: ``redhat-rpm-config`` is required on Fedora 23, but not earlier versions.

Prerequisites are installed on **Ubuntu 16.04 LTS** with::

    sudo apt-get install libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev \
        libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
        libharfbuzz-dev libfribidi-dev

Then see ``depends/install_raqm.sh`` to install libraqm.

Prerequisites are installed on recent **RedHat** **Centos** or **Fedora** with::

    sudo dnf install libtiff-devel libjpeg-devel openjpeg2-devel zlib-devel \
        freetype-devel lcms2-devel libwebp-devel tcl-devel tk-devel \
        harfbuzz-devel fribidi-devel libraqm-devel libimagequant-devel

Note that the package manager may be yum or dnf, depending on the
exact distribution.

See also the ``Dockerfile``\s in the Test Infrastructure repo
(https://github.com/python-pillow/docker-images) for a known working
install process for other tested distros.

Building on Android
^^^^^^^^^^^^^^^^^^^

Basic Android support has been added for compilation within the Termux
environment. The dependencies can be installed by::

    pkg install -y python ndk-sysroot clang make \
        libjpeg-turbo

This has been tested within the Termux app on ChromeOS, on x86.


Platform Support
----------------

Current platform support for Pillow. Binary distributions are
contributed for each release on a volunteer basis, but the source
should compile and run everywhere platform support is listed. In
general, we aim to support all current versions of Linux, macOS, and
Windows.

Continuous Integration Targets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These platforms are built and tested for every change.

+----------------------------------+--------------------------+-----------------------+
|**Operating system**              |**Tested Python versions**|**Tested architecture**|
+----------------------------------+--------------------------+-----------------------+
| Alpine                           | 3.7                      |x86-64                 |
+----------------------------------+--------------------------+-----------------------+
| Arch                             | 3.7                      |x86-64                 |
+----------------------------------+--------------------------+-----------------------+
| Amazon Linux 1                   | 3.6                      |x86-64                 |
+----------------------------------+--------------------------+-----------------------+
| Amazon Linux 2                   | 3.6                      |x86-64                 |
+----------------------------------+--------------------------+-----------------------+
| CentOS 6                         | 3.6                      |x86-64                 |
+----------------------------------+--------------------------+-----------------------+
| CentOS 7                         | 3.6                      |x86-64                 |
+----------------------------------+--------------------------+-----------------------+
| CentOS 8                         | 3.6                      |x86-64                 |
+----------------------------------+--------------------------+-----------------------+
| Debian 9 Stretch                 | 3.5                      |x86                    |
+----------------------------------+--------------------------+-----------------------+
| Debian 10 Buster                 | 3.7                      |x86                    |
+----------------------------------+--------------------------+-----------------------+
| Fedora 30                        | 3.7                      |x86-64                 |
+----------------------------------+--------------------------+-----------------------+
| Fedora 31                        | 3.7                      |x86-64                 |
+----------------------------------+--------------------------+-----------------------+
| macOS 10.13 High Sierra          | 3.5, 3.6, 3.7, 3.8       |x86-64                 |
+----------------------------------+--------------------------+-----------------------+
| macOS 10.15 Catalina             | PyPy3                    |x86-64                 |
+----------------------------------+--------------------------+-----------------------+
| Ubuntu Linux 16.04 LTS           | 3.5, 3.6, 3.7, 3.8, PyPy3|x86-64                 |
+----------------------------------+--------------------------+-----------------------+
| Windows Server 2012 R2           | 3.5, 3.8                 |x86, x86-64            |
|                                  +--------------------------+-----------------------+
|                                  | PyPy3, 3.7/MinGW         |x86                    |
+----------------------------------+--------------------------+-----------------------+
| Windows Server 2019              | 3.5, 3.6, 3.7, 3.8       |x86, x86-64            |
|                                  +--------------------------+-----------------------+
|                                  | PyPy3                    |x86                    |
+----------------------------------+--------------------------+-----------------------+


Other Platforms
^^^^^^^^^^^^^^^

These platforms have been reported to work at the versions mentioned.

.. note::

    Contributors please test Pillow on your platform then update this
    document and send a pull request.

+----------------------------------+------------------------------+--------------------------------+-----------------------+
|**Operating system**              |**Tested Python versions**    |**Latest tested Pillow version**|**Tested processors**  |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| macOS 10.14 Mojave               | 2.7, 3.5, 3.6, 3.7           | 6.0.0                          |x86-64                 |
|                                  +------------------------------+--------------------------------+                       +
|                                  | 3.4                          | 5.4.1                          |                       |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| macOS 10.13 High Sierra          | 2.7, 3.4, 3.5, 3.6           | 4.2.1                          |x86-64                 |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| macOS 10.12 Sierra               | 2.7, 3.4, 3.5, 3.6           | 4.1.1                          |x86-64                 |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| Mac OS X 10.11 El Capitan        | 2.7, 3.4, 3.5, 3.6, 3.7      | 5.4.1                          |x86-64                 |
|                                  +------------------------------+--------------------------------+                       +
|                                  | 3.3                          | 4.1.0                          |                       |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| Mac OS X 10.9 Mavericks          | 2.7, 3.2, 3.3, 3.4           | 3.0.0                          |x86-64                 |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| Mac OS X 10.8 Mountain Lion      | 2.6, 2.7, 3.2, 3.3           |                                |x86-64                 |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| Redhat Linux 6                   | 2.6                          |                                |x86                    |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| CentOS 6.3                       | 2.7, 3.3                     |                                |x86                    |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| Fedora 23                        | 2.7, 3.4                     | 3.1.0                          |x86-64                 |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| Ubuntu Linux 12.04 LTS           | 2.6, 3.2, 3.3, 3.4, 3.5      | 3.4.1                          |x86,x86-64             |
|                                  | PyPy5.3.1, PyPy3 v2.4.0      |                                |                       |
|                                  +------------------------------+--------------------------------+-----------------------+
|                                  | 2.7                          | 4.3.0                          |x86-64                 |
|                                  +------------------------------+--------------------------------+-----------------------+
|                                  | 2.7, 3.2                     | 3.4.1                          |ppc                    |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| Ubuntu Linux 10.04 LTS           | 2.6                          | 2.3.0                          |x86,x86-64             |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| Debian 8.2 Jessie                | 2.7, 3.4                     | 3.1.0                          |x86-64                 |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| Raspbian Jessie                  | 2.7, 3.4                     | 3.1.0                          |arm                    |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| Raspbian Stretch                 | 2.7, 3.5                     | 4.0.0                          |arm                    |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| Gentoo Linux                     | 2.7, 3.2                     | 2.1.0                          |x86-64                 |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| FreeBSD 11.1                     | 2.7, 3.4, 3.5, 3.6           | 4.3.0                          |x86-64                 |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| FreeBSD 10.3                     | 2.7, 3.4, 3.5                | 4.2.0                          |x86-64                 |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| FreeBSD 10.2                     | 2.7, 3.4                     | 3.1.0                          |x86-64                 |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| Windows 8.1 Pro                  | 2.6, 2.7, 3.2, 3.3, 3.4      | 2.4.0                          |x86,x86-64             |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| Windows 8 Pro                    | 2.6, 2.7, 3.2, 3.3, 3.4a3    | 2.2.0                          |x86,x86-64             |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| Windows 7 Pro                    | 2.7, 3.2, 3.3                | 3.4.1                          |x86-64                 |
+----------------------------------+------------------------------+--------------------------------+-----------------------+
| Windows Server 2008 R2 Enterprise| 3.3                          |                                |x86-64                 |
+----------------------------------+------------------------------+--------------------------------+-----------------------+

Old Versions
------------

You can download old distributions from the `release history at PyPI
<https://pypi.org/project/Pillow/#history>`_ and by direct URL access
eg. https://pypi.org/project/Pillow/1.0/.
