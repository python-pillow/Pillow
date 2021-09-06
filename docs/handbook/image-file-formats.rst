.. _image-file-formats:

Image file formats
==================

The Python Imaging Library supports a wide variety of raster file formats.
Over 30 different file formats can be identified and read by the library.
Write support is less extensive, but most common interchange and presentation
formats are supported.

The :py:meth:`~PIL.Image.open` function identifies files from their
contents, not their names, but the :py:meth:`~PIL.Image.Image.save` method
looks at the name to determine which format to use, unless the format is given
explicitly.

When an image is opened from a file, only that instance of the image is considered to
have the format. Copies of the image will contain data loaded from the file, but not
the file itself, meaning that it can no longer be considered to be in the original
format. So if :py:meth:`~PIL.Image.Image.copy` is called on an image, or another method
internally creates a copy of the image, the ``fp`` (file pointer), along with any
methods and attributes specific to a format. The :py:attr:`~PIL.Image.Image.format`
attribute will be ``None``.

Fully supported formats
-----------------------

.. contents::

BMP
^^^

Pillow reads and writes Windows and OS/2 BMP files containing ``1``, ``L``, ``P``,
or ``RGB`` data. 16-colour images are read as ``P`` images. Run-length encoding
is not supported.

The :py:meth:`~PIL.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties:

**compression**
    Set to ``bmp_rle`` if the file is run-length encoded.

DDS
^^^

DDS is a popular container texture format used in video games and natively supported
by DirectX. Uncompressed RGB and RGBA can be read, and (since 8.3.0) written. DXT1,
DXT3 (since 3.4.0) and DXT5 pixel formats can be read, only in ``RGBA`` mode.

DIB
^^^

Pillow reads and writes DIB files. DIB files are similar to BMP files, so see
above for more information.

    .. versionadded:: 6.0.0

EPS
^^^

Pillow identifies EPS files containing image data, and can read files that
contain embedded raster images (ImageData descriptors). If Ghostscript is
available, other EPS files can be read as well. The EPS driver can also write
EPS images. The EPS driver can read EPS images in ``L``, ``LAB``, ``RGB`` and
``CMYK`` mode, but Ghostscript may convert the images to ``RGB`` mode rather
than leaving them in the original color space. The EPS driver can write images
in ``L``, ``RGB`` and ``CMYK`` modes.

If Ghostscript is available, you can call the :py:meth:`~PIL.Image.Image.load`
method with the following parameters to affect how Ghostscript renders the EPS

**scale**
    Affects the scale of the resultant rasterized image. If the EPS suggests
    that the image be rendered at 100px x 100px, setting this parameter to
    2 will make the Ghostscript render a 200px x 200px image instead. The
    relative position of the bounding box is maintained::

        im = Image.open(...)
        im.size #(100,100)
        im.load(scale=2)
        im.size #(200,200)

**transparency**
    If true, generates an RGBA image with a transparent background, instead of
    the default behaviour of an RGB image with a white background.


GIF
^^^

Pillow reads GIF87a and GIF89a versions of the GIF file format. The library
writes run-length encoded files in GIF87a by default, unless GIF89a features
are used or GIF89a is already in use.

Note that GIF files are always read as grayscale (``L``)
or palette mode (``P``) images.

The :py:meth:`~PIL.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties:

**background**
    Default background color (a palette color index).

**transparency**
    Transparency color index. This key is omitted if the image is not
    transparent.

**version**
    Version (either ``GIF87a`` or ``GIF89a``).

**duration**
    May not be present. The time to display the current frame
    of the GIF, in milliseconds.

**loop**
    May not be present. The number of times the GIF should loop. 0 means that
    it will loop forever.

**comment**
    May not be present. A comment about the image.

**extension**
    May not be present. Contains application specific information.

Reading sequences
~~~~~~~~~~~~~~~~~

The GIF loader supports the :py:meth:`~PIL.Image.Image.seek` and
:py:meth:`~PIL.Image.Image.tell` methods. You can combine these methods
to seek to the next frame (``im.seek(im.tell() + 1)``).

``im.seek()`` raises an :py:exc:`EOFError` if you try to seek after the last frame.

Saving
~~~~~~

When calling :py:meth:`~PIL.Image.Image.save` to write a GIF file, the
following options are available::

    im.save(out, save_all=True, append_images=[im1, im2, ...])

**save_all**
    If present and true, all frames of the image will be saved. If
    not, then only the first frame of a multiframe image will be saved.

**append_images**
    A list of images to append as additional frames. Each of the
    images in the list can be single or multiframe images.
    This is currently supported for GIF, PDF, PNG, TIFF, and WebP.

    It is also supported for ICO and ICNS. If images are passed in of relevant
    sizes, they will be used instead of scaling down the main image.

**include_color_table**
    Whether or not to include local color table.

**interlace**
    Whether or not the image is interlaced. By default, it is, unless the image
    is less than 16 pixels in width or height.

