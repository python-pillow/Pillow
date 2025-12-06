.. py:module:: PIL.ImageMorph
.. py:currentmodule:: PIL.ImageMorph

:py:mod:`~PIL.ImageMorph` module
================================

The :py:mod:`~PIL.ImageMorph` module provides morphological operations for
binary and grayscale images. Morphology is a family of image-processing
techniques based on the shape and structure of regions in an image. Basic
uses are dilation, erosion, edge detection, and hit or miss pattern
matching.

``ImageMorph`` works by applying a lookup table (LUT) to a binary representation
of the input image. Patterns used for these operations are defined using small
ASCII masks, which are converted into LUTs through :class:`LutBuilder`. The
resulting LUTs can then be applied to an image using :class:`MorphOp`.

This module is useful for tasks such as noise cleanup, detecting specific
pixel shapes, extracting boundaries, thinning, or locating features defined by
small structuring elements.


Supported image modes
---------------------

Morphological operations in Pillow operate on images in mode ``"L"`` (8-bit
grayscale). A nonzero pixel is treated as “on”, and a zero-valued pixel as
“off”. To apply morphology to a binary image, ensure that the image is first
converted to mode ``"L"``::

    im = im.convert("L")

For best results, use images with values restricted to 0 (black) and 255
(white), though intermediate grayscale values are also supported.


Defining structuring element patterns
-------------------------------------

A structuring pattern is defined using a small ASCII mask consisting of the
characters:

* ``1`` — pixel must be “on”
* ``0`` — pixel must be “off”
* ``-`` — “don’t care” value (ignored during matching)

For example, this mask detects a 2×2 corner shape::

    pattern = [
        "10",
        "11",
    ]

Multiple patterns can be combined into a single LUT. Patterns must all be the
same size, and Pillow builds a lookup table from them using
:class:`LutBuilder`.


Using :class:`LutBuilder`
-------------------------

The :class:`LutBuilder` class constructs a LUT that defines how a morphological
operation should behave. A LUT maps every possible 3×3 neighborhood around a
pixel to an output pixel value (either “on” or “off”).

Basic uses like dilation and erosion can be created by specifying
preset names (``"dilation4"``, ``"dilation8"``, ``"erosion4"``,
``"erosion8"``, ``"edge"``), or you may define custom patterns.

For example, creating a LUT for a 2×2 corner detector::

    from PIL import ImageMorph

    patterns = [
        "10",
        "11",
    ]

    lb = ImageMorph.LutBuilder(op_name="corner")
    lb.add_patterns(patterns)
    lut = lb.build_lut()

You can inspect, save, or reuse the LUT with :meth:`LutBuilder.get_lut`,
:meth:`MorphOp.load_lut`, or :meth:`MorphOp.save_lut`.


Applying morphology with :class:`MorphOp`
-----------------------------------------

Once a LUT is created, the :class:`MorphOp` class applies it to an image. The
:meth:`MorphOp.apply` method performs the morphological operation and returns
a tuple ``(count, out_image)`` where:

* ``count`` is the number of pixels that changed, and
* ``out_image`` is the resulting processed image.

Example: applying a simple dilation operation::

    from PIL import Image, ImageMorph

    with Image.open("input.png") as im:
        im = im.convert("L")

        # Built-in 8-connected dilation
        op = ImageMorph.MorphOp(op_name="dilation8")

        count, out = op.apply(im)
    out.save("dilated.png")

You could also use the method :meth:`MorphOp.match` to check where a pattern
matches without modifying the image, and :meth:`MorphOp.get_on_pixels` to
get the coordinates of “on” pixels after pattern matching.

Example: pattern matching without modifying the image::

    op = ImageMorph.MorphOp(op_name="edge")
    result = op.match(im)

    # result is a list of (x, y) coordinates
    print("Edge pixels found:", len(result))


Saving and loading LUTs
-----------------------

LUTs created by :class:`LutBuilder` can be serialized and reused later. This
is helpful when repeatedly applying the same pattern in a batch-processing
workflow.

Example::

    lb = ImageMorph.LutBuilder(op_name="custom")
    lb.add_patterns(patterns)
    lb.build_lut()
    lb.save_lut("custom.lut")

    # Later...
    op = ImageMorph.MorphOp()
    op.load_lut("custom.lut")
    count, out = op.apply(im)

.. autoclass:: LutBuilder
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: MorphOp
    :members:
    :undoc-members:
    :show-inheritance:
