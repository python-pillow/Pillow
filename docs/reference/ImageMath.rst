.. py:module:: PIL.ImageMath
.. py:currentmodule:: PIL.ImageMath

:py:mod:`ImageMath` Module
==========================

The :py:mod:`ImageMath` module can be used to evaluate “image expressions”. The
module provides a single eval function, which takes an expression string and
one or more images.

Example: Using the :py:mod:`~PIL.ImageMath` module
--------------------------------------------------

.. code-block:: python

    import Image, ImageMath

    im1 = Image.open("image1.jpg")
    im2 = Image.open("image2.jpg")

    out = ImageMath.eval("convert(min(a, b), 'L')", a=im1, b=im2)
    out.save("result.png")

.. py:function:: eval(expression, environment)

    Evaluate expression in the given environment.

    In the current version, :py:mod:`~PIL.ImageMath` only supports
    single-layer images. To process multi-band images, use the
    :py:meth:`~PIL.Image.Image.split` method or :py:func:`~PIL.Image.merge` 
    function.

    :param expression: A string which uses the standard Python expression
                       syntax. In addition to the standard operators, you can
                       also use the functions described below.
    :param environment: A dictionary that maps image names to Image instances.
                        You can use one or more keyword arguments instead of a
                        dictionary, as shown in the above example. Note that
                        the names must be valid Python identifiers.
    :return: An image, an integer value, a floating point value,
             or a pixel tuple, depending on the expression.

Expression syntax
-----------------

Expressions are standard Python expressions, but they’re evaluated in a
non-standard environment. You can use PIL methods as usual, plus the following
set of operators and functions:

Standard Operators
^^^^^^^^^^^^^^^^^^

You can use standard arithmetical operators for addition (+), subtraction (-),
multiplication (*), and division (/).

The module also supports unary minus (-), modulo (%), and power (**) operators.

Note that all operations are done with 32-bit integers or 32-bit floating
point values, as necessary. For example, if you add two 8-bit images, the
result will be a 32-bit integer image. If you add a floating point constant to
an 8-bit image, the result will be a 32-bit floating point image.

You can force conversion using the :py:func:`~PIL.ImageMath.convert`,
:py:func:`~PIL.ImageMath.float`, and :py:func:`~PIL.ImageMath.int` functions
described below.

Bitwise Operators
^^^^^^^^^^^^^^^^^

The module also provides operations that operate on individual bits. This
includes and (&), or (|), and exclusive or (^). You can also invert (~) all
pixel bits.

Note that the operands are converted to 32-bit signed integers before the
bitwise operation is applied. This means that you’ll get negative values if
you invert an ordinary greyscale image. You can use the and (&) operator to
mask off unwanted bits.

Bitwise operators don’t work on floating point images.

Logical Operators
^^^^^^^^^^^^^^^^^

Logical operators like :keyword:`and`, :keyword:`or`, and :keyword:`not` work
on entire images, rather than individual pixels.

An empty image (all pixels zero) is treated as false. All other images are
treated as true.

Note that :keyword:`and` and :keyword:`or` return the last evaluated operand,
while not always returns a boolean value.

Built-in Functions
^^^^^^^^^^^^^^^^^^

These functions are applied to each individual pixel.

.. py:currentmodule:: None

.. py:function:: abs(image)

    Absolute value.

.. py:function:: convert(image, mode)

    Convert image to the given mode. The mode must be given as a string
    constant.

.. py:function:: float(image)

    Convert image to 32-bit floating point. This is equivalent to
    convert(image, “F”).

.. py:function:: int(image)

    Convert image to 32-bit integer. This is equivalent to convert(image, “I”).

    Note that 1-bit and 8-bit images are automatically converted to 32-bit
    integers if necessary to get a correct result.

.. py:function:: max(image1, image2)

    Maximum value.

.. py:function:: min(image1, image2)

    Minimum value.