**disposal**
    Indicates the way in which the graphic is to be treated after being displayed.

    * 0 - No disposal specified.
    * 1 - Do not dispose.
    * 2 - Restore to background color.
    * 3 - Restore to previous content.

     Pass a single integer for a constant disposal, or a list or tuple
     to set the disposal for each frame separately.

**palette**
    Use the specified palette for the saved image. The palette should
    be a bytes or bytearray object containing the palette entries in
    RGBRGB... form. It should be no more than 768 bytes. Alternately,
    the palette can be passed in as an
    :py:class:`PIL.ImagePalette.ImagePalette` object.

**optimize**
    If present and true, attempt to compress the palette by
    eliminating unused colors. This is only useful if the palette can
    be compressed to the next smaller power of 2 elements.

Note that if the image you are saving comes from an existing GIF, it may have
the following properties in its :py:attr:`~PIL.Image.Image.info` dictionary.
For these options, if you do not pass them in, they will default to
their :py:attr:`~PIL.Image.Image.info` values.

**transparency**
    Transparency color index.

**duration**
    The display duration of each frame of the multiframe gif, in
    milliseconds. Pass a single integer for a constant duration, or a
    list or tuple to set the duration for each frame separately.

**loop**
    Integer number of times the GIF should loop. 0 means that it will loop
    forever. By default, the image will not loop.

**comment**
    A comment about the image.

Reading local images
~~~~~~~~~~~~~~~~~~~~

The GIF loader creates an image memory the same size as the GIF file’s *logical
screen size*, and pastes the actual pixel data (the *local image*) into this
image. If you only want the actual pixel rectangle, you can manipulate the
:py:attr:`~PIL.Image.Image.size` and :py:attr:`~PIL.ImageFile.ImageFile.tile`
attributes before loading the file::

    im = Image.open(...)

    if im.tile[0][0] == "gif":
        # only read the first "local image" from this GIF file
        tag, (x0, y0, x1, y1), offset, extra = im.tile[0]
        im.size = (x1 - x0, y1 - y0)
        im.tile = [(tag, (0, 0) + im.size, offset, extra)]

ICNS
^^^^

Pillow reads and writes macOS ``.icns`` files.  By default, the
largest available icon is read, though you can override this by setting the
:py:attr:`~PIL.Image.Image.size` property before calling
:py:meth:`~PIL.Image.Image.load`.  The :py:meth:`~PIL.Image.open` method
sets the following :py:attr:`~PIL.Image.Image.info` property:

.. note::

    Prior to version 8.3.0, Pillow could only write ICNS files on macOS.

**sizes**
    A list of supported sizes found in this icon file; these are a
    3-tuple, ``(width, height, scale)``, where ``scale`` is 2 for a retina
    icon and 1 for a standard icon.  You *are* permitted to use this 3-tuple
    format for the :py:attr:`~PIL.Image.Image.size` property if you set it
    before calling :py:meth:`~PIL.Image.Image.load`; after loading, the size
    will be reset to a 2-tuple containing pixel dimensions (so, e.g. if you
    ask for ``(512, 512, 2)``, the final value of
    :py:attr:`~PIL.Image.Image.size` will be ``(1024, 1024)``).

The :py:meth:`~PIL.Image.Image.save` method can take the following keyword arguments:

**append_images**
    A list of images to replace the scaled down versions of the image.
    The order of the images does not matter, as their use is determined by
    the size of each image.

    .. versionadded:: 5.1.0

ICO
^^^

ICO is used to store icons on Windows. The largest available icon is read.

The :py:meth:`~PIL.Image.Image.save` method supports the following options:

**sizes**
    A list of sizes including in this ico file; these are a 2-tuple,
    ``(width, height)``; Default to ``[(16, 16), (24, 24), (32, 32), (48, 48),
    (64, 64), (128, 128), (256, 256)]``. Any sizes bigger than the original
    size or 256 will be ignored.

The :py:meth:`~PIL.Image.Image.save` method can take the following keyword arguments:

**append_images**
    A list of images to replace the scaled down versions of the image.
    The order of the images does not matter, as their use is determined by
    the size of each image.

    .. versionadded:: 8.1.0

**bitmap_format**
    By default, the image data will be saved in PNG format. With a bitmap format of
    "bmp", image data will be saved in BMP format instead.

    .. versionadded:: 8.3.0

IM
^^

IM is a format used by LabEye and other applications based on the IFUNC image
processing library. The library reads and writes most uncompressed interchange
versions of this format.

IM is the only format that can store all internal Pillow formats.

JPEG
^^^^

Pillow reads JPEG, JFIF, and Adobe JPEG files containing ``L``, ``RGB``, or
``CMYK`` data. It writes standard and progressive JFIF files.

Using the :py:meth:`~PIL.Image.Image.draft` method, you can speed things up by
converting ``RGB`` images to ``L``, and resize images to 1/2, 1/4 or 1/8 of
their original size while loading them.

By default Pillow doesn't allow loading of truncated JPEG files, set
:data:`.ImageFile.LOAD_TRUNCATED_IMAGES` to override this.

The :py:meth:`~PIL.Image.open` method may set the following
:py:attr:`~PIL.Image.Image.info` properties if available:

**jfif**
    JFIF application marker found. If the file is not a JFIF file, this key is
    not present.

**jfif_version**
    A tuple representing the jfif version, (major version, minor version).

**jfif_density**
    A tuple representing the pixel density of the image, in units specified
    by jfif_unit.

**jfif_unit**
    Units for the jfif_density:

    * 0 - No Units
    * 1 - Pixels per Inch
    * 2 - Pixels per Centimeter

**dpi**
    A tuple representing the reported pixel density in pixels per inch, if
    the file is a jfif file and the units are in inches.

**adobe**
    Adobe application marker found. If the file is not an Adobe JPEG file, this
    key is not present.

**adobe_transform**
    Vendor Specific Tag.

**progression**
    Indicates that this is a progressive JPEG file.

**icc_profile**
    The ICC color profile for the image.

**exif**
    Raw EXIF data from the image.

**comment**
    A comment about the image.

    .. versionadded:: 7.1.0


The :py:meth:`~PIL.Image.Image.save` method supports the following options:

**quality**
    The image quality, on a scale from 0 (worst) to 95 (best). The default is
    75. Values above 95 should be avoided; 100 disables portions of the JPEG
    compression algorithm, and results in large files with hardly any gain in
    image quality.

**optimize**
    If present and true, indicates that the encoder should make an extra pass
    over the image in order to select optimal encoder settings.

**progressive**
    If present and true, indicates that this image should be stored as a
    progressive JPEG file.

**dpi**
    A tuple of integers representing the pixel density, ``(x,y)``.

**icc_profile**
    If present and true, the image is stored with the provided ICC profile.
    If this parameter is not provided, the image will be saved with no profile
    attached. To preserve the existing profile::

        im.save(filename, 'jpeg', icc_profile=im.info.get('icc_profile'))

**exif**
    If present, the image will be stored with the provided raw EXIF data.

**subsampling**
    If present, sets the subsampling for the encoder.

    * ``keep``: Only valid for JPEG files, will retain the original image setting.
    * ``4:4:4``, ``4:2:2``, ``4:2:0``: Specific sampling values
    * ``-1``: equivalent to ``keep``
    * ``0``: equivalent to ``4:4:4``
    * ``1``: equivalent to ``4:2:2``
    * ``2``: equivalent to ``4:2:0``

**qtables**
    If present, sets the qtables for the encoder. This is listed as an
    advanced option for wizards in the JPEG documentation. Use with
    caution. ``qtables`` can be one of several types of values:

    *  a string, naming a preset, e.g. ``keep``, ``web_low``, or ``web_high``
    *  a list, tuple, or dictionary (with integer keys =
       range(len(keys))) of lists of 64 integers. There must be
       between 2 and 4 tables.

    .. versionadded:: 2.5.0


.. note::

    To enable JPEG support, you need to build and install the IJG JPEG library
    before building the Python Imaging Library. See the distribution README for
    details.

JPEG 2000
^^^^^^^^^

.. versionadded:: 2.4.0

Pillow reads and writes JPEG 2000 files containing ``L``, ``LA``, ``RGB`` or
``RGBA`` data.  It can also read files containing ``YCbCr`` data, which it
converts on read into ``RGB`` or ``RGBA`` depending on whether or not there is
an alpha channel.  Pillow supports JPEG 2000 raw codestreams (``.j2k`` files),
as well as boxed JPEG 2000 files (``.j2p`` or ``.jpx`` files).  Pillow does
*not* support files whose components have different sampling frequencies.

When loading, if you set the ``mode`` on the image prior to the
:py:meth:`~PIL.Image.Image.load` method being invoked, you can ask Pillow to
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
    Either ``"rates"`` or ``"dB"`` depending on the units you want to use to
    specify image quality.

**quality_layers**
    A sequence of numbers, each of which represents either an approximate size
    reduction (if quality mode is ``"rates"``) or a signal to noise ratio value
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
   OpenJPEG website, but must add them to their PATH in order to use Pillow (if
   you fail to do this, you will get errors about not being able to load the
   ``_imaging`` DLL).

MSP
^^^

Pillow identifies and reads MSP files from Windows 1 and 2. The library writes
uncompressed (Windows 1) versions of this format.

PCX
^^^

Pillow reads and writes PCX files containing ``1``, ``L``, ``P``, or ``RGB`` data.

PNG
^^^

Pillow identifies, reads, and writes PNG files containing ``1``, ``L``, ``LA``,
``I``, ``P``, ``RGB`` or ``RGBA`` data. Interlaced files are supported as of
v1.1.7.

As of Pillow 6.0, EXIF data can be read from PNG images. However, unlike other
image formats, EXIF data is not guaranteed to be present in
:py:attr:`~PIL.Image.Image.info` until :py:meth:`~PIL.Image.Image.load` has been
called.

By default Pillow doesn't allow loading of truncated PNG files, set
:data:`.ImageFile.LOAD_TRUNCATED_IMAGES` to override this.

The :py:func:`~PIL.Image.open` function sets the following
:py:attr:`~PIL.Image.Image.info` properties, when appropriate:

**chromaticity**
    The chromaticity points, as an 8 tuple of floats. (``White Point
    X``, ``White Point Y``, ``Red X``, ``Red Y``, ``Green X``, ``Green
    Y``, ``Blue X``, ``Blue Y``)

**gamma**
    Gamma, given as a floating point number.

**srgb**
    The sRGB rendering intent as an integer.

      * 0 Perceptual
      * 1 Relative Colorimetric
      * 2 Saturation
      * 3 Absolute Colorimetric

**transparency**
    For ``P`` images: Either the palette index for full transparent pixels,
    or a byte string with alpha values for each palette entry.

    For ``1``, ``L``, ``I`` and ``RGB`` images, the color that represents
    full transparent pixels in this image.

    This key is omitted if the image is not a transparent palette image.

.. _png-text:

``open`` also sets ``Image.text`` to a dictionary of the values of the
``tEXt``, ``zTXt``, and ``iTXt`` chunks of the PNG image. Individual
compressed chunks are limited to a decompressed size of
:data:`.PngImagePlugin.MAX_TEXT_CHUNK`, by default 1MB, to prevent
decompression bombs. Additionally, the total size of all of the text
chunks is limited to :data:`.PngImagePlugin.MAX_TEXT_MEMORY`, defaulting to
64MB.

The :py:meth:`~PIL.Image.Image.save` method supports the following options:

**optimize**
    If present and true, instructs the PNG writer to make the output file as
    small as possible. This includes extra processing in order to find optimal
    encoder settings.

**transparency**
    For ``P``, ``1``, ``L``, ``I``, and ``RGB`` images, this option controls
    what color from the image to mark as transparent.

    For ``P`` images, this can be a either the palette index,
    or a byte string with alpha values for each palette entry.

**dpi**
    A tuple of two numbers corresponding to the desired dpi in each direction.

**pnginfo**
    A :py:class:`PIL.PngImagePlugin.PngInfo` instance containing chunks.

**compress_level**
    ZLIB compression level, a number between 0 and 9: 1 gives best speed,
    9 gives best compression, 0 gives no compression at all. Default is 6.
    When ``optimize`` option is True ``compress_level`` has no effect
    (it is set to 9 regardless of a value passed).

**icc_profile**
    The ICC Profile to include in the saved file.

**exif**
    The exif data to include in the saved file.

    .. versionadded:: 6.0.0

**bits (experimental)**
    For ``P`` images, this option controls how many bits to store. If omitted,
    the PNG writer uses 8 bits (256 colors).

**dictionary (experimental)**
    Set the ZLIB encoder dictionary.

.. note::

    To enable PNG support, you need to build and install the ZLIB compression
    library before building the Python Imaging Library. See the
    :doc:`installation documentation <../installation>` for details.

.. _apng-sequences:

APNG sequences
~~~~~~~~~~~~~~

The PNG loader includes limited support for reading and writing Animated Portable
Network Graphics (APNG) files.
When an APNG file is loaded, :py:meth:`~PIL.ImageFile.ImageFile.get_format_mimetype`
will return ``"image/apng"``. The value of the :py:attr:`~PIL.Image.Image.is_animated`
property will be ``True`` when the :py:attr:`~PIL.Image.Image.n_frames` property is
greater than 1. For APNG files, the ``n_frames`` property depends on both the animation
frame count as well as the presence or absence of a default image. See the
``default_image`` property documentation below for more details.
The :py:meth:`~PIL.Image.Image.seek` and :py:meth:`~PIL.Image.Image.tell` methods
are supported.

``im.seek()`` raises an :py:exc:`EOFError` if you try to seek after the last frame.

These :py:attr:`~PIL.Image.Image.info` properties will be set for APNG frames,
where applicable:

**default_image**
    Specifies whether or not this APNG file contains a separate default image,
    which is not a part of the actual APNG animation.

    When an APNG file contains a default image, the initially loaded image (i.e.
    the result of ``seek(0)``) will be the default image.
    To account for the presence of the default image, the
    :py:attr:`~PIL.Image.Image.n_frames` property will be set to ``frame_count + 1``,
    where ``frame_count`` is the actual APNG animation frame count.
    To load the first APNG animation frame, ``seek(1)`` must be called.

    * ``True`` - The APNG contains default image, which is not an animation frame.
    * ``False`` - The APNG does not contain a default image. The ``n_frames`` property
      will be set to the actual APNG animation frame count.
      The initially loaded image (i.e. ``seek(0)``) will be the first APNG animation
      frame.

**loop**
    The number of times to loop this APNG, 0 indicates infinite looping.

**duration**
    The time to display this APNG frame (in milliseconds).

.. note::

    The APNG loader returns images the same size as the APNG file's logical screen size.
    The returned image contains the pixel data for a given frame, after applying
    any APNG frame disposal and frame blend operations (i.e. it contains what a web
    browser would render for this frame - the composite of all previous frames and this
    frame).

    Any APNG file containing sequence errors is treated as an invalid image. The APNG
    loader will not attempt to repair and reorder files containing sequence errors.

.. _apng-saving:

Saving
~~~~~~

When calling :py:meth:`~PIL.Image.Image.save`, by default only a single frame PNG file
will be saved. To save an APNG file (including a single frame APNG), the ``save_all``
parameter must be set to ``True``. The following parameters can also be set:

**default_image**
    Boolean value, specifying whether or not the base image is a default image.
    If ``True``, the base image will be used as the default image, and the first image
    from the ``append_images`` sequence will be the first APNG animation frame.
    If ``False``, the base image will be used as the first APNG animation frame.
    Defaults to ``False``.

**append_images**
    A list or tuple of images to append as additional frames. Each of the
    images in the list can be single or multiframe images. The size of each frame
    should match the size of the base image. Also note that if a frame's mode does
    not match that of the base image, the frame will be converted to the base image
    mode.

**loop**
    Integer number of times to loop this APNG, 0 indicates infinite looping.
    Defaults to 0.

**duration**
    Integer (or list or tuple of integers) length of time to display this APNG frame
    (in milliseconds).
    Defaults to 0.

**disposal**
    An integer (or list or tuple of integers) specifying the APNG disposal
    operation to be used for this frame before rendering the next frame.
    Defaults to 0.

    * 0 (:py:data:`~PIL.PngImagePlugin.APNG_DISPOSE_OP_NONE`, default) -
      No disposal is done on this frame before rendering the next frame.
    * 1 (:py:data:`PIL.PngImagePlugin.APNG_DISPOSE_OP_BACKGROUND`) -
      This frame's modified region is cleared to fully transparent black before
      rendering the next frame.
    * 2 (:py:data:`~PIL.PngImagePlugin.APNG_DISPOSE_OP_PREVIOUS`) -
      This frame's modified region is reverted to the previous frame's contents before
      rendering the next frame.

**blend**
    An integer (or list or tuple of integers) specifying the APNG blend
    operation to be used for this frame before rendering the next frame.
    Defaults to 0.

    * 0 (:py:data:`~PIL.PngImagePlugin.APNG_BLEND_OP_SOURCE`) -
      All color components of this frame, including alpha, overwrite the previous output
      image contents.
    * 1 (:py:data:`~PIL.PngImagePlugin.APNG_BLEND_OP_OVER`) -
      This frame should be alpha composited with the previous output image contents.

.. note::

    The ``duration``, ``disposal`` and ``blend`` parameters can be set to lists or tuples to
    specify values for each individual frame in the animation. The length of the list or tuple
    must be identical to the total number of actual frames in the APNG animation.
    If the APNG contains a default image (i.e. ``default_image`` is set to ``True``),
    these list or tuple parameters should not include an entry for the default image.


PPM
^^^

Pillow reads and writes PBM, PGM, PPM and PNM files containing ``1``, ``L`` or
``RGB`` data.

SGI
^^^

Pillow reads and writes uncompressed ``L``, ``RGB``, and ``RGBA`` files.


SPIDER
^^^^^^

Pillow reads and writes SPIDER image files of 32-bit floating point data
("F;32F").

Pillow also reads SPIDER stack files containing sequences of SPIDER images. The
:py:meth:`~PIL.Image.Image.seek` and :py:meth:`~PIL.Image.Image.tell` methods are supported, and
random access is allowed.

The :py:meth:`~PIL.Image.open` method sets the following attributes:

**format**
    Set to ``SPIDER``

**istack**
    Set to 1 if the file is an image stack, else 0.

**n_frames**
    Set to the number of images in the stack.

A convenience method, :py:meth:`~PIL.SpiderImagePlugin.SpiderImageFile.convert2byte`,
is provided for converting floating point data to byte data (mode ``L``)::

    im = Image.open('image001.spi').convert2byte()

Writing files in SPIDER format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The extension of SPIDER files may be any 3 alphanumeric characters. Therefore
the output format must be specified explicitly::

    im.save('newimage.spi', format='SPIDER')

For more information about the SPIDER image processing package, see the
`SPIDER homepage`_ at `Wadsworth Center`_.

.. _SPIDER homepage: https://spider.wadsworth.org/spider_doc/spider/docs/spider.html
.. _Wadsworth Center: https://www.wadsworth.org/

TGA
^^^

Pillow reads and writes TGA images containing ``L``, ``LA``, ``P``,
``RGB``, and ``RGBA`` data. Pillow can read and write both uncompressed and
run-length encoded TGAs.

TIFF
^^^^

Pillow reads and writes TIFF files. It can read both striped and tiled
images, pixel and plane interleaved multi-band images. If you have
libtiff and its headers installed, Pillow can read and write many kinds
of compressed TIFF files. If not, Pillow will only read and write
uncompressed files.

.. note::

    Beginning in version 5.0.0, Pillow requires libtiff to read or
    write compressed files. Prior to that release, Pillow had buggy
    support for reading Packbits, LZW and JPEG compressed TIFFs
    without using libtiff.

