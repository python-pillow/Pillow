Concepts
========

The Python Imaging Library handles *raster images*; that is, rectangles of
pixel data.

.. _concept-bands:

Bands
-----

An image can consist of one or more bands of data. The Python Imaging Library
allows you to store several bands in a single image, provided they all have the
same dimensions and depth.  For example, a PNG image might have 'R', 'G', 'B',
and 'A' bands for the red, green, blue, and alpha transparency values.  Many
operations act on each band separately, e.g., histograms.  It is often useful to
think of each pixel as having one value per band.

To get the number and names of bands in an image, use the
:py:meth:`~PIL.Image.Image.getbands` method.

.. _concept-modes:

Modes
-----

The ``mode`` of an image is a string which defines the type and depth of a pixel in the
image. Each pixel uses the full range of the bit depth. So a 1-bit pixel has a range of
0-1, an 8-bit pixel has a range of 0-255, a 32-signed integer pixel has the range of
INT32 and a 32-bit floating point pixel has the range of FLOAT32. The current release
supports the following standard modes:

    * ``1`` (1-bit pixels, black and white, stored with one pixel per byte)
    * ``L`` (8-bit pixels, grayscale)
    * ``P`` (8-bit pixels, mapped to any other mode using a color palette)
    * ``RGB`` (3x8-bit pixels, true color)
    * ``RGBA`` (4x8-bit pixels, true color with transparency mask)
    * ``CMYK`` (4x8-bit pixels, color separation)
    * ``YCbCr`` (3x8-bit pixels, color video format)

      * Note that this refers to the JPEG, and not the ITU-R BT.2020, standard

    * ``LAB`` (3x8-bit pixels, the L*a*b color space)
    * ``HSV`` (3x8-bit pixels, Hue, Saturation, Value color space)

      * Hue's range of 0-255 is a scaled version of 0 degrees <= Hue < 360 degrees

    * ``I`` (32-bit signed integer pixels)
    * ``F`` (32-bit floating point pixels)

Pillow also provides limited support for a few additional modes, including:

    * ``LA`` (L with alpha)
    * ``PA`` (P with alpha)
    * ``RGBX`` (true color with padding)
    * ``RGBa`` (true color with premultiplied alpha)
    * ``La`` (L with premultiplied alpha)
    * ``I;16`` (16-bit unsigned integer pixels)
    * ``I;16L`` (16-bit little endian unsigned integer pixels)
    * ``I;16B`` (16-bit big endian unsigned integer pixels)
    * ``I;16N`` (16-bit native endian unsigned integer pixels)

Premultiplied alpha is where the values for each other channel have been
multiplied by the alpha. For example, an RGBA pixel of ``(10, 20, 30, 127)``
would convert to an RGBa pixel of ``(5, 10, 15, 127)``. The values of the R,
G and B channels are halved as a result of the half transparency in the alpha
channel.

Apart from these additional modes, Pillow doesn't yet support multichannel
images with a depth of more than 8 bits per channel.

Pillow also doesn’t support user-defined modes; if you need to handle band
combinations that are not listed above, use a sequence of Image objects.

You can read the mode of an image through the :py:attr:`~PIL.Image.Image.mode`
attribute. This is a string containing one of the above values.

Size
----

You can read the image size through the :py:attr:`~PIL.Image.Image.size`
attribute. This is a 2-tuple, containing the horizontal and vertical size in
pixels.

.. _coordinate-system:

Coordinate System
-----------------

The Python Imaging Library uses a Cartesian pixel coordinate system, with (0,0)
in the upper left corner. Note that the coordinates refer to the implied pixel
corners; the centre of a pixel addressed as (0, 0) actually lies at (0.5, 0.5).

Coordinates are usually passed to the library as 2-tuples (x, y). Rectangles
are represented as 4-tuples, (x1, y1, x2, y2), with the upper left corner given
first.

Palette
-------

The palette mode (``P``) uses a color palette to define the actual color for
each pixel.

Info
----

You can attach auxiliary information to an image using the
:py:attr:`~PIL.Image.Image.info` attribute. This is a dictionary object.

