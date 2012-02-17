=========================
The PIL.ImageChops Module
=========================

The PIL.ImageChops Module
=========================

The **ImageChops** module contains a number of arithmetical image
operations, called *channel operations* ("chops"). These can be used for
various purposes, including special effects, image compositions,
algorithmic painting, and more.

At this time, channel operations are only implemented for 8-bit images
(e.g. "L" and "RGB").

Most channel operations take one or two image arguments and returns a
new image. Unless otherwise noted, the result of a channel operation is
always clipped to the range 0 to MAX (which is 255 for all modes
supported by the operations in this module).

Module Contents
---------------

**add(image1, image2, scale=1.0, offset=0)**
[`# <#PIL.ImageChops.add-function>`_]
    Add images ((image1 + image2) / scale + offset).

    Adds two images, dividing the result by scale and adding the offset.
    If omitted, scale defaults to 1.0, and offset to 0.0.

    *image1*
    *image1*
    Returns:

**add\_modulo(image1, image2)**
[`# <#PIL.ImageChops.add_modulo-function>`_]
    Add images without clipping ((image1 + image2) % MAX).

    Adds two images, without clipping the result.

    *image1*
    *image1*
    Returns:

**blend(image1, image2, alpha)** [`# <#PIL.ImageChops.blend-function>`_]
    Blend images using constant transparency weight.

    Same as the **blend** function in the **Image** module.

**composite(image1, image2, mask)**
[`# <#PIL.ImageChops.composite-function>`_]
    Create composite using transparency mask.

    Same as the **composite** function in the **Image** module.

**constant(image, value)** [`# <#PIL.ImageChops.constant-function>`_]

    *image*
    *value*
    Returns:

**darker(image1, image2)** [`# <#PIL.ImageChops.darker-function>`_]
    Compare images, and return darker pixel value (min(image1, image2)).

    Compares the two images, pixel by pixel, and returns a new image
    containing the darker values.

    *image1*
    *image1*
    Returns:

**difference(image1, image2)**
[`# <#PIL.ImageChops.difference-function>`_]
    Calculate absolute difference (abs(image1 - image2)).

    Returns the absolute value of the difference between the two images.

    *image1*
    *image1*
    Returns:

**duplicate(image)** [`# <#PIL.ImageChops.duplicate-function>`_]

    *image*
    Returns:

**invert(image)** [`# <#PIL.ImageChops.invert-function>`_]

    *image*
    Returns:

**lighter(image1, image2)** [`# <#PIL.ImageChops.lighter-function>`_]
    Compare images, and return lighter pixel value (max(image1,
    image2)).

    Compares the two images, pixel by pixel, and returns a new image
    containing the lighter values.

    *image1*
    *image1*
    Returns:

**logical\_and(image1, image2)**
[`# <#PIL.ImageChops.logical_and-function>`_]
**logical\_or(image1, image2)**
[`# <#PIL.ImageChops.logical_or-function>`_]
**logical\_xor(image1, image2)**
[`# <#PIL.ImageChops.logical_xor-function>`_]
**multiply(image1, image2)** [`# <#PIL.ImageChops.multiply-function>`_]
    Superimpose positive images (image1 \* image2 / MAX).

    Superimposes two images on top of each other. If you multiply an
    image with a solid black image, the result is black. If you multiply
    with a solid white image, the image is unaffected.

    *image1*
    *image1*
    Returns:

**offset(image, xoffset, yoffset=None)**
[`# <#PIL.ImageChops.offset-function>`_]
    Offset image data.

    Returns a copy of the image where data has been offset by the given
    distances. Data wraps around the edges. If yoffset is omitted, it is
    assumed to be equal to xoffset.

    *image*
    *xoffset*
    *yoffset*
    Returns:

**screen(image1, image2)** [`# <#PIL.ImageChops.screen-function>`_]
    Superimpose negative images (MAX - ((MAX - image1) \* (MAX - image2)
    / MAX)).

    Superimposes two inverted images on top of each other.

    *image1*
    *image1*
    Returns:

**subtract(image1, image2, scale=1.0, offset=0)**
[`# <#PIL.ImageChops.subtract-function>`_]
    Subtract images ((image1 - image2) / scale + offset).

    Subtracts two images, dividing the result by scale and adding the
    offset. If omitted, scale defaults to 1.0, and offset to 0.0.

    *image1*
    *image1*
    Returns:

**subtract\_modulo(image1, image2)**
[`# <#PIL.ImageChops.subtract_modulo-function>`_]
    Subtract images without clipping ((image1 - image2) % MAX).

    Subtracts two images, without clipping the result.

    *image1*
    *image1*
    Returns:

