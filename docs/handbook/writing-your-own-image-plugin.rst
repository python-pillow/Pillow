.. _image-plugins:

Writing your own image plugin
=============================

Pillow uses a plugin model which allows you to add your own
decoders and encoders to the library, without any changes to the library
itself. Such plugins usually have names like :file:`XxxImagePlugin.py`,
where ``Xxx`` is a unique format name (usually an abbreviation).

.. warning:: Pillow >= 2.1.0 no longer automatically imports any file
             in the Python path with a name ending in
             :file:`ImagePlugin.py`.  You will need to import your
             image plugin manually.

Pillow decodes files in two stages:

1. It loops over the available image plugins in the loaded order, and
   calls the plugin's ``_accept`` function with the first 16 bytes of
   the file. If the ``_accept`` function returns true, the plugin's
   ``_open`` method is called to set up the image metadata and image
   tiles. The ``_open`` method is not for decoding the actual image
   data.
2. When the image data is requested, the ``ImageFile.load`` method is
   called, which sets up a decoder for each tile and feeds the data to
   it.

An image plugin should contain a format handler derived from the
:py:class:`PIL.ImageFile.ImageFile` base class. This class should provide an
``_open`` method, which reads the file header and sets at least the internal
``_size`` and ``_mode`` attributes so that :py:attr:`~PIL.Image.Image.mode` and
:py:attr:`~PIL.Image.Image.size` are populated. To be able to load the file,
the method must also create a list of ``tile`` descriptors, which contain a
decoder name, extents of the tile, and any decoder-specific data. The format
handler class must be explicitly registered, via a call to the
:py:mod:`~PIL.Image` module.

.. note:: For performance reasons, it is important that the
  ``_open`` method quickly rejects files that do not have the
  appropriate contents.

Example
-------

The following plugin supports a simple format, which has a 128-byte header
consisting of the words “SPAM” followed by the width, height, and pixel size in
bits. The header fields are separated by spaces. The image data follows
directly after the header, and can be either bi-level, grayscale, or 24-bit
true color.

**SpamImagePlugin.py**::

    from PIL import Image, ImageFile


    def _accept(prefix: bytes) -> bool:
        return prefix.startswith(b"SPAM")


    class SpamImageFile(ImageFile.ImageFile):

        format = "SPAM"
        format_description = "Spam raster image"

        def _open(self) -> None:

            header = self.fp.read(128).split()

            # size in pixels (width, height)
            self._size = int(header[1]), int(header[2])

            # mode setting
            bits = int(header[3])
            if bits == 1:
                self._mode = "1"
            elif bits == 8:
                self._mode = "L"
            elif bits == 24:
                self._mode = "RGB"
            else:
                msg = "unknown number of bits"
                raise SyntaxError(msg)

            # data descriptor
            self.tile = [ImageFile._Tile("raw", (0, 0) + self.size, 128, (self.mode, 0, 1))]


    Image.register_open(SpamImageFile.format, SpamImageFile, _accept)

    Image.register_extensions(
        SpamImageFile.format,
        [
            ".spam",
            ".spa",  # DOS version
        ],
    )


The format handler must always set the internal ``_size`` and ``_mode``
attributes so that :py:attr:`~PIL.Image.Image.size` and
:py:attr:`~PIL.Image.Image.mode` are populated. If these are not set, the file
cannot be opened. To simplify the plugin, the calling code considers exceptions
like :py:exc:`SyntaxError`, :py:exc:`KeyError`, :py:exc:`IndexError`,
:py:exc:`EOFError` and :py:exc:`struct.error` as a failure to identify the
file.

Note that the image plugin must be explicitly registered using
:py:func:`PIL.Image.register_open`. Although not required, it is also a good
idea to register any extensions used by this format.

Once the plugin has been imported, it can be used::

    from PIL import Image
    import SpamImagePlugin

    with Image.open("hopper.spam") as im:
        pass

The ``tile`` attribute
----------------------

To be able to read the file as well as just identifying it, the ``tile``
attribute must also be set. This attribute consists of a list of tile
descriptors, where each descriptor specifies how data should be loaded to a
given region in the image.

In most cases, only a single descriptor is used, covering the full image.
:py:class:`.PsdImagePlugin.PsdImageFile` uses multiple tiles to combine
channels within a single layer, given that the channels are stored separately,
one after the other.

The tile descriptor is a 4-tuple with the following contents::

    (decoder, region, offset, parameters)

