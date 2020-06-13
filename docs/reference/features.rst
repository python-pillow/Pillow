.. py:module:: PIL.features
.. py:currentmodule:: PIL.features

:py:mod:`features` Module
==========================

The :py:mod:`PIL.features` module can be used to detect which Pillow features are available on your system.

.. autofunction:: PIL.features.pilinfo
.. autofunction:: PIL.features.check
.. autofunction:: PIL.features.get_supported

Modules
-------

Support for the following modules can be checked:

* ``pil``: The Pillow core module, required for all functionality.
* ``tkinter``: Tkinter support.
* ``freetype2``: FreeType font support via :py:func:`PIL.ImageFont.truetype`.
* ``littlecms2``: LittleCMS 2 support via :py:mod:`PIL.ImageCms`.
* ``webp``: WebP image support.

.. autofunction:: PIL.features.check_module
.. autofunction:: PIL.features.get_supported_modules

Codecs
------

These are only checked during Pillow compilation.
If the required library was uninstalled from the system, the ``pil`` core module may fail to load instead.

Support for the following codecs can be checked:

* ``jpg``: (compile time) Libjpeg support, required for JPEG based image formats.
* ``jpg_2000``: (compile time) OpenJPEG support, required for JPEG 2000 image formats.
* ``zlib``: (compile time) Zlib support, required for zlib compressed formats, such as PNG.
* ``libtiff``: (compile time) LibTIFF support, required for TIFF based image formats.

.. autofunction:: PIL.features.check_codec
.. autofunction:: PIL.features.get_supported_codecs

Features
--------

Some of these are only checked during Pillow compilation.
If the required library was uninstalled from the system, the relevant module may fail to load instead.

Support for the following features can be checked:

* ``libjpeg_turbo``: (compile time) Whether Pillow was compiled against the libjpeg-turbo version of libjpeg.
* ``transp_webp``: Support for transparency in WebP images.
* ``webp_mux``: (compile time) Support for EXIF data in WebP images.
* ``webp_anim``: (compile time) Support for animated WebP images.
* ``raqm``: Raqm library, required for ``ImageFont.LAYOUT_RAQM`` in :py:func:`PIL.ImageFont.truetype`.
* ``libimagequant``: (compile time) ImageQuant quantization support in :py:func:`PIL.Image.Image.quantize`.
* ``xcb``: (compile time) Support for X11 in :py:func:`PIL.ImageGrab.grab` via the XCB library.

.. autofunction:: PIL.features.check_feature
.. autofunction:: PIL.features.get_supported_features
