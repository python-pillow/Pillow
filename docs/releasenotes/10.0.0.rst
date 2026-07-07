10.0.0
------

Security
========

Limit size even if one dimension is zero
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When performing decompression bomb checks, Pillow did not reject images with
excessive width and zero height, or zero width and excessive height. That has
now been fixed.

This effectively dates to the PIL fork, since problem images would still have
been processed before Pillow started checking for decompression bombs.

.. _Added ImageFont.MAX_STRING_LENGTH:

:cve:`2023-44271`: Added ImageFont.MAX_STRING_LENGTH
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To protect against potential DOS attacks when using arbitrary strings as text
input, Pillow will now raise a :py:exc:`ValueError` if the number of characters
passed into ImageFont methods is over a certain limit,
:py:data:`PIL.ImageFont.MAX_STRING_LENGTH`.

This threshold can be changed by setting
:py:data:`PIL.ImageFont.MAX_STRING_LENGTH`. It can be disabled by setting
``ImageFont.MAX_STRING_LENGTH = None``.

Backwards incompatible changes
==============================

Categories
^^^^^^^^^^

``im.category`` has been removed, along with the related ``Image.NORMAL``,
``Image.SEQUENCE`` and ``Image.CONTAINER`` attributes.

To determine if an image has multiple frames or not,
``getattr(im, "is_animated", False)`` can be used instead.

Tk/Tcl 8.4
^^^^^^^^^^

Support for Tk/Tcl 8.4 has been removed.

JpegImagePlugin.convert_dict_qtables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Since deprecation in Pillow 8.3.0, the ``convert_dict_qtables`` method no longer
performed any operations on the data given to it, and has been removed.

ImagePalette size parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before Pillow 8.3.0, ``ImagePalette`` required palette data of particular lengths by
default, and the ``size`` parameter could be used to override that. Pillow 8.3.0
removed the default required length, also removing the need for the ``size`` parameter.

ImageShow.Viewer.show_file file argument
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``file`` argument in :py:meth:`~PIL.ImageShow.Viewer.show_file()` has been
removed and replaced by ``path``.

In effect, ``viewer.show_file("test.jpg")`` will continue to work unchanged.

Constants
^^^^^^^^^

A number of constants have been removed.
Instead, :py:class:`enum.IntEnum` classes have been added.

=====================================================  ============================================================
Removed                                                Use instead
=====================================================  ============================================================
``Image.LINEAR``                                       ``Image.BILINEAR`` or ``Image.Resampling.BILINEAR``
``Image.CUBIC``                                        ``Image.BICUBIC`` or ``Image.Resampling.BICUBIC``
``Image.ANTIALIAS``                                    ``Image.LANCZOS`` or ``Image.Resampling.LANCZOS``
``ImageCms.INTENT_PERCEPTUAL``                         ``ImageCms.Intent.PERCEPTUAL``
``ImageCms.INTENT_RELATIVE_COLORMETRIC``               ``ImageCms.Intent.RELATIVE_COLORMETRIC``
``ImageCms.INTENT_SATURATION``                         ``ImageCms.Intent.SATURATION``
``ImageCms.INTENT_ABSOLUTE_COLORIMETRIC``              ``ImageCms.Intent.ABSOLUTE_COLORIMETRIC``
``ImageCms.DIRECTION_INPUT``                           ``ImageCms.Direction.INPUT``
``ImageCms.DIRECTION_OUTPUT``                          ``ImageCms.Direction.OUTPUT``
``ImageCms.DIRECTION_PROOF``                           ``ImageCms.Direction.PROOF``
``ImageFont.LAYOUT_BASIC``                             ``ImageFont.Layout.BASIC``
``ImageFont.LAYOUT_RAQM``                              ``ImageFont.Layout.RAQM``
``BlpImagePlugin.BLP_FORMAT_JPEG``                     ``BlpImagePlugin.Format.JPEG``
``BlpImagePlugin.BLP_ENCODING_UNCOMPRESSED``           ``BlpImagePlugin.Encoding.UNCOMPRESSED``
``BlpImagePlugin.BLP_ENCODING_DXT``                    ``BlpImagePlugin.Encoding.DXT``
``BlpImagePlugin.BLP_ENCODING_UNCOMPRESSED_RAW_RGBA``  ``BlpImagePlugin.Encoding.UNCOMPRESSED_RAW_RGBA``
``BlpImagePlugin.BLP_ALPHA_ENCODING_DXT1``             ``BlpImagePlugin.AlphaEncoding.DXT1``
``BlpImagePlugin.BLP_ALPHA_ENCODING_DXT3``             ``BlpImagePlugin.AlphaEncoding.DXT3``
``BlpImagePlugin.BLP_ALPHA_ENCODING_DXT5``             ``BlpImagePlugin.AlphaEncoding.DXT5``
``FtexImagePlugin.FORMAT_DXT1``                        ``FtexImagePlugin.Format.DXT1``
``FtexImagePlugin.FORMAT_UNCOMPRESSED``                ``FtexImagePlugin.Format.UNCOMPRESSED``
``PngImagePlugin.APNG_DISPOSE_OP_NONE``                ``PngImagePlugin.Disposal.OP_NONE``
``PngImagePlugin.APNG_DISPOSE_OP_BACKGROUND``          ``PngImagePlugin.Disposal.OP_BACKGROUND``
``PngImagePlugin.APNG_DISPOSE_OP_PREVIOUS``            ``PngImagePlugin.Disposal.OP_PREVIOUS``
``PngImagePlugin.APNG_BLEND_OP_SOURCE``                ``PngImagePlugin.Blend.OP_SOURCE``
``PngImagePlugin.APNG_BLEND_OP_OVER``                  ``PngImagePlugin.Blend.OP_OVER``
=====================================================  ============================================================

FitsStubImagePlugin
^^^^^^^^^^^^^^^^^^^

The stub image plugin ``FitsStubImagePlugin`` has been removed.
FITS images can be read without a handler through :mod:`~PIL.FitsImagePlugin` instead.

Font size and offset methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Several functions for computing the size and offset of rendered text have been removed:

=============================================================== =============================================================================================================
Removed                                                         Use instead
=============================================================== =============================================================================================================
``FreeTypeFont.getsize()`` and ``FreeTypeFont.getoffset()``     :py:meth:`.FreeTypeFont.getbbox` and :py:meth:`.FreeTypeFont.getlength`
``FreeTypeFont.getsize_multiline()``                            :py:meth:`.ImageDraw.multiline_textbbox`
``ImageFont.getsize()``                                         :py:meth:`.ImageFont.getbbox` and :py:meth:`.ImageFont.getlength`
``TransposedFont.getsize()``                                    :py:meth:`.TransposedFont.getbbox` and :py:meth:`.TransposedFont.getlength`
``ImageDraw.textsize()`` and ``ImageDraw.multiline_textsize()`` :py:meth:`.ImageDraw.textbbox`, :py:meth:`.ImageDraw.textlength` and :py:meth:`.ImageDraw.multiline_textbbox`
``ImageDraw2.Draw.textsize()``                                  :py:meth:`.ImageDraw2.Draw.textbbox` and :py:meth:`.ImageDraw2.Draw.textlength`
=============================================================== =============================================================================================================

FreeTypeFont.getmask2 fill parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The undocumented ``fill`` parameter of :py:meth:`.FreeTypeFont.getmask2` has been
removed.

PhotoImage.paste box parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``box`` parameter was unused and has been removed.

PyQt5 and PySide2
^^^^^^^^^^^^^^^^^

`Qt 5 reached end-of-life <https://www.qt.io/blog/qt-5.15-released>`_ on 2020-12-08 for
open-source users (and will reach EOL on 2023-12-08 for commercial licence holders).

Support for PyQt5 and PySide2 has been removed from ``ImageQt``. Upgrade to
`PyQt6 <https://www.riverbankcomputing.com/static/Docs/PyQt6/>`_ or
`PySide6 <https://doc.qt.io/qtforpython-6/>`_ instead.

Image.coerce_e
^^^^^^^^^^^^^^

This undocumented method has been removed.

Deprecations
============

PyAccess and Image.USE_CFFI_ACCESS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Since Pillow's C API is now faster than PyAccess on PyPy,
:py:mod:`!PyAccess` has been deprecated and will be removed in Pillow
11.0.0 (2024-10-15). Pillow's C API will now be used by default on PyPy instead.

``Image.USE_CFFI_ACCESS``, for switching from the C API to PyAccess, is
similarly deprecated.

API changes
===========

Added line width parameter to ImageDraw regular_polygon
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An optional line ``width`` parameter has been added to
``ImageDraw.Draw.regular_polygon``.

API additions
=============

Added ``alpha_only`` argument to ``getbbox()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:meth:`~PIL.Image.Image.getbbox` now accepts a keyword argument of
``alpha_only``. This is an optional flag, defaulting to ``True``. If ``True``
and the image has an alpha channel, trim transparent pixels. Otherwise, trim
pixels when all channels are zero.

Other changes
=============

32-bit wheels
^^^^^^^^^^^^^

32-bit wheels are no longer provided.

Support display_jpeg() in IPython
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition to ``display()`` and ``display_png``, ``display_jpeg()`` can now
also be used to display images in IPython::

    from PIL import Image
    from IPython.display import display_jpeg

    im = Image.new("RGB", (100, 100), (255, 0, 0))
    display_jpeg(im)

Support reading signed 8-bit TIFF images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TIFF images with signed integer data, 8 bits per sample and a photometric
interpretation of BlackIsZero can now be read.
