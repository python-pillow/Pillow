#
# The Python Imaging Library.
# $Id$
#
# standard channel operations
#
# History:
# 1996-03-24 fl   Created
# 1996-08-13 fl   Added logical operations (for "1" images)
# 2000-10-12 fl   Added offset method (from Image.py)
#
# Copyright (c) 1997-2000 by Secret Labs AB
# Copyright (c) 1996-2000 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

import Image

##
# The <b>ImageChops</b> module contains a number of arithmetical image
# operations, called <i>channel operations</i> ("chops"). These can be
# used for various purposes, including special effects, image
# compositions, algorithmic painting, and more.
# <p>
# At this time, channel operations are only implemented for 8-bit
# images (e.g. &quot;L&quot; and &quot;RGB&quot;).
# <p>
# Most channel operations take one or two image arguments and returns
# a new image.  Unless otherwise noted, the result of a channel
# operation is always clipped to the range 0 to MAX (which is 255 for
# all modes supported by the operations in this module).
##

##
# Return an image with the same size as the given image, but filled
# with the given pixel value.
#
# @param image Reference image.
# @param value Pixel value.
# @return An image object.

def constant(image, value):
    "Fill a channel with a given grey level"

    return Image.new("L", image.size, value)

##
# Copy image.
#
# @param image Source image.
# @return A copy of the source image.

def duplicate(image):
    "Create a copy of a channel"

    return image.copy()

##
# Inverts an image
# (MAX - image).
#
# @param image Source image.
# @return An image object.

def invert(image):
    "Invert a channel"

    image.load()
    return image._new(image.im.chop_invert())

##
# Compare images, and return lighter pixel value
# (max(image1, image2)).
# <p>
# Compares the two images, pixel by pixel, and returns a new image
# containing the lighter values.
#
# @param image1 First image.
# @param image1 Second image.
# @return An image object.

def lighter(image1, image2):
    "Select the lighter pixels from each image"

    image1.load()
    image2.load()
    return image1._new(image1.im.chop_lighter(image2.im))

##
# Compare images, and return darker pixel value
# (min(image1, image2)).
# <p>
# Compares the two images, pixel by pixel, and returns a new image
# containing the darker values.
#
# @param image1 First image.
# @param image1 Second image.
# @return An image object.

def darker(image1, image2):
    "Select the darker pixels from each image"

    image1.load()
    image2.load()
    return image1._new(image1.im.chop_darker(image2.im))

##
# Calculate absolute difference
# (abs(image1 - image2)).
# <p>
# Returns the absolute value of the difference between the two images.
#
# @param image1 First image.
# @param image1 Second image.
# @return An image object.

def difference(image1, image2):
    "Subtract one image from another"

    image1.load()
    image2.load()
    return image1._new(image1.im.chop_difference(image2.im))

##
# Superimpose positive images
# (image1 * image2 / MAX).
# <p>
# Superimposes two images on top of each other. If you multiply an
# image with a solid black image, the result is black. If you multiply
# with a solid white image, the image is unaffected.
#
# @param image1 First image.
# @param image1 Second image.
# @return An image object.

def multiply(image1, image2):
    "Superimpose two positive images"

    image1.load()
    image2.load()
    return image1._new(image1.im.chop_multiply(image2.im))

##
# Superimpose negative images
# (MAX - ((MAX - image1) * (MAX - image2) / MAX)).
# <p>
# Superimposes two inverted images on top of each other.
#
# @param image1 First image.
# @param image1 Second image.
# @return An image object.

def screen(image1, image2):
    "Superimpose two negative images"

    image1.load()
    image2.load()
    return image1._new(image1.im.chop_screen(image2.im))

##
# Add images
# ((image1 + image2) / scale + offset).
# <p>
# Adds two images, dividing the result by scale and adding the
# offset. If omitted, scale defaults to 1.0, and offset to 0.0.
#
# @param image1 First image.
# @param image1 Second image.
# @return An image object.

def add(image1, image2, scale=1.0, offset=0):
    "Add two images"

    image1.load()
    image2.load()
    return image1._new(image1.im.chop_add(image2.im, scale, offset))

##
# Subtract images
# ((image1 - image2) / scale + offset).
# <p>
# Subtracts two images, dividing the result by scale and adding the
# offset. If omitted, scale defaults to 1.0, and offset to 0.0.
#
# @param image1 First image.
# @param image1 Second image.
# @return An image object.

def subtract(image1, image2, scale=1.0, offset=0):
    "Subtract two images"

    image1.load()
    image2.load()
    return image1._new(image1.im.chop_subtract(image2.im, scale, offset))

##
# Add images without clipping
# ((image1 + image2) % MAX).
# <p>
# Adds two images, without clipping the result.
#
# @param image1 First image.
# @param image1 Second image.
# @return An image object.

def add_modulo(image1, image2):
    "Add two images without clipping"

    image1.load()
    image2.load()
    return image1._new(image1.im.chop_add_modulo(image2.im))

##
# Subtract images without clipping
# ((image1 - image2) % MAX).
# <p>
# Subtracts two images, without clipping the result.
#
# @param image1 First image.
# @param image1 Second image.
# @return An image object.

def subtract_modulo(image1, image2):
    "Subtract two images without clipping"

    image1.load()
    image2.load()
    return image1._new(image1.im.chop_subtract_modulo(image2.im))

##
# Logical AND
# (image1 and image2).

def logical_and(image1, image2):
    "Logical and between two images"

    image1.load()
    image2.load()
    return image1._new(image1.im.chop_and(image2.im))

##
# Logical OR
# (image1 or image2).

def logical_or(image1, image2):
    "Logical or between two images"

    image1.load()
    image2.load()
    return image1._new(image1.im.chop_or(image2.im))

##
# Logical XOR
# (image1 xor image2).

def logical_xor(image1, image2):
    "Logical xor between two images"

    image1.load()
    image2.load()
    return image1._new(image1.im.chop_xor(image2.im))

##
# Blend images using constant transparency weight.
# <p>
# Same as the <b>blend</b> function in the <b>Image</b> module.

def blend(image1, image2, alpha):
    "Blend two images using a constant transparency weight"

    return Image.blend(image1, image2, alpha)

##
# Create composite using transparency mask.
# <p>
# Same as the <b>composite</b> function in the <b>Image</b> module.

def composite(image1, image2, mask):
    "Create composite image by blending images using a transparency mask"

    return Image.composite(image1, image2, mask)

##
# Offset image data.
# <p>
# Returns a copy of the image where data has been offset by the given
# distances.  Data wraps around the edges.  If yoffset is omitted, it
# is assumed to be equal to xoffset.
#
# @param image Source image.
# @param xoffset The horizontal distance.
# @param yoffset The vertical distance.  If omitted, both
#    distances are set to the same value.
# @return An Image object.

def offset(image, xoffset, yoffset=None):
    "Offset image in horizontal and/or vertical direction"
    if yoffset is None:
        yoffset = xoffset
    image.load()
    return image._new(image.im.offset(xoffset, yoffset))
