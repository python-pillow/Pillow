.. py:module:: PIL.features
.. py:currentmodule:: PIL.features

:py:mod:`~PIL.features` module
==============================

The :py:mod:`PIL.features` module can be used to detect which Pillow features are available on your system.

.. autofunction:: PIL.features.pilinfo
.. autofunction:: PIL.features.check
.. autofunction:: PIL.features.version
.. autofunction:: PIL.features.get_supported

Modules
-------

Support for the following modules can be checked:

* ``pil``: The Pillow core module, required for all functionality.
* ``tkinter``: Tkinter support.
* ``freetype2``: FreeType font support via :py:func:`PIL.ImageFont.truetype`.
* ``littlecms2``: LittleCMS 2 support via :py:mod:`PIL.ImageCms`.
* ``webp``: WebP image support.
* ``avif``: AVIF image support.

.. autofunction:: PIL.features.check_module
.. autofunction:: PIL.features.version_module
.. autofunction:: PIL.features.get_supported_modules

Codecs
------

Support for these is only checked during Pillow compilation.
If the required library was uninstalled from the system, the ``pil`` core module may fail to load instead.
Except for ``jpg``, the version number is checked at run-time.

Support for the following codecs can be checked:

* ``jpg``: (compile time) Libjpeg support, required for JPEG based image formats. Only compile time version number is available.
* ``jpg_2000``: (compile time) OpenJPEG support, required for JPEG 2000 image formats.
* ``zlib``: (compile time) Zlib support, required for zlib compressed formats, such as PNG.
* ``libtiff``: (compile time) LibTIFF support, required for TIFF based image formats.

.. autofunction:: PIL.features.check_codec
.. autofunction:: PIL.features.version_codec
.. autofunction:: PIL.features.get_supported_codecs

Features
--------

Some of these are only checked during Pillow compilation.
If the required library was uninstalled from the system, the relevant module may fail to load instead.
Feature version numbers are available only where stated.

Support for the following features can be checked:

* ``libjpeg_turbo``: (compile time) Whether Pillow was compiled against the libjpeg-turbo version of libjpeg. Compile-time version number is available.
* ``mozjpeg``: (compile time) Whether Pillow was compiled against the MozJPEG version of libjpeg. Compile-time version number is available.
* ``zlib_ng``: (compile time) Whether Pillow was compiled against the zlib-ng version of zlib. Compile-time version number is available.
* ``raqm``: Raqm library, required for ``ImageFont.Layout.RAQM`` in :py:func:`PIL.ImageFont.truetype`. Run-time version number is available for Raqm 0.7.0 or newer.
* ``libimagequant``: (compile time) ImageQuant quantization support in :py:func:`PIL.Image.Image.quantize`. Run-time version number is available.
* ``xcb``: (compile time) Support for X11 in :py:func:`PIL.ImageGrab.grab` via the XCB library.
* ``transp_webp``: Deprecated. Always ``True`` if WebP module is installed.
* ``webp_mux``: Deprecated. Always ``True`` if WebP module is installed.
* ``webp_anim``: Deprecated. Always ``True`` if WebP module is installed.

.. autofunction:: PIL.features.check_feature
.. autofunction:: PIL.features.version_feature
.. autofunction:: PIL.features.get_supported_features
