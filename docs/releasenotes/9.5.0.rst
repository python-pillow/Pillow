9.5.0
-----

Security
========

Clear PPM half token after use
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Image files that are small on disk are often prevented from expanding to be
big images consuming a large amount of resources simply because they lack the
data to populate those resources.

PpmImagePlugin might hold onto the last data read for a pixel value in case the
pixel value has not been finished yet. However, that data was not being cleared
afterwards, meaning that infinite data could be available to fill any image
size. This has been present since Pillow 9.2.0.

That data is now cleared after use.

Saving TIFF tag ImageSourceData
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If Pillow incorrectly saved the TIFF tag ImageSourceData as ASCII instead of
UNDEFINED, a segmentation fault was triggered.

The correct tag type will now be used by default instead.

Deprecations
============

PSFile
^^^^^^

The :py:class:`!PSFile` class has been deprecated and will
be removed in Pillow 11 (2024-10-15). This class was only made as a helper to
be used internally, so there is no replacement. If you need this functionality
though, it is a very short class that can easily be recreated in your own code.

API additions
=============

QOI file format
^^^^^^^^^^^^^^^

Pillow can now read images in Quite OK Image format.

Added ``dpi`` argument when saving PDFs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When saving a PDF, resolution could already be specified using the
``resolution`` argument. Now, a tuple of ``(x_resolution, y_resolution)`` can
be provided as ``dpi``. If both are provided, ``dpi`` will override
``resolution``.

Added ``corners`` argument to ``ImageDraw.rounded_rectangle()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:meth:`.ImageDraw.rounded_rectangle` now accepts a keyword argument of
``corners``. This a tuple of Booleans, specifying whether to round each corner,
``(top_left, top_right, bottom_right, bottom_left)``.

JPEG2000 comments and PLT marker
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When opening a JPEG2000 image, the comment may now be read into
:py:attr:`~PIL.Image.Image.info`. The ``comment`` keyword argument can be used
to save it back again.

If OpenJPEG 2.4.0 or later is available and the ``plt`` keyword argument
is present and true when saving JPEG2000 images, tell the encoder to generate
PLT markers.

Other changes
=============

Added support for saving PDFs in RGBA mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using the JPXDecode filter, PDFs can now be saved in RGBA mode.

Improved I;16N support
^^^^^^^^^^^^^^^^^^^^^^

Support has been added for I;16N access, packing and unpacking. Conversion to
and from L mode has also been added.

BGR;* modes
^^^^^^^^^^^

It is now possible to create new BGR;15, BGR;16 and BGR;24 images. Conversely, BGR;32
has been removed from ImageMode and its associated methods, dropping the little support
Pillow had for the mode.

With that, all modes listed under :ref:`concept-modes` can now be used to create a new
image.