The :py:meth:`~PIL.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties:

**compression**
    Compression mode.

    .. versionadded:: 2.0.0

**dpi**
    Image resolution as an ``(xdpi, ydpi)`` tuple, where applicable. You can use
    the :py:attr:`~PIL.TiffImagePlugin.TiffImageFile.tag` attribute to get more
    detailed information about the image resolution.

    .. versionadded:: 1.1.5

**resolution**
    Image resolution as an ``(xres, yres)`` tuple, where applicable. This is a
    measurement in whichever unit is specified by the file.

    .. versionadded:: 1.1.5


The :py:attr:`~PIL.TiffImagePlugin.TiffImageFile.tag_v2` attribute contains a
dictionary of TIFF metadata. The keys are numerical indexes from
:py:data:`.TiffTags.TAGS_V2`.  Values are strings or numbers for single
items, multiple values are returned in a tuple of values. Rational
numbers are returned as a :py:class:`~PIL.TiffImagePlugin.IFDRational`
object.

    .. versionadded:: 3.0.0

For compatibility with legacy code, the
:py:attr:`~PIL.TiffImagePlugin.TiffImageFile.tag` attribute contains a dictionary
of decoded TIFF fields as returned prior to version 3.0.0.  Values are
returned as either strings or tuples of numeric values. Rational
numbers are returned as a tuple of ``(numerator, denominator)``.

    .. deprecated:: 3.0.0

Reading Multi-frame TIFF Images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The TIFF loader supports the :py:meth:`~PIL.Image.Image.seek` and
:py:meth:`~PIL.Image.Image.tell` methods, taking and returning frame numbers
within the image file. You can combine these methods to seek to the next frame
(``im.seek(im.tell() + 1)``). Frames are numbered from 0 to ``im.n_frames - 1``,
and can be accessed in any order.

``im.seek()`` raises an :py:exc:`EOFError` if you try to seek after the
last frame.

Saving Tiff Images
~~~~~~~~~~~~~~~~~~

The :py:meth:`~PIL.Image.Image.save` method can take the following keyword arguments:

**save_all**
    If true, Pillow will save all frames of the image to a multiframe tiff document.

    .. versionadded:: 3.4.0

**append_images**
    A list of images to append as additional frames. Each of the
    images in the list can be single or multiframe images. Note however, that for
    correct results, all the appended images should have the same
    ``encoderinfo`` and ``encoderconfig`` properties.

    .. versionadded:: 4.2.0

**tiffinfo**
    A :py:class:`~PIL.TiffImagePlugin.ImageFileDirectory_v2` object or dict
    object containing tiff tags and values. The TIFF field type is
    autodetected for Numeric and string values, any other types
    require using an :py:class:`~PIL.TiffImagePlugin.ImageFileDirectory_v2`
    object and setting the type in
    :py:attr:`~PIL.TiffImagePlugin.ImageFileDirectory_v2.tagtype` with
    the appropriate numerical value from
    :py:data:`.TiffTags.TYPES`.

    .. versionadded:: 2.3.0

    Metadata values that are of the rational type should be passed in
    using a :py:class:`~PIL.TiffImagePlugin.IFDRational` object.

    .. versionadded:: 3.1.0

    For compatibility with legacy code, a
    :py:class:`~PIL.TiffImagePlugin.ImageFileDirectory_v1` object may
    be passed in this field. However, this is deprecated.

    .. versionadded:: 5.4.0

    Previous versions only supported some tags when writing using
    libtiff. The supported list is found in
    :py:data:`.TiffTags.LIBTIFF_CORE`.

    .. versionadded:: 6.1.0

    Added support for signed types (e.g. ``TIFF_SIGNED_LONG``) and multiple values.
    Multiple values for a single tag must be to
    :py:class:`~PIL.TiffImagePlugin.ImageFileDirectory_v2` as a tuple and
    require a matching type in
    :py:attr:`~PIL.TiffImagePlugin.ImageFileDirectory_v2.tagtype` tagtype.

**exif**
    Alternate keyword to "tiffinfo", for consistency with other formats.

    .. versionadded:: 8.4.0

**compression**
    A string containing the desired compression method for the
    file. (valid only with libtiff installed) Valid compression
    methods are: :data:`None`, ``"group3"``, ``"group4"``, ``"jpeg"``, ``"lzma"``,
    ``"packbits"``, ``"tiff_adobe_deflate"``, ``"tiff_ccitt"``, ``"tiff_lzw"``,
    ``"tiff_raw_16"``, ``"tiff_sgilog"``, ``"tiff_sgilog24"``, ``"tiff_thunderscan"``,
    ``"webp"`, ``"zstd"``

**quality**
    The image quality for JPEG compression, on a scale from 0 (worst) to 100
    (best). The default is 75.

    .. versionadded:: 6.1.0

These arguments to set the tiff header fields are an alternative to
using the general tags available through tiffinfo.

**description**

**software**

**date_time**

**artist**

**copyright**
    Strings

**icc_profile**
    The ICC Profile to include in the saved file.

**resolution_unit**
    An integer. 1 for no unit, 2 for inches and 3 for centimeters.

**resolution**
    Either an integer or a float, used for both the x and y resolution.

**x_resolution**
    Either an integer or a float.

**y_resolution**
    Either an integer or a float.

