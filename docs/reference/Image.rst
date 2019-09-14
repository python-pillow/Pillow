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

Open, rotate, and display an image (using the default viewer)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following script loads an image, rotates it 45 degrees, and displays it
using an external viewer (usually xv on Unix, and the Paint program on
Windows).

.. code-block:: python

    from PIL import Image
    im = Image.open("bride.jpg")
    im.rotate(45).show()

Create thumbnails
^^^^^^^^^^^^^^^^^

The following script creates nice thumbnails of all JPEG images in the
current directory preserving aspect ratios with 128x128 max resolution.

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
        a lot of memory), Pillow will issue a ``DecompressionBombWarning`` if the image is over a certain
        limit. If desired, the warning can be turned into an error with
        ``warnings.simplefilter('error', Image.DecompressionBombWarning)`` or suppressed entirely with
        ``warnings.simplefilter('ignore', Image.DecompressionBombWarning)``. See also `the logging
        documentation`_ to have warnings output to the logging facility instead of stderr.

	.. _decompression bombs: https://en.wikipedia.org/wiki/Zip_bomb
	.. _the logging documentation: https://docs.python.org/3/library/logging.html#integration-with-the-warnings-module

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
.. autofunction:: register_decoder
.. autofunction:: register_mime
.. autofunction:: register_save
.. autofunction:: register_encoder
.. autofunction:: register_extension


The Image Class
---------------

.. autoclass:: PIL.Image.Image

An instance of the :py:class:`~PIL.Image.Image` class has the following
methods. Unless otherwise stated, all methods return a new instance of the
:py:class:`~PIL.Image.Image` class, holding the resulting image.


.. automethod:: PIL.Image.Image.alpha_composite
.. automethod:: PIL.Image.Image.convert

The following example converts an RGB image (linearly calibrated according to
ITU-R 709, using the D65 luminant) to the CIE XYZ color space:

.. code-block:: python

    rgb2xyz = (
        0.412453, 0.357580, 0.180423, 0,
        0.212671, 0.715160, 0.072169, 0,
        0.019334, 0.119193, 0.950227, 0)
    out = im.convert("RGB", rgb2xyz)

.. automethod:: PIL.Image.Image.copy
.. automethod:: PIL.Image.Image.crop

This crops the input image with the provided coordinates:

.. code-block:: python

    from PIL import Image

    im = Image.open("hopper.jpg")

    # The crop method from the Image module takes four coordinates as input.
    # The right can also be represented as (left+width)
    # and lower can be represented as (upper+height).
    (left, upper, right, lower) = (20, 20, 100, 100)

    # Here the image "im" is cropped and assigned to new variable im_crop
    im_crop = im.crop((left, upper, right, lower))


.. automethod:: PIL.Image.Image.draft
.. automethod:: PIL.Image.Image.filter

This blurs the input image using a filter from the ``ImageFilter`` module:

.. code-block:: python

    from PIL import Image, ImageFilter

    im = Image.open("hopper.jpg")

    # Blur the input image using the filter ImageFilter.BLUR
    im_blurred = im.filter(filter=ImageFilter.BLUR)

.. automethod:: PIL.Image.Image.getbands

This helps to get the bands of the input image:

.. code-block:: python

    from PIL import Image

    im = Image.open("hopper.jpg")
    print(im.getbands())  # Returns ('R', 'G', 'B')

.. automethod:: PIL.Image.Image.getbbox

This helps to get the bounding box coordinates of the input image:

.. code-block:: python

    from PIL import Image

    im = Image.open("hopper.jpg")
    print(im.getbbox())
    # Returns four coordinates in the format (left, upper, right, lower)

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

This resizes the given image from ``(width, height)`` to ``(width/2, height/2)``:

.. code-block:: python

    from PIL import Image

    im = Image.open("hopper.jpg")

    # Provide the target width and height of the image
    (width, height) = (im.width // 2, im.height // 2)
    im_resized = im.resize((width, height))

.. automethod:: PIL.Image.Image.remap_palette
.. automethod:: PIL.Image.Image.rotate

This rotates the input image by ``theta`` degrees counter clockwise:

.. code-block:: python

    from PIL import Image

    im = Image.open("hopper.jpg")

    # Rotate the image by 60 degrees counter clockwise
    theta = 60
    # Angle is in degrees counter clockwise
    im_rotated = im.rotate(angle=theta)

.. automethod:: PIL.Image.Image.save
.. automethod:: PIL.Image.Image.seek
.. automethod:: PIL.Image.Image.show
.. automethod:: PIL.Image.Image.split
.. automethod:: PIL.Image.Image.getchannel
.. automethod:: PIL.Image.Image.tell
.. automethod:: PIL.Image.Image.thumbnail
.. automethod:: PIL.Image.Image.tobitmap
.. automethod:: PIL.Image.Image.tobytes
.. automethod:: PIL.Image.Image.tostring
.. automethod:: PIL.Image.Image.transform
.. automethod:: PIL.Image.Image.transpose

This flips the input image by using the ``Image.FLIP_LEFT_RIGHT`` method.

.. code-block:: python

    from PIL import Image

    im = Image.open("hopper.jpg")

    # Flip the image from left to right
    im_flipped = im.transpose(method=Image.FLIP_LEFT_RIGHT)
    # To flip the image from top to bottom,
    # use the method "Image.FLIP_TOP_BOTTOM"


.. automethod:: PIL.Image.Image.verify

.. automethod:: PIL.Image.Image.fromstring

.. automethod:: PIL.Image.Image.load
.. automethod:: PIL.Image.Image.close

Attributes
----------

Instances of the :py:class:`Image` class have the following attributes:

.. py:attribute:: filename

    The filename or path of the source file. Only images created with the
    factory function ``open`` have a filename attribute. If the input is a
    file like object, the filename attribute is set to an empty string.

    :type: :py:class:`string`

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

    Colour palette table, if any. If mode is "P" or "PA", this should be an
    instance of the :py:class:`~PIL.ImagePalette.ImagePalette` class.
    Otherwise, it should be set to ``None``.

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
