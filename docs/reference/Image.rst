.. py:module:: PIL.Image
.. py:currentmodule:: PIL.Image

:py:mod:`Image` Module
======================

The :py:mod:`~PIL.Image` module provides a class with the same name which is
used to represent a PIL image. The module also provides a number of factory
functions, including functions to load images from files, and to create new
images.

Examples
--------

The following script loads an image, rotates it 45 degrees, and displays it
using an external viewer (usually xv on Unix, and the paint program on
Windows).

Open, rotate, and display an image (using the default viewer)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from PIL import Image
    im = Image.open("bride.jpg")
    im.rotate(45).show()

The following script creates nice 128x128 thumbnails of all JPEG images in the
current directory.

Create thumbnails
^^^^^^^^^^^^^^^^^

.. code-block:: python

    from PIL import Image
    import glob, os

    size = 128, 128

    for infile in glob.glob("*.jpg"):
        file, ext = os.path.splitext(infile)
        im = Image.open(infile)
        im.thumbnail(size)
        im.save(file + ".thumbnail", "JPEG")

Functions
---------

.. autofunction:: open

    .. warning::
        To protect against potential DOS attacks caused by "`decompression bombs`_" (i.e. malicious files
        which decompress into a huge amount of data and are designed to crash or cause disruption by using up
        a lot of memory), Pillow will issue a `DecompressionBombWarning` if the image is over a certain
        limit. If desired, the warning can be turned into an error with
        ``warnings.simplefilter('error', Image.DecompressionBombWarning)`` or suppressed entirely with
        ``warnings.simplefilter('ignore', Image.DecompressionBombWarning)``. See also `the logging
        documentation`_ to have warnings output to the logging facility instead of stderr.

	.. _decompression bombs: https://en.wikipedia.org/wiki/Zip_bomb
	.. _the logging documentation: https://docs.python.org/2/library/logging.html?highlight=logging#integration-with-the-warnings-module

Image processing
^^^^^^^^^^^^^^^^

.. autofunction:: alpha_composite
.. autofunction:: blend
.. autofunction:: composite
.. autofunction:: eval
.. autofunction:: merge

Constructing images
^^^^^^^^^^^^^^^^^^^

.. autofunction:: new
.. autofunction:: fromarray
.. autofunction:: frombytes
.. autofunction:: fromstring
.. autofunction:: frombuffer

Registering plugins
^^^^^^^^^^^^^^^^^^^

.. note::

    These functions are for use by plugin authors. Application authors can
    ignore them.

.. autofunction:: register_open
.. autofunction:: register_mime
.. autofunction:: register_save
.. autofunction:: register_extension

The Image Class
---------------

.. autoclass:: PIL.Image.Image

An instance of the :py:class:`~PIL.Image.Image` class has the following
methods. Unless otherwise stated, all methods return a new instance of the
:py:class:`~PIL.Image.Image` class, holding the resulting image.

.. automethod:: PIL.Image.Image.convert

The following example converts an RGB image (linearly calibrated according to
ITU-R 709, using the D65 luminant) to the CIE XYZ color space:

.. code-block:: python

    rgb2xyz = (
        0.412453, 0.357580, 0.180423, 0,
        0.212671, 0.715160, 0.072169, 0,
        0.019334, 0.119193, 0.950227, 0 )
    out = im.convert("RGB", rgb2xyz)

.. automethod:: PIL.Image.Image.copy
.. automethod:: PIL.Image.Image.crop
.. automethod:: PIL.Image.Image.draft
.. automethod:: PIL.Image.Image.filter
.. automethod:: PIL.Image.Image.getbands
.. automethod:: PIL.Image.Image.getbbox
.. automethod:: PIL.Image.Image.getcolors
.. automethod:: PIL.Image.Image.getdata
.. automethod:: PIL.Image.Image.getextrema
.. automethod:: PIL.Image.Image.getpalette
.. automethod:: PIL.Image.Image.getpixel
.. automethod:: PIL.Image.Image.histogram
.. automethod:: PIL.Image.Image.offset
.. automethod:: PIL.Image.Image.paste
.. automethod:: PIL.Image.Image.point
.. automethod:: PIL.Image.Image.putalpha
.. automethod:: PIL.Image.Image.putdata
.. automethod:: PIL.Image.Image.putpalette
.. automethod:: PIL.Image.Image.putpixel
.. automethod:: PIL.Image.Image.quantize
.. automethod:: PIL.Image.Image.resize
.. automethod:: PIL.Image.Image.rotate
.. automethod:: PIL.Image.Image.save
.. automethod:: PIL.Image.Image.seek
.. automethod:: PIL.Image.Image.show
.. automethod:: PIL.Image.Image.split
.. automethod:: PIL.Image.Image.tell
.. automethod:: PIL.Image.Image.thumbnail
.. automethod:: PIL.Image.Image.tobitmap
.. automethod:: PIL.Image.Image.tobytes
.. automethod:: PIL.Image.Image.tostring
.. automethod:: PIL.Image.Image.transform
.. automethod:: PIL.Image.Image.transpose
.. automethod:: PIL.Image.Image.verify

.. automethod:: PIL.Image.Image.fromstring

.. automethod:: PIL.Image.Image.load
.. automethod:: PIL.Image.Image.close

Attributes
----------

Instances of the :py:class:`Image` class have the following attributes:

.. py:attribute:: format

    The file format of the source file. For images created by the library
    itself (via a factory function, or by running a method on an existing
    image), this attribute is set to ``None``.

    :type: :py:class:`string` or ``None``

.. py:attribute:: mode

    Image mode. This is a string specifying the pixel format used by the image.
    Typical values are “1”, “L”, “RGB”, or “CMYK.” See
    :ref:`concept-modes` for a full list.

    :type: :py:class:`string`

.. py:attribute:: size

    Image size, in pixels. The size is given as a 2-tuple (width, height).

    :type: ``(width, height)``

.. py:attribute:: width

    Image width, in pixels.

    :type: :py:class:`int`

.. py:attribute:: height

    Image height, in pixels.

    :type: :py:class:`int`

.. py:attribute:: palette

    Colour palette table, if any. If mode is “P”, this should be an instance of
    the :py:class:`~PIL.ImagePalette.ImagePalette` class. Otherwise, it should
    be set to ``None``.

    :type: :py:class:`~PIL.ImagePalette.ImagePalette` or ``None``

.. py:attribute:: info

    A dictionary holding data associated with the image. This dictionary is
    used by file handlers to pass on various non-image information read from
    the file. See documentation for the various file handlers for details.

    Most methods ignore the dictionary when returning new images; since the
    keys are not standardized, it’s not possible for a method to know if the
    operation affects the dictionary. If you need the information later on,
    keep a reference to the info dictionary returned from the open method.

    Unless noted elsewhere, this dictionary does not affect saving files.

    :type: :py:class:`dict`
