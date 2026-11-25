Third-party plugins
===================

Pillow's plugin model lets other projects add support for more image formats,
without any changes to Pillow itself. To write your own, see
:doc:`writing-your-own-image-plugin`. These PyPI projects provide plugins:

* :pypi:`amigainfo`: Adds support for Amiga Workbench .info icon files.
* :pypi:`amos-abk`: AMOS BASIC sprite and image banks.
* :pypi:`heif-image-plugin`: Simple HEIF/HEIC images plugin, based on the pyheif library.
* :pypi:`jxlpy`: Introduces reading and writing support for JPEG XL.
* :pypi:`pi-heif`: A light version of pillow-heif, with a more permissive license for binary wheels.
* :pypi:`pillow-degas`: Adds reading Atari ST Degas image files.
* :pypi:`pillow-heif`: Python bindings to libheif for working with HEIF images.
* :pypi:`pillow-jpls`: Plugin for the JPEG-LS codec, based on the Charls JPEG-LS implementation. Python bindings implemented using pybind11.
* :pypi:`pillow-jxl-plugin`: Plugin for JPEG-XL, using Rust for bindings.
* :pypi:`pillow-lunasvg`: SVG read support based on the LunaSVG C++ library. Wheels for Linux, macOS and Windows, no system libraries needed.
* :pypi:`pillow-mbm`: Adds support for KSP's proprietary MBM texture format.
* :pypi:`pillow-minecraft-map`: Loading, saving and color-quantizing Minecraft .dat map files.
* :pypi:`pillow-netpbm`: Adds .pam support, and loads images using `Netpbm <https://en.wikipedia.org/wiki/Netpbm>`__'s converter collection.
* :pypi:`pillow-wmf`: Cross platform support for Windows MetaFiles.
* :pypi:`pillow-zx-spectrum`: Open loading SCREEN$ from ZX Spectrum tapes, disks and memory snapshots.
* :pypi:`pylibheif`: Python bindings for libheif, with a plugin for HEIC, HEIF and AVIF images.
* :pypi:`wsq`: Adds support for WSQ fingerprint images, based on the NBIS library.

Emeritus
--------

.. list-table::
    :header-rows: 1

    * - Project
      - Reason
    * - :pypi:`DjvuRleImagePlugin`
      - Does not work with Pillow 10.1.0 and later.
    * - :pypi:`pillow-avif-plugin`
      - Describes itself as a plugin until official support was added. Pillow now
        supports AVIF.
    * - :pypi:`pillow-stackblur`
      - Does not add support for an image format.
    * - :pypi:`pillow-svg`
      - Requires Pillow earlier than 9.0.0.
    * - :pypi:`pyheif-pillow-opener`
      - Discontinued.
    * - :pypi:`raw-pillow-opener`
      - Requires rawpy 0.16.0, which cannot be installed on supported Python versions.
