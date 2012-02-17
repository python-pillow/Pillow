=======================
The PIL.ImageOps Module
=======================

The PIL.ImageOps Module
=======================

(New in 1.1.3) The **ImageOps** module contains a number of 'ready-made'
image processing operations. This module is somewhat experimental, and
most operators only work on L and RGB images.

Module Contents
---------------

**autocontrast(image, cutoff=0, ignore=None)**
[`# <#PIL.ImageOps.autocontrast-function>`_]
    Maximize (normalize) image contrast. This function calculates a
    histogram of the input image, removes *cutoff* percent of the
    lightest and darkest pixels from the histogram, and remaps the image
    so that the darkest pixel becomes black (0), and the lightest
    becomes white (255).

    *image*
    *cutoff*
    *ignore*
    Returns:

**colorize(image, black, white)**
[`# <#PIL.ImageOps.colorize-function>`_]
    Colorize grayscale image. The *black* and *white* arguments should
    be RGB tuples; this function calculates a colour wedge mapping all
    black pixels in the source image to the first colour, and all white
    pixels to the second colour.

    *image*
    *black*
    *white*
    Returns:

**crop(image, border=0)** [`# <#PIL.ImageOps.crop-function>`_]

    *image*
    *border*
    Returns:

**deform(image, deformer, resample=Image.BILINEAR)**
[`# <#PIL.ImageOps.deform-function>`_]

    *image*
    *deformer*
    *resample*
    Returns:

**equalize(image, mask=None)** [`# <#PIL.ImageOps.equalize-function>`_]

    *image*
    *mask*
    Returns:

**expand(image, border=0, fill=0)**
[`# <#PIL.ImageOps.expand-function>`_]

    *image*
    *border*
    *fill*
    Returns:

**fit(image, size, method=Image.NEAREST, bleed=0.0, centering=(0.5,
0.5))** [`# <#PIL.ImageOps.fit-function>`_]
    Returns a sized and cropped version of the image, cropped to the
    requested aspect ratio and size.

    The **fit** function was contributed by Kevin Cazabon.

    *size*
    *method*
    *bleed*
    *centering*
    Returns:

**flip(image)** [`# <#PIL.ImageOps.flip-function>`_]

    *image*
    Returns:

**grayscale(image)** [`# <#PIL.ImageOps.grayscale-function>`_]

    *image*
    Returns:

**invert(image)** [`# <#PIL.ImageOps.invert-function>`_]

    *image*
    Returns:

**mirror(image)** [`# <#PIL.ImageOps.mirror-function>`_]

    *image*
    Returns:

**posterize(image, bits)** [`# <#PIL.ImageOps.posterize-function>`_]

    *image*
    *bits*
    Returns:

**solarize(image, threshold=128)**
[`# <#PIL.ImageOps.solarize-function>`_]

    *image*
    *threshold*
    Returns:

