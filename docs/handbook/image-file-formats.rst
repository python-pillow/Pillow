.. _image-file-formats:

Image file formats
==================

The Python Imaging Library supports a wide variety of raster file formats.
Nearly 30 different file formats can be identified and read by the library.
Write support is less extensive, but most common interchange and presentation
formats are supported.

The :py:meth:`~PIL.Image.Image.open` function identifies files from their
contents, not their names, but the :py:meth:`~PIL.Image.Image.save` method
looks at the name to determine which format to use, unless the format is given
explicitly.

Fully supported formats
-----------------------

BMP
^^^

PIL reads and writes Windows and OS/2 BMP files containing ``1``, ``L``, ``P``,
or ``RGB`` data. 16-colour images are read as ``P`` images. Run-length encoding
is not supported.

The :py:meth:`~PIL.Image.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties:

**compression**
    Set to ``bmp_rle`` if the file is run-length encoded.

EPS
^^^

PIL identifies EPS files containing image data, and can read files that contain
embedded raster images (ImageData descriptors). If Ghostscript is available,
other EPS files can be read as well. The EPS driver can also write EPS images.

If Ghostscript is available, you can call the :py:meth:`~PIL.Image.Image.load`
method with the following parameter to affect how Ghostscript renders the EPS

**scale**
    Affects the scale of the resultant rasterized image. If the EPS suggests
    that the image be rendered at 100px x 100px, setting this parameter to
    2 will make the Ghostscript render a 200px x 200px image instead. The
    relative position of the bounding box is maintained::

        im = Image.open(...)
        im.size #(100,100)
        im.load(scale=2)
        im.size #(200,200)

GIF
^^^

PIL reads GIF87a and GIF89a versions of the GIF file format. The library writes
run-length encoded GIF87a files. Note that GIF files are always read as
grayscale (``L``) or palette mode (``P``) images.

The :py:meth:`~PIL.Image.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties:

**background**
    Default background color (a palette color index).

**duration**
    Time between frames in an animation (in milliseconds).

**transparency**
    Transparency color index. This key is omitted if the image is not
    transparent.

**version**
    Version (either ``GIF87a`` or ``GIF89a``).

Reading sequences
~~~~~~~~~~~~~~~~~

