.. _deprecations:

Deprecations and removals
=========================

This page lists Pillow features that are deprecated, or have been removed in
past major releases, and gives the alternatives to use instead.

Deprecated features
-------------------

Below are features which are considered deprecated. Where appropriate,
a ``DeprecationWarning`` is issued.

FreeType 2.7
~~~~~~~~~~~~

.. deprecated:: 8.1.0

Support for FreeType 2.7 is deprecated and will be removed in Pillow 9.0.0 (2022-01-02),
when FreeType 2.8 will be the minimum supported.

We recommend upgrading to at least FreeType `2.10.4`_, which fixed a severe
vulnerability introduced in FreeType 2.6 (:cve:`CVE-2020-15999`).

.. _2.10.4: https://sourceforge.net/projects/freetype/files/freetype2/2.10.4/

Tk/Tcl 8.4
~~~~~~~~~~

.. deprecated:: 8.2.0

Support for Tk/Tcl 8.4 is deprecated and will be removed in Pillow 10.0.0 (2023-01-02),
when Tk/Tcl 8.5 will be the minimum supported.

Categories
~~~~~~~~~~

.. deprecated:: 8.2.0

``im.category`` is deprecated and will be removed in Pillow 10.0.0 (2023-01-02),
along with the related ``Image.NORMAL``, ``Image.SEQUENCE`` and
``Image.CONTAINER`` attributes.

To determine if an image has multiple frames or not,
``getattr(im, "is_animated", False)`` can be used instead.

Image.show command parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 7.2.0

The ``command`` parameter will be removed in Pillow 9.0.0 (2022-01-02).
Use a subclass of :py:class:`.ImageShow.Viewer` instead.

Image._showxv
~~~~~~~~~~~~~

.. deprecated:: 7.2.0

``Image._showxv`` will be removed in Pillow 9.0.0 (2022-01-02).
Use :py:meth:`.Image.Image.show` instead. If custom behaviour is required, use
:py:func:`.ImageShow.register` to add a custom :py:class:`.ImageShow.Viewer` class.

ImageFile.raise_ioerror
~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 7.2.0

``IOError`` was merged into ``OSError`` in Python 3.3.
So, ``ImageFile.raise_ioerror`` will be removed in Pillow 9.0.0 (2022-01-02).
Use ``ImageFile.raise_oserror`` instead.

PILLOW_VERSION constant
~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 5.2.0

``PILLOW_VERSION`` will be removed in Pillow 9.0.0 (2022-01-02).
Use ``__version__`` instead.

It was initially removed in Pillow 7.0.0, but brought back in 7.1.0 to give projects
more time to upgrade.

Removed features
----------------

Deprecated features are only removed in major releases after an appropriate
period of deprecation has passed.

im.offset
~~~~~~~~~

.. deprecated:: 1.1.2
.. versionremoved:: 8.0.0

``im.offset()`` has been removed, call :py:func:`.ImageChops.offset()` instead.

It was documented as deprecated in PIL 1.1.2,
raised a ``DeprecationWarning`` since 1.1.5,
an ``Exception`` since Pillow 3.0.0
and ``NotImplementedError`` since 3.3.0.

Image.fromstring, im.fromstring and im.tostring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 2.0.0
.. versionremoved:: 8.0.0

* ``Image.fromstring()`` has been removed, call :py:func:`.Image.frombytes()` instead.
* ``im.fromstring()`` has been removed, call :py:meth:`~PIL.Image.Image.frombytes()` instead.
* ``im.tostring()`` has been removed, call :py:meth:`~PIL.Image.Image.tobytes()` instead.

They issued a ``DeprecationWarning`` since 2.0.0,
an ``Exception`` since 3.0.0
and ``NotImplementedError`` since 3.3.0.

ImageCms.CmsProfile attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 3.2.0
.. versionremoved:: 8.0.0

Some attributes in :py:class:`PIL.ImageCms.CmsProfile` have been removed. From 6.0.0,
they issued a ``DeprecationWarning``:

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

Previous method:

.. code-block:: python

    im = Image.open("hopper.png")
    im.save("out.jpg")

Use instead:

.. code-block:: python

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

PIL.OleFileIO was removed as a vendored file and in Pillow 4.0.0 (2017-01) in favour of
the upstream olefile Python package, and replaced with an ``ImportError`` in 5.0.0
(2018-01). The deprecated file has now been removed from Pillow. If needed, install from
PyPI (eg. ``python3 -m pip install olefile``).