**dpi**
    A tuple of (x_resolution, y_resolution), with inches as the resolution
    unit. For consistency with other image formats, the x and y resolutions
    of the dpi will be rounded to the nearest integer.


WebP
^^^^

Pillow reads and writes WebP files. The specifics of Pillow's capabilities with
this format are currently undocumented.

The :py:meth:`~PIL.Image.Image.save` method supports the following options:

**lossless**
    If present and true, instructs the WebP writer to use lossless compression.

**quality**
    Integer, 1-100, Defaults to 80. For lossy, 0 gives the smallest
    size and 100 the largest. For lossless, this parameter is the amount
    of effort put into the compression: 0 is the fastest, but gives larger
    files compared to the slowest, but best, 100.

**method**
    Quality/speed trade-off (0=fast, 6=slower-better). Defaults to 4.

**icc_profile**
    The ICC Profile to include in the saved file. Only supported if
    the system WebP library was built with webpmux support.

**exif**
    The exif data to include in the saved file. Only supported if
    the system WebP library was built with webpmux support.

Saving sequences
~~~~~~~~~~~~~~~~~

.. note::

    Support for animated WebP files will only be enabled if the system WebP
    library is v0.5.0 or later. You can check webp animation support at
    runtime by calling ``features.check("webp_anim")``.

When calling :py:meth:`~PIL.Image.Image.save` to write a WebP file, by default
only the first frame of a multiframe image will be saved. If the ``save_all``
argument is present and true, then all frames will be saved, and the following
options will also be available.

**append_images**
    A list of images to append as additional frames. Each of the
    images in the list can be single or multiframe images.

**duration**
    The display duration of each frame, in milliseconds. Pass a single
    integer for a constant duration, or a list or tuple to set the
    duration for each frame separately.

**loop**
    Number of times to repeat the animation. Defaults to [0 = infinite].

**background**
    Background color of the canvas, as an RGBA tuple with values in
    the range of (0-255).

**minimize_size**
    If true, minimize the output size (slow). Implicitly disables
    key-frame insertion.

**kmin, kmax**
    Minimum and maximum distance between consecutive key frames in
    the output. The library may insert some key frames as needed
    to satisfy this criteria. Note that these conditions should
    hold: kmax > kmin and kmin >= kmax / 2 + 1. Also, if kmax <= 0,
    then key-frame insertion is disabled; and if kmax == 1, then all
    frames will be key-frames (kmin value does not matter for these
    special cases).

**allow_mixed**
    If true, use mixed compression mode; the encoder heuristically
    chooses between lossy and lossless for each frame.

XBM
^^^

Pillow reads and writes X bitmap files (mode ``1``).

Read-only formats
-----------------

BLP
^^^

BLP is the Blizzard Mipmap Format, a texture format used in World of
Warcraft. Pillow supports reading ``JPEG`` Compressed or raw ``BLP1``
images, and all types of ``BLP2`` images.

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
:py:meth:`~PIL.Image.Image.seek` or :py:mod:`~PIL.ImageSequence` to read other images.

FLI, FLC
^^^^^^^^

Pillow reads Autodesk FLI and FLC animations.

The :py:meth:`~PIL.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties:

**duration**
    The delay (in milliseconds) between each frame.

FPX
^^^

Pillow reads Kodak FlashPix files. In the current version, only the highest
resolution image is read from the file, and the viewing transform is not taken
into account.

.. note::

    To enable full FlashPix support, you need to build and install the IJG JPEG
    library before building the Python Imaging Library. See the distribution
    README for details.

FTEX
^^^^

.. versionadded:: 3.2.0

The FTEX decoder reads textures used for 3D objects in
Independence War 2: Edge Of Chaos. The plugin reads a single texture
per file, in the compressed and uncompressed formats.

GBR
^^^

The GBR decoder reads GIMP brush files, version 1 and 2.

The :py:meth:`~PIL.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties:

**comment**
    The brush name.

**spacing**
    The spacing between the brushes, in pixels. Version 2 only.

GD
^^

Pillow reads uncompressed GD2 files. Note that you must use
:py:func:`PIL.GdImageFile.open` to read such a file.