The fields are used as follows:

**decoder**
    Specifies which decoder to use. The ``raw`` decoder used here supports
    uncompressed data, in a variety of pixel formats. For more information on
    this decoder, see the description below.

    A list of C decoders can be seen under codecs section of the function array
    in :file:`_imaging.c`. Python decoders are registered within the relevant
    plugins.

**region**
    A 4-tuple specifying where to store data in the image.

**offset**
    Byte offset from the beginning of the file to image data.

**parameters**
    Parameters to the decoder. The contents of this field depends on the
    decoder specified by the first field in the tile descriptor tuple. If the
    decoder doesn’t need any parameters, use :data:`None` for this field.

Note that the ``tile`` attribute contains a list of tile descriptors,
not just a single descriptor.

Decoders
========

The raw decoder
---------------

The ``raw`` decoder is used to read uncompressed data from an image file. It
can be used with most uncompressed file formats, such as PPM, BMP, uncompressed
TIFF, and many others. To use the raw decoder with the
:py:func:`PIL.Image.frombytes` function, use the following syntax::

    image = Image.frombytes(
        mode, size, data, "raw",
        raw_mode, stride, orientation
        )

When used in a tile descriptor, the parameter field should look like::

    (raw_mode, stride, orientation)

The fields are used as follows:

**raw_mode**
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
complete list, see the table in the :file:`Unpack.c` module. The following
table describes some commonly used **raw modes**:

+-----------+-------------------------------------------------------------------+
| mode      | description                                                       |
+===========+===================================================================+
| ``1``     | | 1-bit bilevel, stored with the leftmost pixel in the most       |
|           | | significant bit. 0 means black, 1 means white.                  |
+-----------+-------------------------------------------------------------------+
| ``1;I``   | | 1-bit inverted bilevel, stored with the leftmost pixel in the   |
|           | | most significant bit. 0 means white, 1 means black.             |
+-----------+-------------------------------------------------------------------+
| ``1;R``   | | 1-bit reversed bilevel, stored with the leftmost pixel in the   |
|           | | least significant bit. 0 means black, 1 means white.            |
+-----------+-------------------------------------------------------------------+
| ``L``     | 8-bit grayscale. 0 means black, 255 means white.                  |
+-----------+-------------------------------------------------------------------+
| ``L;I``   | 8-bit inverted grayscale. 0 means white, 255 means black.         |
+-----------+-------------------------------------------------------------------+
| ``P``     | 8-bit palette-mapped image.                                       |
+-----------+-------------------------------------------------------------------+
| ``RGB``   | 24-bit true color, stored as (red, green, blue).                  |
+-----------+-------------------------------------------------------------------+
| ``BGR``   | 24-bit true color, stored as (blue, green, red).                  |
+-----------+-------------------------------------------------------------------+
| ``RGBX``  | | 24-bit true color, stored as (red, green, blue, pad). The pad   |
|           | | pixels may vary.                                                |
+-----------+-------------------------------------------------------------------+
| ``RGB;L`` | | 24-bit true color, line interleaved (first all red pixels, then |
|           | | all green pixels, finally all blue pixels).                     |
+-----------+-------------------------------------------------------------------+

Note that for the most common cases, the raw mode is simply the same as the mode.

The Python Imaging Library supports many other decoders, including JPEG, PNG,
and PackBits. For details, see the :file:`decode.c` source file, and the
standard plugin implementations provided with the library.

Decoding floating point data
----------------------------

PIL provides some special mechanisms to allow you to load a wide variety of
formats into a mode ``F`` (floating point) image memory.

You can use the ``raw`` decoder to read images where data is packed in any
standard machine data type, using one of the following raw modes:

============ =======================================
mode         description
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

To use the bit decoder with the :py:func:`PIL.Image.frombytes` function, use
the following syntax::

    image = Image.frombytes(
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

.. _file-codecs:

Writing your own file codec in C
================================

There are 3 stages in a file codec's lifetime:

1. Setup: Pillow looks for a function in the decoder or encoder registry,
   falling back to a function named ``[codecname]_decoder`` or
   ``[codecname]_encoder`` on the internal core image object. That function is
   called with the ``args`` tuple from the ``tile``.

2. Transforming: The codec's ``decode`` or ``encode`` function is repeatedly
   called with chunks of image data.

3. Cleanup: If the codec has registered a cleanup function, it will
   be called at the end of the transformation process, even if there was an
   exception raised.


Setup
-----

The current conventions are that the codec setup function is named
``PyImaging_[codecname]DecoderNew`` or ``PyImaging_[codecname]EncoderNew``
and defined in ``decode.c`` or ``encode.c``. The Python binding for it is
named ``[codecname]_decoder`` or ``[codecname]_encoder`` and is set up from
within the ``_imaging.c`` file in the codecs section of the function array.

The setup function needs to call ``PyImaging_DecoderNew`` or
``PyImaging_EncoderNew`` and at the very least, set the ``decode`` or
``encode`` function pointer. The fields of interest in this object are:

**decode**/**encode**
  Function pointer to the decode or encode function, which has access to
  ``im``, ``state``, and the buffer of data to be transformed.

**cleanup**
  Function pointer to the cleanup function, has access to ``state``.

**im**
  The target image, will be set by Pillow.

**state**
  An ImagingCodecStateInstance, will be set by Pillow. The ``context``
  member is an opaque struct that can be used by the codec to store
  any format specific state or options.

**pulls_fd**/**pushes_fd**
  If the decoder has ``pulls_fd`` or the encoder has ``pushes_fd`` set to 1,
  ``state->fd`` will be a pointer to the Python file-like object. The codec may
  use the functions in ``codec_fd.c`` to read or write directly with the file
  like object rather than have the data pushed through a buffer.

  .. versionadded:: 3.3.0


Transforming
------------

The decode or encode function is called with the target (core) image, the codec
state structure, and a buffer of data to be transformed.

It is the codec's responsibility to pull as much data as possible out of the
buffer and return the number of bytes consumed. The next call to the codec will
include the previous unconsumed tail. The codec function will be called
multiple times as the data is processed.

Alternatively, if ``pulls_fd`` or ``pushes_fd`` is set, then the decode or
encode function is called once, with an empty buffer. It is the codec's
responsibility to transform the entire tile in that one call.  Using this will
provide a codec with more freedom, but that freedom may mean increased memory
usage if the entire tile is held in memory at once by the codec.

If an error occurs, set ``state->errcode`` and return -1.

Return -1 on success, without setting the errcode.

Cleanup
-------

The cleanup function is called after the codec returns a negative
value, or if there is an error. This function should free any allocated
memory and release any resources from external libraries.

.. _file-codecs-py:

Writing your own file codec in Python
=====================================

Python file decoders and encoders should derive from
:py:class:`PIL.ImageFile.PyDecoder` and :py:class:`PIL.ImageFile.PyEncoder`
respectively, and should at least override the decode or encode method.
They should be registered using :py:meth:`PIL.Image.register_decoder` and
:py:meth:`PIL.Image.register_encoder`. As in the C implementation of
the file codecs, there are three stages in the lifetime of a
Python-based file codec:

1. Setup: Pillow looks for the codec in the decoder or encoder registry, then
   instantiates the class.

2. Transforming: The instance's ``decode`` method is repeatedly called with
   a buffer of data to be interpreted, or the ``encode`` method is repeatedly
   called with the size of data to be output.

   Alternatively, if the decoder's ``_pulls_fd`` property (or the encoder's
   ``_pushes_fd`` property) is set to ``True``, then ``decode`` and ``encode``
   will only be called once. In the decoder, ``self.fd`` can be used to access
   the file-like object. Using this will provide a codec with more freedom, but
   that freedom may mean increased memory usage if the entire file is held in
   memory at once by the codec.

   In ``decode``, once the data has been interpreted, ``set_as_raw`` can be
   used to populate the image.

3. Cleanup: The instance's ``cleanup`` method is called once the transformation
   is complete. This can be used to clean up any resources used by the codec.

   If you set ``_pulls_fd`` or ``_pushes_fd`` to ``True`` however, then you
   probably chose to perform any cleanup tasks at the end of ``decode`` or
   ``encode``.

For an example :py:class:`PIL.ImageFile.PyDecoder`, see `DdsImagePlugin
<https://github.com/python-pillow/Pillow/blob/main/docs/example/DdsImagePlugin.py>`_.
For a plugin that uses both :py:class:`PIL.ImageFile.PyDecoder` and
:py:class:`PIL.ImageFile.PyEncoder`, see `BlpImagePlugin
<https://github.com/python-pillow/Pillow/blob/main/src/PIL/BlpImagePlugin.py>`_
