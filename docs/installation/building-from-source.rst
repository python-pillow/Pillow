.. raw:: html

    <script>
    document.addEventListener('DOMContentLoaded', function() {
      activateTab(getOS());
    });
    </script>

.. _building-from-source:

Building from source
====================

.. _external-libraries:

External libraries
------------------

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

  * Pillow has been tested with libjpeg versions **6b**, **8**, **9-9d** and
    libjpeg-turbo version **8**.
  * Starting with Pillow 3.0.0, libjpeg is required by default. It can be
    disabled with the ``-C jpeg=disable`` flag.

* **zlib** provides access to compressed PNGs

  * Starting with Pillow 3.0.0, zlib is required by default. It can be
    disabled with the ``-C zlib=disable`` flag.

* **libtiff** provides compressed TIFF functionality

  * Pillow has been tested with libtiff versions **3.x** and **4.0-4.7.0**

* **libfreetype** provides type related services

* **littlecms** provides color management

  * Pillow version 2.2.1 and below uses liblcms1, Pillow 2.3.0 and
    above uses liblcms2. Tested with **1.19** and **2.7-2.17**.

* **libwebp** provides the WebP format.

* **openjpeg** provides JPEG 2000 functionality.

  * Pillow has been tested with openjpeg **2.0.0**, **2.1.0**, **2.3.1**,
    **2.4.0**, **2.5.0**, **2.5.2** and **2.5.3**.
  * Pillow does **not** support the earlier **1.5** series which ships
    with Debian Jessie.

* **libimagequant** provides improved color quantization

  * Pillow has been tested with libimagequant **2.6-4.3.4**
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
  * Setting text direction or font features is not supported without libraqm.
  * Pillow wheels since version 8.2.0 include a modified version of libraqm that
    loads libfribidi at runtime if it is installed.
    On Windows this requires compiling FriBiDi and installing ``fribidi.dll``
    into a directory listed in the `Dynamic-link library search order (Microsoft Learn)
    <https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order#search-order-for-unpackaged-apps>`_
    (``fribidi-0.dll`` or ``libfribidi-0.dll`` are also detected).
    See `Build Options`_ to see how to build this version.
  * Previous versions of Pillow (5.0.0 to 8.1.2) linked libraqm dynamically at runtime.

* **libxcb** provides X11 screengrab support.

* **libavif** provides support for the AVIF format.

  * Pillow requires libavif version **1.0.0** or greater.
  * libavif is merely an API that wraps AVIF codecs. If you are compiling
    libavif from source, you will also need to install both an AVIF encoder
    and decoder, such as rav1e and dav1d, or libaom, which both encodes and
    decodes AVIF images.

