====================
The PIL.Image Module
====================

The PIL.Image Module
====================

**blend(im1, im2, alpha)** [`# <#PIL.Image.blend-function>`_]
    Creates a new image by interpolating between two input images, using
    a constant alpha.

    ::

           out = image1 * (1.0 - alpha) + image2 * alpha

    *im1*
    *im2*
    *alpha*
    Returns:

**composite(image1, image2, mask)**
[`# <#PIL.Image.composite-function>`_]

    *image1*
    *image2*
    *mask*

**eval(image, function)** [`# <#PIL.Image.eval-function>`_]

    *image*
    *function*
    Returns:

**frombuffer(mode, size, data, decoder\_name="raw", \*args)**
[`# <#PIL.Image.frombuffer-function>`_]
    (New in 1.1.4) Creates an image memory referencing pixel data in a
    byte buffer.

    This function is similar to
    `**frombytes** <#PIL.Image.frombytes-function>`_, but uses data in
    the byte buffer, where possible. This means that changes to the
    original buffer object are reflected in this image). Not all modes
    can share memory; support modes include "L", "RGBX", "RGBA", and
    "CMYK". For other modes, this function behaves like a corresponding
    call to the **fromstring** function.

    Note that this function decodes pixel data only, not entire images.
    If you have an entire image file in a string, wrap it in a
    **StringIO** object, and use `**open** <#PIL.Image.open-function>`_
    to load it.

    *mode*
    *size*
    *data*
    *decoder\_name*
    *\*args*
    Returns:

**frombytes(mode, size, data, decoder\_name="raw", \*args)**
[`# <#PIL.Image.frombytes-function>`_]
    Creates a copy of an image memory from pixel data in a buffer.

    In its simplest form, this function takes three arguments (mode,
    size, and unpacked pixel data).

    You can also use any pixel decoder supported by PIL. For more
    information on available decoders, see the section `*Writing Your
    Own File Decoder* <pil-decoder.htm>`_.

    Note that this function decodes pixel data only, not entire images.
    If you have an entire image in a string, wrap it in a **StringIO**
    object, and use `**open** <#PIL.Image.open-function>`_ to load it.

    *mode*
    *size*
    *data*
    *decoder\_name*
    *\*args*
    Returns:

