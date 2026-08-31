.. raw:: html

    <script>
    document.addEventListener('DOMContentLoaded', function() {
      activateTab(getOS());
    });
    </script>

.. _basic-installation:

Basic installation
==================

.. note::

    The following instructions will install Pillow with support for
    most common image formats. See :ref:`external-libraries` for a
    full list of external libraries supported.

Install Pillow with :command:`pip`::

    python3 -m pip install --upgrade pip
    python3 -m pip install --upgrade Pillow

Optionally, install :pypi:`defusedxml` for Pillow to read XMP data,
and :pypi:`olefile` for Pillow to read FPX and MIC images::

    python3 -m pip install --upgrade defusedxml olefile


.. tab:: Linux

    We provide binaries for Linux for each of the supported Python
    versions in the manylinux wheel format. These include support for all
    optional libraries except libimagequant. Raqm support requires
    FriBiDi to be installed separately::

        python3 -m pip install --upgrade pip
        python3 -m pip install --upgrade Pillow

    Most major Linux distributions, including Fedora, Ubuntu and ArchLinux
    also include Pillow in packages that previously contained PIL e.g.
    ``python-imaging``. Debian splits it into two packages, ``python3-pil``
    and ``python3-pil.imagetk``.

.. tab:: macOS

    We provide binaries for macOS for each of the supported Python
    versions in the wheel format. These include support for all optional
    libraries except libimagequant. Raqm support requires
    FriBiDi to be installed separately::

        python3 -m pip install --upgrade pip
        python3 -m pip install --upgrade Pillow

    While we provide binaries for both x86-64 and arm64, we do not provide universal2
    binaries. However, it is simple to combine our current binaries to create one::

        python3 -m pip download --only-binary=:all: --platform macosx_10_10_x86_64 Pillow
        python3 -m pip download --only-binary=:all: --platform macosx_11_0_arm64 Pillow
        python3 -m pip install delocate

    Then, with the names of the downloaded wheels, use Python to combine them::

        from delocate.fuse import fuse_wheels
        fuse_wheels('Pillow-9.4.0-2-cp39-cp39-macosx_10_10_x86_64.whl', 'Pillow-9.4.0-cp39-cp39-macosx_11_0_arm64.whl', 'Pillow-9.4.0-cp39-cp39-macosx_11_0_universal2.whl')

.. tab:: Windows

    We provide Pillow binaries for Windows compiled for the matrix of supported
    Pythons in the wheel format. These include x86, x86-64 and arm64 versions.
    These binaries include support
    for all optional libraries except libimagequant and libxcb. Raqm support
    requires FriBiDi to be installed separately::

        python3 -m pip install --upgrade pip
        python3 -m pip install --upgrade Pillow

    To install Pillow in MSYS2, see :ref:`building-from-source`.

.. tab:: FreeBSD

    Pillow can be installed on FreeBSD via the official Ports or Packages systems:

    **Ports**::

        cd /usr/ports/graphics/py-pillow && make install clean

    **Packages**::

        pkg install py38-pillow

    .. note::

        The `Pillow FreeBSD port
        <https://www.freshports.org/graphics/py-pillow/>`_ and packages
        are tested by the ports team with all supported FreeBSD versions.