.. tab:: Linux

    If you didn't build Python from source, make sure you have Python's
    development libraries installed.

    In Debian or Ubuntu::

        sudo apt-get install python3-dev python3-setuptools

    In Fedora, the command is::

        sudo dnf install python3-devel redhat-rpm-config

    In Alpine, the command is::

        sudo apk add python3-dev py3-setuptools

    .. Note:: ``redhat-rpm-config`` is required on Fedora 23, but not earlier versions.

    Prerequisites for **Ubuntu 16.04 LTS - 22.04 LTS** are installed with::

        sudo apt-get install libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev \
            libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
            libharfbuzz-dev libfribidi-dev libxcb1-dev

    To install libraqm, ``sudo apt-get install meson`` and then see
    ``depends/install_raqm.sh``.

    Build prerequisites for libavif on Ubuntu are installed with::

        sudo apt-get install cmake ninja-build nasm

    Then see ``depends/install_libavif.sh`` to build and install libavif.

    Prerequisites are installed on recent **Red Hat**, **CentOS** or **Fedora** with::

        sudo dnf install libtiff-devel libjpeg-devel openjpeg2-devel zlib-devel \
            freetype-devel lcms2-devel libwebp-devel tcl-devel tk-devel \
            harfbuzz-devel fribidi-devel libraqm-devel libimagequant-devel libxcb-devel

    Note that the package manager may be yum or DNF, depending on the
    exact distribution.

    Prerequisites are installed for **Alpine** with::

        sudo apk add tiff-dev jpeg-dev openjpeg-dev zlib-dev freetype-dev lcms2-dev \
            libwebp-dev tcl-dev tk-dev harfbuzz-dev fribidi-dev libimagequant-dev \
            libxcb-dev libpng-dev

    See also the ``Dockerfile``\s in the Test Infrastructure repo
    (https://github.com/python-pillow/docker-images) for a known working
    install process for other tested distros.

.. tab:: macOS

    The Xcode command line tools are required to compile portions of
    Pillow. The tools are installed by running ``xcode-select --install``
    from the command line. The command line tools are required even if you
    have the full Xcode package installed.  It may be necessary to run
    ``sudo xcodebuild -license`` to accept the license prior to using the
    tools.

    The easiest way to install external libraries is via `Homebrew
    <https://brew.sh/>`_. After you install Homebrew, run::

        brew install libavif libjpeg libraqm libtiff little-cms2 openjpeg webp

    If you would like to use libavif with more codecs than just aom, then
    instead of installing libavif through Homebrew directly, you can use
    Homebrew to install libavif's build dependencies::

        brew install aom dav1d rav1e svt-av1

    Then see ``depends/install_libavif.sh`` to install libavif.

.. tab:: Windows

    We recommend you use prebuilt wheels from PyPI.
    If you wish to compile Pillow manually, you can use the build scripts
    in the ``winbuild`` directory used for CI testing and development.
    These scripts require Visual Studio 2017 or newer and NASM.

    The scripts also install Pillow from the local copy of the source code, so the
    `Installing`_ instructions will not be necessary afterwards.

.. tab:: Windows using MSYS2/MinGW

    To build Pillow using MSYS2, make sure you run the **MSYS2 MinGW 32-bit** or
    **MSYS2 MinGW 64-bit** console, *not* **MSYS2** directly.

    The following instructions target the 64-bit build, for 32-bit
    replace all occurrences of ``mingw-w64-x86_64-`` with ``mingw-w64-i686-``.

    Make sure you have Python and GCC installed::

        pacman -S \
            mingw-w64-x86_64-gcc \
            mingw-w64-x86_64-python \
            mingw-w64-x86_64-python-pip \
            mingw-w64-x86_64-python-setuptools

    Prerequisites are installed on **MSYS2 MinGW 64-bit** with::

        pacman -S \
            mingw-w64-x86_64-libjpeg-turbo \
            mingw-w64-x86_64-zlib \
            mingw-w64-x86_64-libtiff \
            mingw-w64-x86_64-freetype \
            mingw-w64-x86_64-lcms2 \
            mingw-w64-x86_64-libwebp \
            mingw-w64-x86_64-openjpeg2 \
            mingw-w64-x86_64-libimagequant \
            mingw-w64-x86_64-libraqm \
            mingw-w64-x86_64-libavif

.. tab:: FreeBSD

    .. Note:: Only FreeBSD 10 and 11 tested

    Make sure you have Python's development libraries installed::

        sudo pkg install python3

    Prerequisites are installed on **FreeBSD 10 or 11** with::

        sudo pkg install jpeg-turbo tiff webp lcms2 freetype2 openjpeg harfbuzz fribidi libxcb libavif

    Then see ``depends/install_raqm_cmake.sh`` to install libraqm.

.. tab:: Android

    Basic Android support has been added for compilation within the Termux
    environment. The dependencies can be installed by::

        pkg install -y python ndk-sysroot clang make \
            libjpeg-turbo

    This has been tested within the Termux app on ChromeOS, on x86.

Installing
----------

Once you have installed the prerequisites, to install Pillow from the source
code on PyPI, run::

    python3 -m pip install --upgrade pip
    python3 -m pip install --upgrade Pillow --no-binary :all:

If the prerequisites are installed in the standard library locations
for your machine (e.g. :file:`/usr` or :file:`/usr/local`), no
additional configuration should be required. If they are installed in
a non-standard location, you may need to configure setuptools to use
those locations by editing :file:`setup.py` or
:file:`pyproject.toml`, or by adding environment variables on the command
line::

    CFLAGS="-I/usr/pkg/include" python3 -m pip install --upgrade Pillow --no-binary :all:

If Pillow has been previously built without the required
prerequisites, it may be necessary to manually clear the pip cache or
build without cache using the ``--no-cache-dir`` option to force a
build with newly installed external libraries.

If you would like to install from a local copy of the source code instead, you
can clone from GitHub with ``git clone https://github.com/python-pillow/Pillow``
or download and extract the `compressed archive from PyPI`_.

After navigating to the Pillow directory, run::

    python3 -m pip install --upgrade pip
    python3 -m pip install .

.. _compressed archive from PyPI: https://pypi.org/project/pillow/#files

Build options
^^^^^^^^^^^^^

* Config setting: ``-C parallel=n``. Can also be given
  with environment variable: ``MAX_CONCURRENCY=n``. Pillow can use
  multiprocessing to build the extension. Setting ``-C parallel=n``
  sets the number of CPUs to use to ``n``, or can disable parallel building by
  using a setting of 1. By default, it uses 4 CPUs, or if 4 are not
  available, as many as are present.

* Config settings: ``-C zlib=disable``, ``-C jpeg=disable``,
  ``-C tiff=disable``, ``-C freetype=disable``, ``-C raqm=disable``,
  ``-C lcms=disable``, ``-C webp=disable``,
  ``-C jpeg2000=disable``, ``-C imagequant=disable``, ``-C xcb=disable``,
  ``-C avif=disable``.
  Disable building the corresponding feature even if the development
  libraries are present on the building machine.

* Config settings: ``-C zlib=enable``, ``-C jpeg=enable``,
  ``-C tiff=enable``, ``-C freetype=enable``, ``-C raqm=enable``,
  ``-C lcms=enable``, ``-C webp=enable``,
  ``-C jpeg2000=enable``, ``-C imagequant=enable``, ``-C xcb=enable``,
  ``-C avif=enable``.
  Require that the corresponding feature is built. The build will raise
  an exception if the libraries are not found. Tcl and Tk must be used
  together.

* Config settings: ``-C raqm=vendor``, ``-C fribidi=vendor``.
  These flags are used to compile a modified version of libraqm and
  a shim that dynamically loads libfribidi at runtime. These are
  used to compile the standard Pillow wheels. Compiling libraqm requires
  a C99-compliant compiler.

* Config setting: ``-C platform-guessing=disable``. Skips all of the
  platform dependent guessing of include and library directories for
  automated build systems that configure the proper paths in the
  environment variables (e.g. Buildroot).

* Config setting: ``-C debug=true``. Adds a debugging flag to the include and
  library search process to dump all paths searched for and found to stdout.


Sample usage::

    python3 -m pip install --upgrade Pillow -C [feature]=enable

.. _old-versions:

Old versions
============

You can download old distributions from the `release history at PyPI
<https://pypi.org/project/pillow/#history>`_ and by direct URL access
eg. https://pypi.org/project/pillow/1.0/.