How such information is handled when loading and saving image files is up to
the file format handler (see the chapter on :ref:`image-file-formats`). Most
handlers add properties to the :py:attr:`~PIL.Image.Image.info` attribute when
loading an image, but ignore it when saving images.

Transparency
------------

If an image does not have an alpha band, transparency may be specified in the
:py:attr:`~PIL.Image.Image.info` attribute with a "transparency" key.

Most of the time, the "transparency" value is a single integer, describing
which pixel value is transparent in a "1", "L", "I" or "P" mode image.
However, PNG images may have three values, one for each channel in an "RGB"
mode image, or can have a byte string for a "P" mode image, to specify the
alpha value for each palette entry.

Orientation
-----------

A common element of the :py:attr:`~PIL.Image.Image.info` attribute for JPG and
TIFF images is the EXIF orientation tag. This is an instruction for how the
image data should be oriented. For example, it may instruct an image to be
rotated by 90 degrees, or to be mirrored. To apply this information to an
image, :py:meth:`~PIL.ImageOps.exif_transpose` can be used.

.. _concept-filters:

Filters
-------

For geometry operations that may map multiple input pixels to a single output
pixel, the Python Imaging Library provides different resampling *filters*.

.. py:currentmodule:: PIL.Image

.. data:: Resampling.NEAREST
    :noindex:

    Pick one nearest pixel from the input image. Ignore all other input pixels.

.. data:: Resampling.BOX
    :noindex:

    Each pixel of source image contributes to one pixel of the
    destination image with identical weights.
    For upscaling is equivalent of :data:`Resampling.NEAREST`.
    This filter can only be used with the :py:meth:`~PIL.Image.Image.resize`
    and :py:meth:`~PIL.Image.Image.thumbnail` methods.

    .. versionadded:: 3.4.0

.. data:: Resampling.BILINEAR
    :noindex:

    For resize calculate the output pixel value using linear interpolation
    on all pixels that may contribute to the output value.
    For other transformations linear interpolation over a 2x2 environment
    in the input image is used.

.. data:: Resampling.HAMMING
    :noindex:

    Produces a sharper image than :data:`Resampling.BILINEAR`, doesn't have
    dislocations on local level like with :data:`Resampling.BOX`.
    This filter can only be used with the :py:meth:`~PIL.Image.Image.resize`
    and :py:meth:`~PIL.Image.Image.thumbnail` methods.

    .. versionadded:: 3.4.0

.. data:: Resampling.BICUBIC
    :noindex:

    For resize calculate the output pixel value using cubic interpolation
    on all pixels that may contribute to the output value.
    For other transformations cubic interpolation over a 4x4 environment
    in the input image is used.

.. data:: Resampling.LANCZOS
    :noindex:

    Calculate the output pixel value using a high-quality Lanczos filter (a
    truncated sinc) on all pixels that may contribute to the output value.
    This filter can only be used with the :py:meth:`~PIL.Image.Image.resize`
    and :py:meth:`~PIL.Image.Image.thumbnail` methods.

    .. versionadded:: 1.1.3


Filters comparison table
~~~~~~~~~~~~~~~~~~~~~~~~

+---------------------------+-------------+-----------+-------------+
| Filter                    | Downscaling | Upscaling | Performance |
|                           | quality     | quality   |             |
+===========================+=============+===========+=============+
|:data:`Resampling.NEAREST` |             |           | ⭐⭐⭐⭐⭐  |
+---------------------------+-------------+-----------+-------------+
|:data:`Resampling.BOX`     | ⭐          |           | ⭐⭐⭐⭐    |
+---------------------------+-------------+-----------+-------------+
|:data:`Resampling.BILINEAR`| ⭐          | ⭐        | ⭐⭐⭐      |
+---------------------------+-------------+-----------+-------------+
|:data:`Resampling.HAMMING` | ⭐⭐        |           | ⭐⭐⭐      |
+---------------------------+-------------+-----------+-------------+
|:data:`Resampling.BICUBIC` | ⭐⭐⭐      | ⭐⭐⭐    | ⭐⭐        |
+---------------------------+-------------+-----------+-------------+
|:data:`Resampling.LANCZOS` | ⭐⭐⭐⭐    | ⭐⭐⭐⭐  | ⭐          |
+---------------------------+-------------+-----------+-------------+
