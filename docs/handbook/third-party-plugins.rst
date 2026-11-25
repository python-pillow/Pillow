Third-party plugins
===================

Pillow's plugin model lets other projects add support for more image formats,
without any changes to Pillow itself. To write your own, see
:doc:`writing-your-own-image-plugin`. These PyPI projects provide plugins:

.. list-table::
    :header-rows: 1

    * - Project
      - Description
    * - :pypi:`amigainfo`
      - Amiga Workbench .info icon files.
    * - :pypi:`amos-abk`
      - AMOS BASIC sprite and image banks.
    * - :pypi:`heif-image-plugin`
      - HEIF/HEIC and AVIF images, based on pyheif.
    * - :pypi:`jxlpy`
      - Reading and writing JPEG XL images.
    * - :pypi:`pi-heif`
      - A light version of pillow-heif, with a more permissive license for binary wheels.
    * - :pypi:`pillow-degas`
      - Reading Atari ST DEGAS images.
    * - :pypi:`pillow-heif`
      - HEIF images, based on libheif.
    * - :pypi:`pillow-jpls`
      - JPEG-LS images, based on CharLS.
    * - :pypi:`pillow-jxl-plugin`
      - JPEG XL images, with Rust bindings.
    * - :pypi:`pillow-lunasvg`
      - Reading SVG images, based on LunaSVG. No system libraries needed.
    * - :pypi:`pillow-mbm`
      - Kerbal Space Program's MBM texture format.
    * - :pypi:`pillow-minecraft-map`
      - Loading, saving and color-quantizing Minecraft .dat map files.
    * - :pypi:`pillow-netpbm`
      - PAM images, and loading other formats through `Netpbm
        <https://en.wikipedia.org/wiki/Netpbm>`__'s converters.
    * - :pypi:`pillow-wmf`
      - Windows Metafile (WMF) images on any platform.
    * - :pypi:`pillow-zx-spectrum`
      - Loading SCREEN$ images from ZX Spectrum tapes, disks and memory snapshots.
    * - :pypi:`pylibheif`
      - Python bindings for libheif, with a plugin for HEIC, HEIF and AVIF images.
    * - :pypi:`wsq`
      - Adds support for WSQ fingerprint images, based on the NBIS library.

Other
-----

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