The :py:meth:`~PIL.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties:

**transparency**
    Transparency color index. This key is omitted if the image is not
    transparent.

IMT
^^^

Pillow reads Image Tools images containing ``L`` data.

IPTC/NAA
^^^^^^^^

Pillow provides limited read support for IPTC/NAA newsphoto files.

MCIDAS
^^^^^^

Pillow identifies and reads 8-bit McIdas area files.

MIC
^^^

Pillow identifies and reads Microsoft Image Composer (MIC) files. When opened,
the first sprite in the file is loaded. You can use :py:meth:`~PIL.Image.Image.seek` and
:py:meth:`~PIL.Image.Image.tell` to read other sprites from the file.

Note that there may be an embedded gamma of 2.2 in MIC files.

MPO
^^^

Pillow identifies and reads Multi Picture Object (MPO) files, loading the primary
image when first opened. The :py:meth:`~PIL.Image.Image.seek` and :py:meth:`~PIL.Image.Image.tell`
methods may be used to read other pictures from the file. The pictures are
zero-indexed and random access is supported.

PCD
^^^

Pillow reads PhotoCD files containing ``RGB`` data. This only reads the 768x512
resolution image from the file. Higher resolutions are encoded in a proprietary
encoding.

PIXAR
^^^^^

Pillow provides limited support for PIXAR raster files. The library can
identify and read “dumped” RGB files.

The format code is ``PIXAR``.

PSD
^^^

Pillow identifies and reads PSD files written by Adobe Photoshop 2.5 and 3.0.


WAL
^^^

.. versionadded:: 1.1.4

Pillow reads Quake2 WAL texture files.

Note that this file format cannot be automatically identified, so you must use
the open function in the :py:mod:`~PIL.WalImageFile` module to read files in
this format.

By default, a Quake2 standard palette is attached to the texture. To override
the palette, use the putpalette method.

WMF
^^^

Pillow can identify WMF files.

On Windows, it can read WMF files. By default, it will load the image at 72
dpi. To load it at another resolution:

.. code-block:: python

    from PIL import Image
    with Image.open("drawing.wmf") as im:
        im.load(dpi=144)

To add other read or write support, use
:py:func:`PIL.WmfImagePlugin.register_handler` to register a WMF handler.

.. code-block:: python

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

XPM
^^^

Pillow reads X pixmap files (mode ``P``) with 256 colors or less.

The :py:meth:`~PIL.Image.open` method sets the following
:py:attr:`~PIL.Image.Image.info` properties:

**transparency**
    Transparency color index. This key is omitted if the image is not
    transparent.

Write-only formats
------------------

PALM
^^^^

Pillow provides write-only support for PALM pixmap files.

The format code is ``Palm``, the extension is ``.palm``.

PDF
^^^

Pillow can write PDF (Acrobat) images. Such images are written as binary PDF 1.4
files, using either JPEG or HEX encoding depending on the image mode (and
whether JPEG support is available or not).

The :py:meth:`~PIL.Image.Image.save` method can take the following keyword arguments:

**save_all**
    If a multiframe image is used, by default, only the first image will be saved.
    To save all frames, each frame to a separate page of the PDF, the ``save_all``
    parameter must be present and set to ``True``.

    .. versionadded:: 3.0.0

**append_images**
    A list of :py:class:`PIL.Image.Image` objects to append as additional pages. Each
    of the images in the list can be single or multiframe images. The ``save_all``
    parameter must be present and set to ``True`` in conjunction with
    ``append_images``.

    .. versionadded:: 4.2.0

**append**
    Set to True to append pages to an existing PDF file. If the file doesn't
    exist, an :py:exc:`OSError` will be raised.

    .. versionadded:: 5.1.0

**resolution**
    Image resolution in DPI. This, together with the number of pixels in the
    image, will determine the physical dimensions of the page that will be
    saved in the PDF.

**title**
    The document’s title. If not appending to an existing PDF file, this will
    default to the filename.

    .. versionadded:: 5.1.0

**author**
    The name of the person who created the document.

    .. versionadded:: 5.1.0

**subject**
    The subject of the document.

    .. versionadded:: 5.1.0

**keywords**
    Keywords associated with the document.

    .. versionadded:: 5.1.0

**creator**
    If the document was converted to PDF from another format, the name of the
    conforming product that created the original document from which it was
    converted.

    .. versionadded:: 5.1.0

**producer**
    If the document was converted to PDF from another format, the name of the
    conforming product that converted it to PDF.

    .. versionadded:: 5.1.0

**creationDate**
    The creation date of the document. If not appending to an existing PDF
    file, this will default to the current time.

    .. versionadded:: 5.3.0

**modDate**
    The modification date of the document. If not appending to an existing PDF
    file, this will default to the current time.

    .. versionadded:: 5.3.0

XV Thumbnails
^^^^^^^^^^^^^

Pillow can read XV thumbnail files.

Identify-only formats
---------------------

BUFR
^^^^

.. versionadded:: 1.1.3

Pillow provides a stub driver for BUFR files.

To add read or write support to your application, use
:py:func:`PIL.BufrStubImagePlugin.register_handler`.

FITS
^^^^

.. versionadded:: 1.1.5

Pillow provides a stub driver for FITS files.

To add read or write support to your application, use
:py:func:`PIL.FitsStubImagePlugin.register_handler`.

GRIB
^^^^

.. versionadded:: 1.1.5

Pillow provides a stub driver for GRIB files.

The driver requires the file to start with a GRIB header. If you have files
with embedded GRIB data, or files with multiple GRIB fields, your application
has to seek to the header before passing the file handle to Pillow.

To add read or write support to your application, use
:py:func:`PIL.GribStubImagePlugin.register_handler`.

HDF5
^^^^

.. versionadded:: 1.1.5

Pillow provides a stub driver for HDF5 files.

To add read or write support to your application, use
:py:func:`PIL.Hdf5StubImagePlugin.register_handler`.

MPEG
^^^^

Pillow identifies MPEG files.
