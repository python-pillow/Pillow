.. _deprecations:

Deprecations and removals
=========================

This page lists Pillow features that are deprecated, or have been removed in
past major releases, and gives the alternatives to use instead.

Deprecated features
-------------------

Below are features which are considered deprecated. Where appropriate,
a ``DeprecationWarning`` is issued.

ImageCms.CmsProfile attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 3.2.0

Some attributes in ``ImageCms.CmsProfile`` are deprecated. From 6.0.0, they issue a
``DeprecationWarning``:

========================  ===============================
Deprecated                Use instead
========================  ===============================
``color_space``           Padded ``xcolor_space``
``pcs``                   Padded ``connection_space``
``product_copyright``     Unicode ``copyright``
``product_desc``          Unicode ``profile_description``
``product_description``   Unicode ``profile_description``
``product_manufacturer``  Unicode ``manufacturer``
``product_model``         Unicode ``model``
========================  ===============================

Removed features
----------------

Deprecated features are only removed in major releases after an appropriate
period of deprecation has passed.

Python 2.7
~~~~~~~~~~

*Removed in version 7.0.0.*

Python 2.7 reached end-of-life on 2020-01-01. Pillow 6.x was the last series to
support Python 2.

Image.__del__
~~~~~~~~~~~~~

*Removed in version 7.0.0.*

Implicitly closing the image's underlying file in ``Image.__del__`` has been removed.
Use a context manager or call ``Image.close()`` instead to close the file in a
deterministic way.

Previous method:

.. code-block:: python

    im = Image.open("hopper.png")
    im.save("out.jpg")

Use instead:

.. code-block:: python

    with Image.open("hopper.png") as im:
        im.save("out.jpg")

PILLOW_VERSION constant
~~~~~~~~~~~~~~~~~~~~~~~

*Removed in version 7.0.0.*

``PILLOW_VERSION`` has been removed. Use ``__version__`` instead.

PIL.*ImagePlugin.__version__ attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Removed in version 7.0.0.*

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

*Removed in version 7.0.0.*

Qt 4 reached end-of-life on 2015-12-19. Its Python bindings are also EOL: PyQt4 since
2018-08-31 and PySide since 2015-10-14.

Support for PyQt4 and PySide has been removed  from ``ImageQt``. Please upgrade to PyQt5
or PySide2.

Setting the size of TIFF images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Removed in version 7.0.0.*

Setting the size of a TIFF image directly (eg. ``im.size = (256, 256)``) throws
an error. Use ``Image.resize`` instead.

VERSION constant
~~~~~~~~~~~~~~~~

*Removed in version 6.0.0.*

``VERSION`` (the old PIL version, always 1.1.7) has been removed. Use
``__version__`` instead.

Undocumented ImageOps functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Removed in version 6.0.0.*

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

*Removed in version 6.0.0.*

PIL.OleFileIO was removed as a vendored file and in Pillow 4.0.0 (2017-01) in favour of
the upstream olefile Python package, and replaced with an ``ImportError`` in 5.0.0
(2018-01). The deprecated file has now been removed from Pillow. If needed, install from
PyPI (eg. ``pip install olefile``).
