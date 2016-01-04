.. _file-decoders:

Writing Your Own File Decoder
=============================

The Python Imaging Library uses a plug-in model which allows you to
add your own decoders to the library, without any changes to the
library itself. Such plug-ins usually have names like
:file:`XxxImagePlugin.py`, where ``Xxx`` is a unique format name
(usually an abbreviation).

.. warning:: Pillow >= 2.1.0 no longer automatically imports any file in the Python path with a name ending in :file:`ImagePlugin.py`.  You will need to import your decoder manually.

A decoder plug-in should contain a decoder class, based on the
:py:class:`PIL.ImageFile.ImageFile` base class. This class should provide an
:py:meth:`_open` method, which reads the file header and sets up at least the
:py:attr:`~PIL.Image.Image.mode` and :py:attr:`~PIL.Image.Image.size`
attributes. To be able to load the file, the method must also create a list of
:py:attr:`tile` descriptors. The class must be explicitly registered, via a
call to the :py:mod:`~PIL.Image` module.

For performance reasons, it is important that the :py:meth:`_open` method
quickly rejects files that do not have the appropriate contents.

Example
-------

The following plug-in supports a simple format, which has a 128-byte header
consisting of the words “SPAM” followed by the width, height, and pixel size in
bits. The header fields are separated by spaces. The image data follows
directly after the header, and can be either bi-level, greyscale, or 24-bit
true color.

**SpamImagePlugin.py**::

    from PIL import Image, ImageFile
    import string

    class SpamImageFile(ImageFile.ImageFile):

        format = "SPAM"
        format_description = "Spam raster image"

        def _open(self):

            # check header
            header = self.fp.read(128)
            if header[:4] != "SPAM":
                raise SyntaxError, "not a SPAM file"

            header = string.split(header)

            # size in pixels (width, height)
            self.size = int(header[1]), int(header[2])

            # mode setting
            bits = int(header[3])
            if bits == 1:
                self.mode = "1"
            elif bits == 8:
                self.mode = "L"
            elif bits == 24:
                self.mode = "RGB"
            else:
                raise SyntaxError, "unknown number of bits"

            # data descriptor
            self.tile = [
                ("raw", (0, 0) + self.size, 128, (self.mode, 0, 1))
            ]

    Image.register_open("SPAM", SpamImageFile)

    Image.register_extension("SPAM", ".spam")
    Image.register_extension("SPAM", ".spa") # dos version

The format handler must always set the :py:attr:`~PIL.Image.Image.size` and
:py:attr:`~PIL.Image.Image.mode` attributes. If these are not set, the file
cannot be opened. To simplify the decoder, the calling code considers
exceptions like :py:exc:`SyntaxError`, :py:exc:`KeyError`, and
:py:exc:`IndexError`, as a failure to identify the file.

Note that the decoder must be explicitly registered using
:py:func:`PIL.Image.register_open`. Although not required, it is also a good
idea to register any extensions used by this format.

The :py:attr:`tile` attribute
-----------------------------

To be able to read the file as well as just identifying it, the :py:attr:`tile`
attribute must also be set. This attribute consists of a list of tile
descriptors, where each descriptor specifies how data should be loaded to a
given region in the image. In most cases, only a single descriptor is used,
covering the full image.

The tile descriptor is a 4-tuple with the following contents::

    (decoder, region, offset, parameters)

The fields are used as follows:

**decoder**
    Specifies which decoder to use. The ``raw`` decoder used here supports
    uncompressed data, in a variety of pixel formats. For more information on
    this decoder, see the description below.

**region**
    A 4-tuple specifying where to store data in the image.

**offset**
    Byte offset from the beginning of the file to image data.

**parameters**
    Parameters to the decoder. The contents of this field depends on the
    decoder specified by the first field in the tile descriptor tuple. If the
    decoder doesn’t need any parameters, use None for this field.

Note that the :py:attr:`tile` attribute contains a list of tile descriptors,
not just a single descriptor.

The raw decoder
---------------

The ``raw`` decoder is used to read uncompressed data from an image file. It
can be used with most uncompressed file formats, such as PPM, BMP, uncompressed
TIFF, and many others. To use the raw decoder with the
:py:func:`PIL.Image.frombytes` function, use the following syntax::

    image = Image.frombytes(
        mode, size, data, "raw",
        raw mode, stride, orientation
        )

When used in a tile descriptor, the parameter field should look like::

    (raw mode, stride, orientation)

The fields are used as follows:

**raw mode**
    The pixel layout used in the file, and is used to properly convert data to
    PIL’s internal layout. For a summary of the available formats, see the
    table below.

**stride**
    The distance in bytes between two consecutive lines in the image. If 0, the
    image is assumed to be packed (no padding between lines). If omitted, the
    stride defaults to 0.

**orientation**

    Whether the first line in the image is the top line on the screen (1), or
    the bottom line (-1). If omitted, the orientation defaults to 1.