The GIF loader supports the :py:meth:`~file.seek` and :py:meth:`~file.tell`
methods. You can seek to the next frame (``im.seek(im.tell() + 1``), or rewind
the file by seeking to the first frame. Random access is not supported.

Reading local images
~~~~~~~~~~~~~~~~~~~~

The GIF loader creates an image memory the same size as the GIF file’s *logical
screen size*, and pastes the actual pixel data (the *local image*) into this
image. If you only want the actual pixel rectangle, you can manipulate the
:py:attr:`~PIL.Image.Image.size` and :py:attr:`~PIL.Image.Image.tile`
attributes before loading the file::

    im = Image.open(...)

    if im.tile[0][0] == "gif":
        # only read the first "local image" from this GIF file
        tag, (x0, y0, x1, y1), offset, extra = im.tile[0]
        im.size = (x1 - x0, y1 - y0)
        im.tile = [(tag, (0, 0) + im.size, offset, extra)]

IM
^^

IM is a format used by LabEye and other applications based on the IFUNC image
processing library. The library reads and writes most uncompressed interchange
versions of this format.

IM is the only format that can store all internal PIL formats.

JPEG
^^^^

PIL reads JPEG, JFIF, and Adobe JPEG files containing ``L``, ``RGB``, or
``CMYK`` data. It writes standard and progressive JFIF files.

Using the :py:meth:`~PIL.Image.Image.draft` method, you can speed things up by
converting ``RGB`` images to ``L``, and resize images to 1/2, 1/4 or 1/8 of
their original size while loading them. The :py:meth:`~PIL.Image.Image.draft`
method also configures the JPEG decoder to trade some quality for speed.

The :py:meth:`~PIL.Image.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties:

**jfif**
    JFIF application marker found. If the file is not a JFIF file, this key is
    not present.

**adobe**
    Adobe application marker found. If the file is not an Adobe JPEG file, this
    key is not present.

**progression**
    Indicates that this is a progressive JPEG file.

The :py:meth:`~PIL.Image.Image.save` method supports the following options:

**quality**
    The image quality, on a scale from 1 (worst) to 95 (best). The default is
    75. Values above 95 should be avoided; 100 disables portions of the JPEG
    compression algorithm, and results in large files with hardly any gain in =
    image quality.

**optimize**
    If present, indicates that the encoder should make an extra pass over the
    image in order to select optimal encoder settings.

**progressive**
    If present, indicates that this image should be stored as a progressive
    JPEG file.

.. note::

    To enable JPEG support, you need to build and install the IJG JPEG library
    before building the Python Imaging Library. See the distribution README for
    details.

JPEG 2000
^^^^^^^^^

PIL reads and writes JPEG 2000 files containing ``L``, ``LA``, ``RGB`` or
``RGBA`` data.  It can also read files containing ``YCbCr`` data, which it
converts on read into ``RGB`` or ``RGBA`` depending on whether or not there is
an alpha channel.  PIL supports JPEG 2000 raw codestreams (``.j2k`` files), as
well as boxed JPEG 2000 files (``.j2p`` or ``.jpx`` files).  PIL does *not*
support files whose components have different sampling frequencies.

When loading, if you set the ``mode`` on the image prior to the
:py:meth:`~PIL.Image.Image.load` method being invoked, you can ask PIL to
convert the image to either ``RGB`` or ``RGBA`` rather than choosing for
itself.  It is also possible to set ``reduce`` to the number of resolutions to
discard (each one reduces the size of the resulting image by a factor of 2),
and ``layers`` to specify the number of quality layers to load.

The :py:meth:`~PIL.Image.Image.save` method supports the following options:

**offset**
    The image offset, as a tuple of integers, e.g. (16, 16)

**tile_offset**
    The tile offset, again as a 2-tuple of integers.

**tile_size**
    The tile size as a 2-tuple.  If not specified, or if set to None, the
    image will be saved without tiling.

**quality_mode**
    Either `"rates"` or `"dB"` depending on the units you want to use to
    specify image quality.

**quality_layers**
    A sequence of numbers, each of which represents either an approximate size
    reduction (if quality mode is `"rates"`) or a signal to noise ratio value
    in decibels.  If not specified, defaults to a single layer of full quality.

**num_resolutions**
    The number of different image resolutions to be stored (which corresponds
    to the number of Discrete Wavelet Transform decompositions plus one).

**codeblock_size**
    The code-block size as a 2-tuple.  Minimum size is 4 x 4, maximum is 1024 x
    1024, with the additional restriction that no code-block may have more
    than 4096 coefficients (i.e. the product of the two numbers must be no
    greater than 4096).

**precinct_size**
    The precinct size as a 2-tuple.  Must be a power of two along both axes,
    and must be greater than the code-block size.

**irreversible**
    If ``True``, use the lossy Irreversible Color Transformation
    followed by DWT 9-7.  Defaults to ``False``, which means to use the
    Reversible Color Transformation with DWT 5-3.

**progression**
    Controls the progression order; must be one of ``"LRCP"``, ``"RLCP"``,
    ``"RPCL"``, ``"PCRL"``, ``"CPRL"``.  The letters stand for Component,
    Position, Resolution and Layer respectively and control the order of
    encoding, the idea being that e.g. an image encoded using LRCP mode can
    have its quality layers decoded as they arrive at the decoder, while one
    encoded using RLCP mode will have increasing resolutions decoded as they
    arrive, and so on.

**cinema_mode**
    Set the encoder to produce output compliant with the digital cinema
    specifications.  The options here are ``"no"`` (the default),
    ``"cinema2k-24"`` for 24fps 2K, ``"cinema2k-48"`` for 48fps 2K, and
    ``"cinema4k-24"`` for 24fps 4K.  Note that for compliant 2K files,
    *at least one* of your image dimensions must match 2048 x 1080, while
    for compliant 4K files, *at least one* of the dimensions must match
    4096 x 2160.

.. note::

   To enable JPEG 2000 support, you need to build and install the OpenJPEG
   library, version 2.0.0 or higher, before building the Python Imaging
   Library.

   Windows users can install the OpenJPEG binaries available on the
   OpenJPEG website, but must add them to their PATH in order to use PIL (if
   you fail to do this, you will get errors about not being able to load the
   ``_imaging`` DLL).

MSP
^^^

PIL identifies and reads MSP files from Windows 1 and 2. The library writes
uncompressed (Windows 1) versions of this format.

PCX
^^^

PIL reads and writes PCX files containing ``1``, ``L``, ``P``, or ``RGB`` data.

PNG
^^^

PIL identifies, reads, and writes PNG files containing ``1``, ``L``, ``P``,
``RGB``, or ``RGBA`` data. Interlaced files are supported as of v1.1.7.

The :py:meth:`~PIL.Image.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties, when appropriate:

**gamma**
    Gamma, given as a floating point number.

**transparency**
    Transparency color index. This key is omitted if the image is not a
    transparent palette image.

The :py:meth:`~PIL.Image.Image.save` method supports the following options:

**optimize**
    If present, instructs the PNG writer to make the output file as small as
    possible. This includes extra processing in order to find optimal encoder
    settings.

**transparency** 
    For ``P``, ``L``, and ``RGB`` images, this option controls what
    color image to mark as transparent.

**bits (experimental)**
    For ``P`` images, this option controls how many bits to store. If omitted,
    the PNG writer uses 8 bits (256 colors).

**dictionary (experimental)**
    Set the ZLIB encoder dictionary.

.. note::

    To enable PNG support, you need to build and install the ZLIB compression
    library before building the Python Imaging Library. See the distribution
    README for details.

PPM
^^^

PIL reads and writes PBM, PGM and PPM files containing ``1``, ``L`` or ``RGB``
data.

SPIDER
^^^^^^

PIL reads and writes SPIDER image files of 32-bit floating point data
("F;32F").

PIL also reads SPIDER stack files containing sequences of SPIDER images. The
:py:meth:`~file.seek` and :py:meth:`~file.tell` methods are supported, and
random access is allowed.

The :py:meth:`~PIL.Image.Image.open` method sets the following attributes:

**format**
    Set to ``SPIDER``

**istack**
    Set to 1 if the file is an image stack, else 0.

**nimages**
    Set to the number of images in the stack.

A convenience method, :py:meth:`~PIL.Image.Image.convert2byte`, is provided for
converting floating point data to byte data (mode ``L``)::

    im = Image.open('image001.spi').convert2byte()

Writing files in SPIDER format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The extension of SPIDER files may be any 3 alphanumeric characters. Therefore
the output format must be specified explicitly::

    im.save('newimage.spi', format='SPIDER')

For more information about the SPIDER image processing package, see the
`SPIDER home page`_ at `Wadsworth Center`_.

.. _SPIDER home page: http://www.wadsworth.org/spider_doc/spider/docs/master.html
.. _Wadsworth Center: http://www.wadsworth.org/

TIFF
^^^^

PIL reads and writes TIFF files. It can read both striped and tiled images,
pixel and plane interleaved multi-band images, and either uncompressed, or
Packbits, LZW, or JPEG compressed images.

If you have libtiff and its headers installed, PIL can read and write many more
kinds of compressed TIFF files. If not, PIL will always write uncompressed
files.

The :py:meth:`~PIL.Image.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties:

**compression**
    Compression mode.

**dpi**
    Image resolution as an (xdpi, ydpi) tuple, where applicable. You can use
    the :py:attr:`~PIL.Image.Image.tag` attribute to get more detailed
    information about the image resolution.

    .. versionadded:: 1.1.5

In addition, the :py:attr:`~PIL.Image.Image.tag` attribute contains a
dictionary of decoded TIFF fields. Values are stored as either strings or
tuples. Note that only short, long and ASCII tags are correctly unpacked by
this release.

Saving Tiff Images
~~~~~~~~~~~~~~~~~~

The :py:meth:`~PIL.Image.Image.save` method can take the following keyword arguments:

**tiffinfo** 
    A :py:class:`~PIL.TiffImagePlugin.ImageFileDirectory` object or dict
    object containing tiff tags and values. The TIFF field type is
    autodetected for Numeric and string values, any other types
    require using an :py:class:`~PIL.TiffImagePlugin.ImageFileDirectory`
    object and setting the type in
    :py:attr:`~PIL.TiffImagePlugin.ImageFileDirectory.tagtype` with
    the appropriate numerical value from
    ``TiffTags.TYPES``.
 
    .. versionadded:: 2.3.0

**compression**
    A string containing the desired compression method for the
	file. (valid only with libtiff installed) Valid compression
	methods are: ``[None, "tiff_ccitt", "group3", "group4",
	"tiff_jpeg", "tiff_adobe_deflate", "tiff_thunderscan",
	"tiff_deflate", "tiff_sgilog", "tiff_sgilog24", "tiff_raw_16"]``

These arguments to set the tiff header fields are an alternative to using the general tags available through tiffinfo.

**description** 

**software**

**date time**

**artist**

**copyright**
    Strings

**resolution unit**
    A string of "inch", "centimeter" or "cm" 

**resolution**

**x resolution**

**y resolution**

**dpi**
    Either a Float, Integer, or 2 tuple of (numerator,
    denominator). Resolution implies an equal x and y resolution, dpi
    also implies a unit of inches.

WebP
^^^^

PIL reads and writes WebP files. The specifics of PIL's capabilities with this
format are currently undocumented.

The :py:meth:`~PIL.Image.Image.save` method supports the following options:

**lossless**
    If present, instructs the WEBP writer to use lossless
    compression.

**quality**
    Integer, 1-100, Defaults to 80. Sets the quality level for
    lossy compression.

**icc_procfile**
    The ICC Profile to include in the saved file. Only supported if
    the system webp library was built with webpmux support.

**exif**
    The exif data to include in the saved file. Only supported if
    the system webp library was built with webpmux support.

XBM
^^^

PIL reads and writes X bitmap files (mode ``1``).

XV Thumbnails
^^^^^^^^^^^^^

PIL can read XV thumbnail files.

Read-only formats
-----------------

CUR
^^^

CUR is used to store cursors on Windows. The CUR decoder reads the largest
available cursor. Animated cursors are not supported.

DCX
^^^

DCX is a container file format for PCX files, defined by Intel. The DCX format
is commonly used in fax applications. The DCX decoder can read files containing
``1``, ``L``, ``P``, or ``RGB`` data.

When the file is opened, only the first image is read. You can use
:py:meth:`~file.seek` or :py:mod:`~PIL.ImageSequence` to read other images.

FLI, FLC
^^^^^^^^

PIL reads Autodesk FLI and FLC animations.

The :py:meth:`~PIL.Image.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties:

**duration**
    The delay (in milliseconds) between each frame.

FPX
^^^

PIL reads Kodak FlashPix files. In the current version, only the highest
resolution image is read from the file, and the viewing transform is not taken
into account.

.. note::

    To enable full FlashPix support, you need to build and install the IJG JPEG
    library before building the Python Imaging Library. See the distribution
    README for details.

GBR
^^^

The GBR decoder reads GIMP brush files.

The :py:meth:`~PIL.Image.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties:

**description**
    The brush name.

GD
^^

PIL reads uncompressed GD files. Note that this file format cannot be
automatically identified, so you must use :py:func:`PIL.GdImageFile.open` to
read such a file.

The :py:meth:`~PIL.Image.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties:

**transparency**
    Transparency color index. This key is omitted if the image is not
    transparent.

ICO
^^^

ICO is used to store icons on Windows. The largest available icon is read.

ICNS
^^^^

PIL reads Mac OS X ``.icns`` files.  By default, the largest available icon is
read, though you can override this by setting the :py:attr:`~PIL.Image.Image.size`
property before calling :py:meth:`~PIL.Image.Image.load`.  The
:py:meth:`~PIL.Image.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` property:

**sizes**
    A list of supported sizes found in this icon file; these are a
    3-tuple, ``(width, height, scale)``, where ``scale`` is 2 for a retina
    icon and 1 for a standard icon.  You *are* permitted to use this 3-tuple
    format for the :py:attr:`~PIL.Image.Image.size` property if you set it
    before calling :py:meth:`~PIL.Image.Image.load`; after loading, the size
    will be reset to a 2-tuple containing pixel dimensions (so, e.g. if you
    ask for ``(512, 512, 2)``, the final value of
    :py:attr:`~PIL.Image.Image.size` will be ``(1024, 1024)``).

IMT
^^^

PIL reads Image Tools images containing ``L`` data.

IPTC/NAA
^^^^^^^^

PIL provides limited read support for IPTC/NAA newsphoto files.

MCIDAS
^^^^^^

PIL identifies and reads 8-bit McIdas area files.

MIC (read only)

PIL identifies and reads Microsoft Image Composer (MIC) files. When opened, the
first sprite in the file is loaded. You can use :py:meth:`~file.seek` and
:py:meth:`~file.tell` to read other sprites from the file.

PCD
^^^

PIL reads PhotoCD files containing ``RGB`` data. By default, the 768x512
resolution is read. You can use the :py:meth:`~PIL.Image.Image.draft` method to
read the lower resolution versions instead, thus effectively resizing the image
to 384x256 or 192x128. Higher resolutions cannot be read by the Python Imaging
Library.

PSD
^^^

PIL identifies and reads PSD files written by Adobe Photoshop 2.5 and 3.0.

SGI
^^^

PIL reads uncompressed ``L``, ``RGB``, and ``RGBA`` files.

TGA
^^^

PIL reads 24- and 32-bit uncompressed and run-length encoded TGA files.

WAL
^^^

.. versionadded:: 1.1.4

PIL reads Quake2 WAL texture files.

Note that this file format cannot be automatically identified, so you must use
the open function in the :py:mod:`~PIL.WalImageFile` module to read files in
this format.

By default, a Quake2 standard palette is attached to the texture. To override
the palette, use the putpalette method.

XPM
^^^

PIL reads X pixmap files (mode ``P``) with 256 colors or less.

The :py:meth:`~PIL.Image.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties:

**transparency**
    Transparency color index. This key is omitted if the image is not
    transparent.

Write-only formats
------------------

PALM
^^^^

PIL provides write-only support for PALM pixmap files.

The format code is ``Palm``, the extension is ``.palm``.

PDF
^^^

PIL can write PDF (Acrobat) images. Such images are written as binary PDF 1.1
files, using either JPEG or HEX encoding depending on the image mode (and
whether JPEG support is available or not).

PIXAR (read only)

PIL provides limited support for PIXAR raster files. The library can identify
and read “dumped” RGB files.

The format code is ``PIXAR``.

Identify-only formats
---------------------

BUFR
^^^^

.. versionadded:: 1.1.3

PIL provides a stub driver for BUFR files.

To add read or write support to your application, use
:py:func:`PIL.BufrStubImagePlugin.register_handler`.

FITS
^^^^

.. versionadded:: 1.1.5

PIL provides a stub driver for FITS files.

To add read or write support to your application, use
:py:func:`PIL.FitsStubImagePlugin.register_handler`.

GRIB
^^^^

.. versionadded:: 1.1.5

PIL provides a stub driver for GRIB files.

The driver requires the file to start with a GRIB header. If you have files
with embedded GRIB data, or files with multiple GRIB fields, your application
has to seek to the header before passing the file handle to PIL.

To add read or write support to your application, use
:py:func:`PIL.GribStubImagePlugin.register_handler`.

HDF5
^^^^

.. versionadded:: 1.1.5

PIL provides a stub driver for HDF5 files.

To add read or write support to your application, use
:py:func:`PIL.Hdf5StubImagePlugin.register_handler`.

MPEG
^^^^

PIL identifies MPEG files.

WMF
^^^

PIL can identify placable WMF files.

In PIL 1.1.4 and earlier, the WMF driver provides some limited rendering
support, but not enough to be useful for any real application.

In PIL 1.1.5 and later, the WMF driver is a stub driver. To add WMF read or
write support to your application, use
:py:func:`PIL.WmfImagePlugin.register_handler` to register a WMF handler.

::

    from PIL import Image
    from PIL import WmfImagePlugin

    class WmfHandler:
        def open(self, im):
            ...
        def load(self, im):
            ...
            return image
        def save(self, im, fp, filename):
            ...

    wmf_handler = WmfHandler()

    WmfImagePlugin.register_handler(wmf_handler)

    im = Image.open("sample.wmf")
