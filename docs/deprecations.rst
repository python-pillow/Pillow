.. _deprecations:

Deprecations and removals
=========================

This page lists Pillow features that are deprecated, or have been removed in
past major releases, and gives the alternatives to use instead.

Deprecated features
-------------------

Below are features which are considered deprecated. Where appropriate,
a :py:exc:`DeprecationWarning` is issued.

ImageFile.raise_oserror
~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 10.2.0

``ImageFile.raise_oserror()`` has been deprecated and will be removed in Pillow
12.0.0 (2025-10-15). The function is undocumented and is only useful for translating
error codes returned by a codec's ``decode()`` method, which ImageFile already does
automatically.

IptcImageFile helper functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 10.2.0

The functions ``IptcImageFile.dump`` and ``IptcImageFile.i``, and the constant
``IptcImageFile.PAD`` have been deprecated and will be removed in Pillow
12.0.0 (2025-10-15). These are undocumented helper functions intended
for internal use, so there is no replacement. They can each be replaced
by a single line of code using builtin functions in Python.

ImageCms constants and versions() function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 10.3.0

A number of constants and a function in :py:mod:`.ImageCms` have been deprecated.
This includes a table of flags based on LittleCMS version 1 which has been
replaced with a new class :py:class:`.ImageCms.Flags` based on LittleCMS 2 flags.

============================================  ====================================================
Deprecated                                    Use instead
============================================  ====================================================
``ImageCms.DESCRIPTION``                      No replacement
``ImageCms.VERSION``                          ``PIL.__version__``
``ImageCms.FLAGS["MATRIXINPUT"]``             :py:attr:`.ImageCms.Flags.CLUT_POST_LINEARIZATION`
``ImageCms.FLAGS["MATRIXOUTPUT"]``            :py:attr:`.ImageCms.Flags.FORCE_CLUT`
``ImageCms.FLAGS["MATRIXONLY"]``              No replacement
``ImageCms.FLAGS["NOWHITEONWHITEFIXUP"]``     :py:attr:`.ImageCms.Flags.NOWHITEONWHITEFIXUP`
``ImageCms.FLAGS["NOPRELINEARIZATION"]``      :py:attr:`.ImageCms.Flags.CLUT_PRE_LINEARIZATION`
``ImageCms.FLAGS["GUESSDEVICECLASS"]``        :py:attr:`.ImageCms.Flags.GUESSDEVICECLASS`
``ImageCms.FLAGS["NOTCACHE"]``                :py:attr:`.ImageCms.Flags.NOCACHE`
``ImageCms.FLAGS["NOTPRECALC"]``              :py:attr:`.ImageCms.Flags.NOOPTIMIZE`
``ImageCms.FLAGS["NULLTRANSFORM"]``           :py:attr:`.ImageCms.Flags.NULLTRANSFORM`
``ImageCms.FLAGS["HIGHRESPRECALC"]``          :py:attr:`.ImageCms.Flags.HIGHRESPRECALC`
``ImageCms.FLAGS["LOWRESPRECALC"]``           :py:attr:`.ImageCms.Flags.LOWRESPRECALC`
``ImageCms.FLAGS["GAMUTCHECK"]``              :py:attr:`.ImageCms.Flags.GAMUTCHECK`
``ImageCms.FLAGS["WHITEBLACKCOMPENSATION"]``  :py:attr:`.ImageCms.Flags.BLACKPOINTCOMPENSATION`
``ImageCms.FLAGS["BLACKPOINTCOMPENSATION"]``  :py:attr:`.ImageCms.Flags.BLACKPOINTCOMPENSATION`
``ImageCms.FLAGS["SOFTPROOFING"]``            :py:attr:`.ImageCms.Flags.SOFTPROOFING`
``ImageCms.FLAGS["PRESERVEBLACK"]``           :py:attr:`.ImageCms.Flags.NONEGATIVES`
``ImageCms.FLAGS["NODEFAULTRESOURCEDEF"]``    :py:attr:`.ImageCms.Flags.NODEFAULTRESOURCEDEF`
``ImageCms.FLAGS["GRIDPOINTS"]``              :py:attr:`.ImageCms.Flags.GRIDPOINTS()`
``ImageCms.versions()``                       :py:func:`PIL.features.version_module` with
                                              ``feature="littlecms2"``, :py:data:`sys.version` or
                                              :py:data:`sys.version_info`, and ``PIL.__version__``
============================================  ====================================================

ImageMath eval()
^^^^^^^^^^^^^^^^

.. deprecated:: 10.3.0

``ImageMath.eval()`` has been deprecated. Use :py:meth:`~PIL.ImageMath.lambda_eval` or
:py:meth:`~PIL.ImageMath.unsafe_eval` instead.

BGR;15, BGR 16 and BGR;24
^^^^^^^^^^^^^^^^^^^^^^^^^

.. deprecated:: 10.4.0

The experimental BGR;15, BGR;16 and BGR;24 modes have been deprecated.

Non-image modes in ImageCms
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. deprecated:: 10.4.0

The use in :py:mod:`.ImageCms` of input modes and output modes that are not Pillow
image modes has been deprecated. Defaulting to "L" or "1" if the mode cannot be mapped
is also deprecated.

Support for LibTIFF earlier than 4
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. deprecated:: 10.4.0

Support for LibTIFF earlier than version 4 has been deprecated.
Upgrade to a newer version of LibTIFF instead.

ImageDraw.getdraw hints parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. deprecated:: 10.4.0

The ``hints`` parameter in :py:meth:`~PIL.ImageDraw.getdraw()` has been deprecated.

FreeType 2.9.0
^^^^^^^^^^^^^^

.. deprecated:: 11.0.0

Support for FreeType 2.9.0 is deprecated and will be removed in Pillow 12.0.0
(2025-10-15), when FreeType 2.9.1 will be the minimum supported.

We recommend upgrading to at least FreeType `2.10.4`_, which fixed a severe
vulnerability introduced in FreeType 2.6 (:cve:`2020-15999`).

.. _2.10.4: https://sourceforge.net/projects/freetype/files/freetype2/2.10.4/

ICNS (width, height, scale) sizes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. deprecated:: 11.0.0

Setting an ICNS image size to ``(width, height, scale)`` before loading has been
deprecated. Instead, ``load(scale)`` can be used.

Image isImageType()
^^^^^^^^^^^^^^^^^^^

.. deprecated:: 11.0.0

``Image.isImageType(im)`` has been deprecated. Use ``isinstance(im, Image.Image)``
instead.

ImageMath.lambda_eval and ImageMath.unsafe_eval options parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. deprecated:: 11.0.0

The ``options`` parameter in :py:meth:`~PIL.ImageMath.lambda_eval()` and
:py:meth:`~PIL.ImageMath.unsafe_eval()` has been deprecated. One or more keyword
arguments can be used instead.

JpegImageFile.huffman_ac and JpegImageFile.huffman_dc
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. deprecated:: 11.0.0

The ``huffman_ac`` and ``huffman_dc`` dictionaries on JPEG images were unused. They
have been deprecated, and will be removed in Pillow 12 (2025-10-15).

Specific WebP Feature Checks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. deprecated:: 11.0.0

``features.check("transp_webp")``, ``features.check("webp_mux")`` and
``features.check("webp_anim")`` are now deprecated. They will always return
``True`` if the WebP module is installed, until they are removed in Pillow
12.0.0 (2025-10-15).

Removed features
----------------

Deprecated features are only removed in major releases after an appropriate
period of deprecation has passed.

TiffImagePlugin IFD_LEGACY_API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionremoved:: 11.0.0

``TiffImagePlugin.IFD_LEGACY_API`` was removed, as it was an unused setting.

PSFile
~~~~~~

.. deprecated:: 9.5.0
.. versionremoved:: 11.0.0

The :py:class:`!PSFile` class was removed in Pillow 11 (2024-10-15).
This class was only made as a helper to be used internally,
so there is no replacement. If you need this functionality though,
it is a very short class that can easily be recreated in your own code.

PyAccess and Image.USE_CFFI_ACCESS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 10.0.0
.. versionremoved:: 11.0.0

Since Pillow's C API is now faster than PyAccess on PyPy, ``PyAccess`` has been
removed. Pillow's C API will now be used on PyPy instead.

``Image.USE_CFFI_ACCESS``, for switching from the C API to PyAccess, was
similarly removed.

Tk/Tcl 8.4
~~~~~~~~~~

.. deprecated:: 8.2.0
.. versionremoved:: 10.0.0

Support for Tk/Tcl 8.4 was removed in Pillow 10.0.0 (2023-07-01).

Categories
~~~~~~~~~~

.. deprecated:: 8.2.0
.. versionremoved:: 10.0.0

``im.category`` was removed along with the related ``Image.NORMAL``,
``Image.SEQUENCE`` and ``Image.CONTAINER`` attributes.

To determine if an image has multiple frames or not,
``getattr(im, "is_animated", False)`` can be used instead.

JpegImagePlugin.convert_dict_qtables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 8.3.0
.. versionremoved:: 10.0.0

Since deprecation in Pillow 8.3.0, the ``convert_dict_qtables`` method no longer
performed any operations on the data given to it, and has been removed.

ImagePalette size parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 8.4.0
.. versionremoved:: 10.0.0

Before Pillow 8.3.0, ``ImagePalette`` required palette data of particular lengths by
default, and the ``size`` parameter could be used to override that. Pillow 8.3.0
removed the default required length, also removing the need for the ``size`` parameter.

ImageShow.Viewer.show_file file argument
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 9.1.0
.. versionremoved:: 10.0.0

The ``file`` argument in :py:meth:`~PIL.ImageShow.Viewer.show_file()` has been
removed and replaced by ``path``.

In effect, ``viewer.show_file("test.jpg")`` will continue to work unchanged.

Constants
~~~~~~~~~

.. deprecated:: 9.1.0
.. versionremoved:: 10.0.0

A number of constants have been removed.
Instead, :py:class:`enum.IntEnum` classes have been added.

.. note::

    Additional ``Image`` constants were deprecated in Pillow 9.1.0, but that
    was reversed in Pillow 9.4.0 and those constants will now remain available.
    See :ref:`restored-image-constants`

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
~~~~~~~~~~~~~~~~~~~

.. deprecated:: 9.1.0
.. versionremoved:: 10.0.0

The stub image plugin ``FitsStubImagePlugin`` has been removed.
FITS images can be read without a handler through :mod:`~PIL.FitsImagePlugin` instead.

Font size and offset methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 9.2.0
.. versionremoved:: 10.0.0

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

Previous code::

    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf")
    width, height = font.getsize("Hello world")
    left, top = font.getoffset("Hello world")

    im = Image.new("RGB", (100, 100))
    draw = ImageDraw.Draw(im)
    width, height = draw.textsize("Hello world", font)

    width, height = font.getsize_multiline("Hello\nworld")
    width, height = draw.multiline_textsize("Hello\nworld", font)

Use instead::

    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf")
    left, top, right, bottom = font.getbbox("Hello world")
    width, height = right - left, bottom - top

    im = Image.new("RGB", (100, 100))
    draw = ImageDraw.Draw(im)
    width = draw.textlength("Hello world", font)

    left, top, right, bottom = draw.multiline_textbbox((0, 0), "Hello\nworld", font)
    width, height = right - left, bottom - top

Previously, the ``size`` methods returned a ``height`` that included the vertical
offset of the text, while the new ``bbox`` methods distinguish this as a ``top``
offset.

.. image:: ./example/size_vs_bbox.webp
    :alt: In bbox methods, top measures the vertical distance above the text, while bottom measures that plus the vertical distance of the text itself. In size methods, height also measures the vertical distance above the text plus the vertical distance of the text itself.
    :align: center

If you are using these methods for aligning text, consider using :ref:`text-anchors` instead
which avoid issues that can occur with non-English text or unusual fonts.
For example, instead of the following code::

    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf")

    im = Image.new("RGB", (100, 100))
    draw = ImageDraw.Draw(im)
    width, height = draw.textsize("Hello world", font)
    x, y = (100 - width) / 2, (100 - height) / 2
    draw.text((x, y), "Hello world", font=font)

Use instead::

    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf")

    im = Image.new("RGB", (100, 100))
    draw = ImageDraw.Draw(im)
    draw.text((100 / 2, 100 / 2), "Hello world", font=font, anchor="mm")

FreeTypeFont.getmask2 fill parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 9.2.0
.. versionremoved:: 10.0.0

The undocumented ``fill`` parameter of :py:meth:`.FreeTypeFont.getmask2` has been
removed.

PhotoImage.paste box parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 9.2.0
.. versionremoved:: 10.0.0

The ``box`` parameter was unused and has been removed.

PyQt5 and PySide2
~~~~~~~~~~~~~~~~~

.. deprecated:: 9.2.0
.. versionremoved:: 10.0.0

`Qt 5 reached end-of-life <https://www.qt.io/blog/qt-5.15-released>`_ on 2020-12-08 for
open-source users (and will reach EOL on 2023-12-08 for commercial licence holders).

Support for PyQt5 and PySide2 has been removed from ``ImageQt``. Upgrade to
`PyQt6 <https://www.riverbankcomputing.com/static/Docs/PyQt6/>`_ or
`PySide6 <https://doc.qt.io/qtforpython-6/>`_ instead.

Image.coerce_e
~~~~~~~~~~~~~~

.. deprecated:: 9.2.0
.. versionremoved:: 10.0.0

This undocumented method has been removed.

PILLOW_VERSION constant
~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 5.2.0
.. versionremoved:: 9.0.0

Use ``__version__`` instead.

It was initially removed in Pillow 7.0.0, but temporarily brought back in 7.1.0
to give projects more time to upgrade.

Image.show command parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 7.2.0
.. versionremoved:: 9.0.0

The ``command`` parameter has been removed. Use a subclass of
:py:class:`.ImageShow.Viewer` instead.

Image._showxv
~~~~~~~~~~~~~

.. deprecated:: 7.2.0
.. versionremoved:: 9.0.0

Use :py:meth:`.Image.Image.show` instead. If custom behaviour is required, use
:py:func:`.ImageShow.register` to add a custom :py:class:`.ImageShow.Viewer` class.

ImageFile.raise_ioerror
~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 7.2.0
.. versionremoved:: 9.0.0

:py:exc:`IOError` was merged into :py:exc:`OSError` in Python 3.3.
So, ``ImageFile.raise_ioerror`` has been removed.
Use ``ImageFile.raise_oserror`` instead.

FreeType 2.7
~~~~~~~~~~~~

.. deprecated:: 8.1.0
.. versionremoved:: 9.0.0

Support for FreeType 2.7 has been removed.

We recommend upgrading to at least `FreeType`_ 2.10.4, which fixed a severe
vulnerability introduced in FreeType 2.6 (:cve:`2020-15999`).

.. _FreeType: https://freetype.org/

im.offset
~~~~~~~~~

.. deprecated:: 1.1.2
.. versionremoved:: 8.0.0

``im.offset()`` has been removed, call :py:func:`.ImageChops.offset()` instead.

It was documented as deprecated in PIL 1.1.2,
raised a :py:exc:`DeprecationWarning` since 1.1.5,
an :py:exc:`Exception` since Pillow 3.0.0
and :py:exc:`NotImplementedError` since 3.3.0.

Image.fromstring, im.fromstring and im.tostring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 2.0.0
.. versionremoved:: 8.0.0

* ``Image.fromstring()`` has been removed, call :py:func:`.Image.frombytes()` instead.
* ``im.fromstring()`` has been removed, call :py:meth:`~PIL.Image.Image.frombytes()` instead.
* ``im.tostring()`` has been removed, call :py:meth:`~PIL.Image.Image.tobytes()` instead.

They issued a :py:exc:`DeprecationWarning` since 2.0.0,
an :py:exc:`Exception` since 3.0.0
and :py:exc:`NotImplementedError` since 3.3.0.

ImageCms.CmsProfile attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 3.2.0
.. versionremoved:: 8.0.0

Some attributes in :py:class:`PIL.ImageCms.core.CmsProfile` have been removed.
From 6.0.0, they issued a :py:exc:`DeprecationWarning`:

========================  ===================================================
Removed                   Use instead
========================  ===================================================
``color_space``           Padded :py:attr:`~.CmsProfile.xcolor_space`
``pcs``                   Padded :py:attr:`~.CmsProfile.connection_space`
``product_copyright``     Unicode :py:attr:`~.CmsProfile.copyright`
``product_desc``          Unicode :py:attr:`~.CmsProfile.profile_description`
``product_description``   Unicode :py:attr:`~.CmsProfile.profile_description`
``product_manufacturer``  Unicode :py:attr:`~.CmsProfile.manufacturer`
``product_model``         Unicode :py:attr:`~.CmsProfile.model`
========================  ===================================================

Python 2.7
~~~~~~~~~~

.. deprecated:: 6.0.0
.. versionremoved:: 7.0.0

Python 2.7 reached end-of-life on 2020-01-01. Pillow 6.x was the last series to
support Python 2.

Image.__del__
~~~~~~~~~~~~~

.. deprecated:: 6.1.0
.. versionremoved:: 7.0.0

Implicitly closing the image's underlying file in ``Image.__del__`` has been removed.
Use a context manager or call ``Image.close()`` instead to close the file in a
deterministic way.

Previous method::

    im = Image.open("hopper.png")
    im.save("out.jpg")

Use instead::

    with Image.open("hopper.png") as im:
        im.save("out.jpg")

PIL.*ImagePlugin.__version__ attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 6.0.0
.. versionremoved:: 7.0.0

The version constants of individual plugins have been removed. Use ``PIL.__version__``
instead.

===============================  =================================  ==================================
Removed                          Removed                            Removed
===============================  =================================  ==================================
``BmpImagePlugin.__version__``   ``Jpeg2KImagePlugin.__version__``  ``PngImagePlugin.__version__``
``CurImagePlugin.__version__``   ``JpegImagePlugin.__version__``    ``PpmImagePlugin.__version__``
``DcxImagePlugin.__version__``   ``McIdasImagePlugin.__version__``  ``PsdImagePlugin.__version__``
``EpsImagePlugin.__version__``   ``MicImagePlugin.__version__``     ``SgiImagePlugin.__version__``
``FliImagePlugin.__version__``   ``MpegImagePlugin.__version__``    ``SunImagePlugin.__version__``
``FpxImagePlugin.__version__``   ``MpoImagePlugin.__version__``     ``TgaImagePlugin.__version__``
``GdImageFile.__version__``      ``MspImagePlugin.__version__``     ``TiffImagePlugin.__version__``
``GifImagePlugin.__version__``   ``PalmImagePlugin.__version__``    ``WmfImagePlugin.__version__``
``IcoImagePlugin.__version__``   ``PcdImagePlugin.__version__``     ``XbmImagePlugin.__version__``
``ImImagePlugin.__version__``    ``PcxImagePlugin.__version__``     ``XpmImagePlugin.__version__``
``ImtImagePlugin.__version__``   ``PdfImagePlugin.__version__``     ``XVThumbImagePlugin.__version__``
``IptcImagePlugin.__version__``  ``PixarImagePlugin.__version__``
===============================  =================================  ==================================

PyQt4 and PySide
~~~~~~~~~~~~~~~~

.. deprecated:: 6.0.0
.. versionremoved:: 7.0.0

Qt 4 reached end-of-life on 2015-12-19. Its Python bindings are also EOL: PyQt4 since
2018-08-31 and PySide since 2015-10-14.

Support for PyQt4 and PySide has been removed  from ``ImageQt``. Please upgrade to PyQt5
or PySide2.

Setting the size of TIFF images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 5.3.0
.. versionremoved:: 7.0.0

Setting the size of a TIFF image directly (eg. ``im.size = (256, 256)``) throws
an error. Use ``Image.resize`` instead.

VERSION constant
~~~~~~~~~~~~~~~~

.. deprecated:: 5.2.0
.. versionremoved:: 6.0.0

``VERSION`` (the old PIL version, always 1.1.7) has been removed. Use
``__version__`` instead.

Undocumented ImageOps functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 4.3.0
.. versionremoved:: 6.0.0

Several undocumented functions in ``ImageOps`` have been removed. Use the equivalents
in ``ImageFilter`` instead:

==========================  ============================
Removed                     Use instead
==========================  ============================
``ImageOps.box_blur``       ``ImageFilter.BoxBlur``
``ImageOps.gaussian_blur``  ``ImageFilter.GaussianBlur``
``ImageOps.gblur``          ``ImageFilter.GaussianBlur``
``ImageOps.usm``            ``ImageFilter.UnsharpMask``
``ImageOps.unsharp_mask``   ``ImageFilter.UnsharpMask``
==========================  ============================

PIL.OleFileIO
~~~~~~~~~~~~~

.. deprecated:: 4.0.0
.. versionremoved:: 6.0.0

``PIL.OleFileIO`` was removed as a vendored file in Pillow 4.0.0 (2017-01) in favour of
the upstream :pypi:`olefile` Python package, and replaced with an :py:exc:`ImportError` in 5.0.0
(2018-01). The deprecated file has now been removed from Pillow. If needed, install from
PyPI (eg. ``python3 -m pip install olefile``).

import _imaging
~~~~~~~~~~~~~~~

.. versionremoved:: 2.1.0

Pillow >= 2.1.0 no longer supports ``import _imaging``.
Please use ``from PIL.Image import core as _imaging`` instead.

Pillow and PIL
~~~~~~~~~~~~~~

.. versionremoved:: 1.0.0

Pillow and PIL cannot co-exist in the same environment.
Before installing Pillow, please uninstall PIL.

import Image
~~~~~~~~~~~~

.. versionremoved:: 1.0.0

Pillow >= 1.0 no longer supports ``import Image``.
Please use ``from PIL import Image`` instead.