**getmodebandnames(mode)** [`# <#PIL.Image.getmodebandnames-function>`_]
    Gets a list of individual band names. Given a mode, this function
    returns a tuple containing the names of individual bands (use
    `**getmodetype** <#PIL.Image.getmodetype-function>`_ to get the mode
    used to store each individual band.

    *mode*
    Returns:
    Raises **KeyError**:

**getmodebands(mode)** [`# <#PIL.Image.getmodebands-function>`_]

    *mode*
    Returns:
    Raises **KeyError**:

**getmodebase(mode)** [`# <#PIL.Image.getmodebase-function>`_]

    *mode*
    Returns:
    Raises **KeyError**:

**getmodetype(mode)** [`# <#PIL.Image.getmodetype-function>`_]

    *mode*
    Returns:
    Raises **KeyError**:

**Image()** (class) [`# <#PIL.Image.Image-class>`_]
    This class represents an image object.

    For more information about this class, see `*The Image
    Class* <#PIL.Image.Image-class>`_.

**init()** [`# <#PIL.Image.init-function>`_]
**isDirectory(f)** [`# <#PIL.Image.isDirectory-function>`_]
**isImageType(t)** [`# <#PIL.Image.isImageType-function>`_]
**isStringType(t)** [`# <#PIL.Image.isStringType-function>`_]
**merge(mode, bands)** [`# <#PIL.Image.merge-function>`_]

    *mode*
    *bands*
    Returns:

**new(mode, size, color=0)** [`# <#PIL.Image.new-function>`_]

    *mode*
    *size*
    *color*
    Returns:

**open(file, mode="r")** [`# <#PIL.Image.open-function>`_]
    Opens and identifies the given image file.

    This is a lazy operation; this function identifies the file, but the
    actual image data is not read from the file until you try to process
    the data (or call the `**load** <#PIL.Image.Image.load-method>`_
    method).

    *file*
        A filename (string) or a file object. The file object must
        implement **read**, **seek**, and **tell** methods, and be
        opened in binary mode.
    *mode*
    Returns:
    Raises **IOError**:

**preinit()** [`# <#PIL.Image.preinit-function>`_]
**register\_extension(id, extension)**
[`# <#PIL.Image.register_extension-function>`_]

    *id*
    *extension*

**register\_mime(id, mimetype)**
[`# <#PIL.Image.register_mime-function>`_]

    *id*
    *mimetype*

**register\_open(id, factory, accept=None)**
[`# <#PIL.Image.register_open-function>`_]

    *id*
    *factory*
    *accept*

**register\_save(id, driver)**
[`# <#PIL.Image.register_save-function>`_]

    *id*
    *driver*

The Image Class
---------------

**Image()** (class) [`# <#PIL.Image.Image-class>`_]
**convert(mode, matrix=None)** [`# <#PIL.Image.Image.convert-method>`_]
    Returns a converted copy of this image. For the "P" mode, this
    method translates pixels through the palette. If mode is omitted, a
    mode is chosen so that all information in the image and the palette
    can be represented without a palette.

    The current version supports all possible conversions between "L",
    "RGB" and "CMYK."

    When translating a colour image to black and white (mode "L"), the
    library uses the ITU-R 601-2 luma transform:

    **L = R \* 299/1000 + G \* 587/1000 + B \* 114/1000**

    When translating a greyscale image into a bilevel image (mode "1"),
    all non-zero values are set to 255 (white). To use other thresholds,
    use the `**point** <#PIL.Image.Image.point-method>`_ method.

    *mode*
    *matrix*
    Returns:

**copy()** [`# <#PIL.Image.Image.copy-method>`_]

    Returns:

**crop(box=None)** [`# <#PIL.Image.Image.crop-method>`_]
    Returns a rectangular region from this image. The box is a 4-tuple
    defining the left, upper, right, and lower pixel coordinate.

    This is a lazy operation. Changes to the source image may or may not
    be reflected in the cropped image. To break the connection, call the
    `**load** <#PIL.Image.Image.load-method>`_ method on the cropped
    copy.

    *The*
    Returns:

**draft(mode, size)** [`# <#PIL.Image.Image.draft-method>`_]
    Configures the image file loader so it returns a version of the
    image that as closely as possible matches the given mode and size.
    For example, you can use this method to convert a colour JPEG to
    greyscale while loading it, or to extract a 128x192 version from a
    PCD file.

    Note that this method modifies the Image object in place. If the
    image has already been loaded, this method has no effect.

    *mode*
    *size*

**filter(filter)** [`# <#PIL.Image.Image.filter-method>`_]
    Filters this image using the given filter. For a list of available
    filters, see the **ImageFilter** module.

    *filter*
    Returns:

**frombytes(data, decoder\_name="raw", \*args)**
[`# <#PIL.Image.Image.frombytes-method>`_]
    Loads this image with pixel data from a byte uffer.

    This method is similar to the
    `**frombytes** <#PIL.Image.frombytes-function>`_ function, but
    loads data into this image instead of creating a new image object.

    (In Python 2.6 and 2.7, this is also available as fromstring().)

**getbands()** [`# <#PIL.Image.Image.getbands-method>`_]
    Returns a tuple containing the name of each band in this image. For
    example, **getbands** on an RGB image returns ("R", "G", "B").

    Returns:

**getbbox()** [`# <#PIL.Image.Image.getbbox-method>`_]

    Returns:

**getcolors(maxcolors=256)** [`# <#PIL.Image.Image.getcolors-method>`_]

    *maxcolors*
    Returns:

**getdata(band=None)** [`# <#PIL.Image.Image.getdata-method>`_]
    Returns the contents of this image as a sequence object containing
    pixel values. The sequence object is flattened, so that values for
    line one follow directly after the values of line zero, and so on.

    Note that the sequence object returned by this method is an internal
    PIL data type, which only supports certain sequence operations. To
    convert it to an ordinary sequence (e.g. for printing), use
    **list(im.getdata())**.

    *band*
    Returns:

**getextrema()** [`# <#PIL.Image.Image.getextrema-method>`_]

    Returns:

**getim()** [`# <#PIL.Image.Image.getim-method>`_]

    Returns:

**getpalette()** [`# <#PIL.Image.Image.getpalette-method>`_]

    Returns:

**getpixel(xy)** [`# <#PIL.Image.Image.getpixel-method>`_]

    *xy*
    Returns:

**getprojection()** [`# <#PIL.Image.Image.getprojection-method>`_]

    Returns:

**histogram(mask=None)** [`# <#PIL.Image.Image.histogram-method>`_]
    Returns a histogram for the image. The histogram is returned as a
    list of pixel counts, one for each pixel value in the source image.
    If the image has more than one band, the histograms for all bands
    are concatenated (for example, the histogram for an "RGB" image
    contains 768 values).

    A bilevel image (mode "1") is treated as a greyscale ("L") image by
    this method.

    If a mask is provided, the method returns a histogram for those
    parts of the image where the mask image is non-zero. The mask image
    must have the same size as the image, and be either a bi-level image
    (mode "1") or a greyscale image ("L").

    *mask*
    Returns:

**load()** [`# <#PIL.Image.Image.load-method>`_]

    Returns:

**offset(xoffset, yoffset=None)**
[`# <#PIL.Image.Image.offset-method>`_]
    (Deprecated) Returns a copy of the image where the data has been
    offset by the given distances. Data wraps around the edges. If
    yoffset is omitted, it is assumed to be equal to xoffset.

    This method is deprecated. New code should use the **offset**
    function in the **ImageChops** module.

    *xoffset*
    *yoffset*
    Returns:

**paste(im, box=None, mask=None)**
[`# <#PIL.Image.Image.paste-method>`_]
    Pastes another image into this image. The box argument is either a
    2-tuple giving the upper left corner, a 4-tuple defining the left,
    upper, right, and lower pixel coordinate, or None (same as (0, 0)).
    If a 4-tuple is given, the size of the pasted image must match the
    size of the region.

    If the modes don't match, the pasted image is converted to the mode
    of this image (see the
    `**convert** <#PIL.Image.Image.convert-method>`_ method for
    details).

    Instead of an image, the source can be a integer or tuple containing
    pixel values. The method then fills the region with the given
    colour. When creating RGB images, you can also use colour strings as
    supported by the ImageColor module.

    If a mask is given, this method updates only the regions indicated
    by the mask. You can use either "1", "L" or "RGBA" images (in the
    latter case, the alpha band is used as mask). Where the mask is 255,
    the given image is copied as is. Where the mask is 0, the current
    value is preserved. Intermediate values can be used for transparency
    effects.

    Note that if you paste an "RGBA" image, the alpha band is ignored.
    You can work around this by using the same image as both source
    image and mask.

    *im*
    *box*
        An optional 4-tuple giving the region to paste into. If a
        2-tuple is used instead, it's treated as the upper left corner.
        If omitted or None, the source is pasted into the upper left
        corner.

        If an image is given as the second argument and there is no
        third, the box defaults to (0, 0), and the second argument is
        interpreted as a mask image.

    *mask*
    Returns:

**point(lut, mode=None)** [`# <#PIL.Image.Image.point-method>`_]

    *lut*
    *mode*
    Returns:

**putalpha(alpha)** [`# <#PIL.Image.Image.putalpha-method>`_]

    *im*

**putdata(data, scale=1.0, offset=0.0)**
[`# <#PIL.Image.Image.putdata-method>`_]
    Copies pixel data to this image. This method copies data from a
    sequence object into the image, starting at the upper left corner
    (0, 0), and continuing until either the image or the sequence ends.
    The scale and offset values are used to adjust the sequence values:
    **pixel = value\*scale + offset**.

    *data*
    *scale*
    *offset*

**putpalette(data)** [`# <#PIL.Image.Image.putpalette-method>`_]

    *data*

**putpixel(xy, value)** [`# <#PIL.Image.Image.putpixel-method>`_]
    Modifies the pixel at the given position. The colour is given as a
    single numerical value for single-band images, and a tuple for
    multi-band images.

    Note that this method is relatively slow. For more extensive
    changes, use `**paste** <#PIL.Image.Image.paste-method>`_ or the
    **ImageDraw** module instead.

    *xy*
    *value*

**resize(size, filter=NEAREST)** [`# <#PIL.Image.Image.resize-method>`_]

    *size*
    *filter*
        An optional resampling filter. This can be one of **NEAREST**
        (use nearest neighbour), **BILINEAR** (linear interpolation in a
        2x2 environment), **BICUBIC** (cubic spline interpolation in a
        4x4 environment), or **ANTIALIAS** (a high-quality downsampling
        filter). If omitted, or if the image has mode "1" or "P", it is
        set **NEAREST**.
    Returns:

**rotate(angle, filter=NEAREST)**
[`# <#PIL.Image.Image.rotate-method>`_]

    *angle*
    *filter*
        An optional resampling filter. This can be one of **NEAREST**
        (use nearest neighbour), **BILINEAR** (linear interpolation in a
        2x2 environment), or **BICUBIC** (cubic spline interpolation in
        a 4x4 environment). If omitted, or if the image has mode "1" or
        "P", it is set **NEAREST**.
    Returns:

**save(file, format=None, \*\*options)**
[`# <#PIL.Image.Image.save-method>`_]
    Saves this image under the given filename. If no format is
    specified, the format to use is determined from the filename
    extension, if possible.

    Keyword options can be used to provide additional instructions to
    the writer. If a writer doesn't recognise an option, it is silently
    ignored. The available options are described later in this handbook.

    You can use a file object instead of a filename. In this case, you
    must always specify the format. The file object must implement the
    **seek**, **tell**, and **write** methods, and be opened in binary
    mode.

    *file*
    *format*
    *\*\*options*
    Returns:
    Raises **KeyError**:
    Raises **IOError**:

**seek(frame)** [`# <#PIL.Image.Image.seek-method>`_]
    Seeks to the given frame in this sequence file. If you seek beyond
    the end of the sequence, the method raises an **EOFError**
    exception. When a sequence file is opened, the library automatically
    seeks to frame 0.

    Note that in the current version of the library, most sequence
    formats only allows you to seek to the next frame.

    *frame*
    Raises **EOFError**:

**show(title=None)** [`# <#PIL.Image.Image.show-method>`_]
    Displays this image. This method is mainly intended for debugging
    purposes.

    On Unix platforms, this method saves the image to a temporary PPM
    file, and calls the **xv** utility.

    On Windows, it saves the image to a temporary BMP file, and uses the
    standard BMP display utility to show it (usually Paint).

    *title*

**split()** [`# <#PIL.Image.Image.split-method>`_]

    Returns:

**tell()** [`# <#PIL.Image.Image.tell-method>`_]

    Returns:

**thumbnail(size, resample=NEAREST)**
[`# <#PIL.Image.Image.thumbnail-method>`_]
    Make this image into a thumbnail. This method modifies the image to
    contain a thumbnail version of itself, no larger than the given
    size. This method calculates an appropriate thumbnail size to
    preserve the aspect of the image, calls the
    `**draft** <#PIL.Image.Image.draft-method>`_ method to configure the
    file reader (where applicable), and finally resizes the image.

    Note that the bilinear and bicubic filters in the current version of
    PIL are not well-suited for thumbnail generation. You should use
    **ANTIALIAS** unless speed is much more important than quality.

    Also note that this function modifies the Image object in place. If
    you need to use the full resolution image as well, apply this method
    to a `**copy** <#PIL.Image.Image.copy-method>`_ of the original
    image.

    *size*
    *resample*
        Optional resampling filter. This can be one of **NEAREST**,
        **BILINEAR**, **BICUBIC**, or **ANTIALIAS** (best quality). If
        omitted, it defaults to **NEAREST** (this will be changed to
        ANTIALIAS in a future version).
    Returns:

**tobitmap(name="image")** [`# <#PIL.Image.Image.tobitmap-method>`_]

    *name*
    Returns:
    Raises **ValueError**:

**tobytes(encoder\_name="raw", \*args)**
[`# <#PIL.Image.Image.tobytes-method>`_]
    (In Python 2.6 and 2.7, this is also available as tostring().)

    *encoder\_name*
    *\*args*
    Returns:

**transform(size, method, data, resample=NEAREST)**
[`# <#PIL.Image.Image.transform-method>`_]
    Transforms this image. This method creates a new image with the
    given size, and the same mode as the original, and copies data to
    the new image using the given transform.

    *size*
    *method*
        The transformation method. This is one of **EXTENT** (cut out a
        rectangular subregion), **AFFINE** (affine transform),
        **PERSPECTIVE** (perspective transform), **QUAD** (map a
        quadrilateral to a rectangle), or **MESH** (map a number of
        source quadrilaterals in one operation).
    *data*
    *resample*
        Optional resampling filter. It can be one of **NEAREST** (use
        nearest neighbour), **BILINEAR** (linear interpolation in a 2x2
        environment), or **BICUBIC** (cubic spline interpolation in a
        4x4 environment). If omitted, or if the image has mode "1" or
        "P", it is set to **NEAREST**.
    Returns:

**transpose(method)** [`# <#PIL.Image.Image.transpose-method>`_]

    *method*
        One of **FLIP\_LEFT\_RIGHT**, **FLIP\_TOP\_BOTTOM**,
        **ROTATE\_90**, **ROTATE\_180**, or **ROTATE\_270**.

**verify()** [`# <#PIL.Image.Image.verify-method>`_]