The **raw mode** field is used to determine how the data should be unpacked to
match PIL’s internal pixel layout. PIL supports a large set of raw modes; for a
complete list, see the table in the :py:mod:`Unpack.c` module. The following
table describes some commonly used **raw modes**:

+-----------+-----------------------------------------------------------------+
| mode	    | description                                                     |
+===========+=================================================================+
| ``1``     | 1-bit bilevel, stored with the leftmost pixel in the most       |
|           | significant bit. 0 means black, 1 means white.                  |
+-----------+-----------------------------------------------------------------+
| ``1;I``   | 1-bit inverted bilevel, stored with the leftmost pixel in the   |
|           | most significant bit. 0 means white, 1 means black.             |
+-----------+-----------------------------------------------------------------+
| ``1;R``   | 1-bit reversed bilevel, stored with the leftmost pixel in the   |
|           | least significant bit. 0 means black, 1 means white.            |
+-----------+-----------------------------------------------------------------+
| ``L``     | 8-bit greyscale. 0 means black, 255 means white.                |
+-----------+-----------------------------------------------------------------+
| ``L;I``   | 8-bit inverted greyscale. 0 means white, 255 means black.       |
+-----------+-----------------------------------------------------------------+
| ``P``     | 8-bit palette-mapped image.                                     |
+-----------+-----------------------------------------------------------------+
| ``RGB``   | 24-bit true colour, stored as (red, green, blue).               |
+-----------+-----------------------------------------------------------------+
| ``BGR``   | 24-bit true colour, stored as (blue, green, red).               |
+-----------+-----------------------------------------------------------------+
| ``RGBX``  | 24-bit true colour, stored as (blue, green, red, pad).          |
+-----------+-----------------------------------------------------------------+
| ``RGB;L`` | 24-bit true colour, line interleaved (first all red pixels, the |
|           | all green pixels, finally all blue pixels).                     |
+-----------+-----------------------------------------------------------------+

Note that for the most common cases, the raw mode is simply the same as the mode.

The Python Imaging Library supports many other decoders, including JPEG, PNG,
and PackBits. For details, see the :file:`decode.c` source file, and the
standard plug-in implementations provided with the library.

Decoding floating point data
----------------------------

PIL provides some special mechanisms to allow you to load a wide variety of
formats into a mode ``F`` (floating point) image memory.

You can use the ``raw`` decoder to read images where data is packed in any
standard machine data type, using one of the following raw modes:

============ =======================================
mode	     description
============ =======================================
``F``        32-bit native floating point.
``F;8``      8-bit unsigned integer.
``F;8S``     8-bit signed integer.
``F;16``     16-bit little endian unsigned integer.
``F;16S``    16-bit little endian signed integer.
``F;16B``    16-bit big endian unsigned integer.
``F;16BS``   16-bit big endian signed integer.
``F;16N``    16-bit native unsigned integer.
``F;16NS``   16-bit native signed integer.
``F;32``     32-bit little endian unsigned integer.
``F;32S``    32-bit little endian signed integer.
``F;32B``    32-bit big endian unsigned integer.
``F;32BS``   32-bit big endian signed integer.
``F;32N``    32-bit native unsigned integer.
``F;32NS``   32-bit native signed integer.
``F;32F``    32-bit little endian floating point.
``F;32BF``   32-bit big endian floating point.
``F;32NF``   32-bit native floating point.
``F;64F``    64-bit little endian floating point.
``F;64BF``   64-bit big endian floating point.
``F;64NF``   64-bit native floating point.
============ =======================================

The bit decoder
---------------

If the raw decoder cannot handle your format, PIL also provides a special “bit”
decoder that can be used to read various packed formats into a floating point
image memory.

To use the bit decoder with the frombytes function, use the following syntax::

    image = frombytes(
        mode, size, data, "bit",
        bits, pad, fill, sign, orientation
        )

When used in a tile descriptor, the parameter field should look like::

    (bits, pad, fill, sign, orientation)

The fields are used as follows:

**bits**
    Number of bits per pixel (2-32). No default.

**pad**
    Padding between lines, in bits. This is either 0 if there is no padding, or
    8 if lines are padded to full bytes. If omitted, the pad value defaults to
    8.

**fill**
    Controls how data are added to, and stored from, the decoder bit buffer.

**fill=0**
    Add bytes to the LSB end of the decoder buffer; store pixels from the MSB
    end.

**fill=1**
    Add bytes to the MSB end of the decoder buffer; store pixels from the MSB
    end.

**fill=2**
    Add bytes to the LSB end of the decoder buffer; store pixels from the LSB
    end.

**fill=3**
    Add bytes to the MSB end of the decoder buffer; store pixels from the LSB
    end.

    If omitted, the fill order defaults to 0.

**sign**
    If non-zero, bit fields are sign extended. If zero or omitted, bit fields
    are unsigned.

**orientation**
    Whether the first line in the image is the top line on the screen (1), or
    the bottom line (-1). If omitted, the orientation defaults to 1.
