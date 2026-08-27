.. py:module:: PIL.ImageMath
.. py:currentmodule:: PIL.ImageMath

:py:mod:`~PIL.ImageMath` module
===============================

The :py:mod:`~PIL.ImageMath` module can be used to evaluate “image expressions”, that
can take a number of images and generate a result.

:py:mod:`~PIL.ImageMath` only supports single-layer images. To process multi-band
images, use the :py:meth:`~PIL.Image.Image.split` method or :py:func:`~PIL.Image.merge`
function.

Example: Using the :py:mod:`~PIL.ImageMath` module
--------------------------------------------------

::

    from PIL import Image, ImageMath

    with Image.open("image1.jpg") as im1:
        with Image.open("image2.jpg") as im2:
            out = ImageMath.lambda_eval(
              lambda args: args["convert"](args["min"](args["a"], args["b"]), 'L'),
              a=im1,
              b=im2
            )
            out = ImageMath.unsafe_eval(
              "convert(min(a, b), 'L')",
              a=im1,
              b=im2
            )

.. py:function:: lambda_eval(expression, options, **kw)

    Returns the result of an image function.

    :param expression: A function that receives a dictionary.
    :param options: Values to add to the function's dictionary. Note that the names
                    must be valid Python identifiers. Deprecated.
                    You can instead use one or more keyword arguments, as
                    shown in the above example.
    :param \**kw: Values to add to the function's dictionary, mapping image names to
                 Image instances.
    :return: An image, an integer value, a floating point value,
             or a pixel tuple, depending on the expression.

.. py:function:: unsafe_eval(expression, options, **kw)

    Evaluates an image expression.

    .. danger::
        This uses Python's ``eval()`` function to process the expression string,
        and carries the security risks of doing so. It is not
        recommended to process expressions without considering this.
        :py:meth:`lambda_eval` is a more secure alternative.

    :py:mod:`~PIL.ImageMath` only supports single-layer images. To process multi-band
    images, use the :py:meth:`~PIL.Image.Image.split` method or
    :py:func:`~PIL.Image.merge` function.

    :param expression: A string which uses the standard Python expression
                       syntax. In addition to the standard operators, you can
                       also use the functions described below.
    :param options: Values to add to the evaluation context. Note that the names must
                    be valid Python identifiers. Deprecated.
                    You can instead use one or more keyword arguments, as
                    shown in the above example.
    :param \**kw: Values to add to the evaluation context, mapping image names to Image
                 instances.
    :return: An image, an integer value, a floating point value,
             or a pixel tuple, depending on the expression.

Expression syntax
-----------------

* :py:meth:`lambda_eval` expressions are functions that receive a dictionary
  containing images and operators.

* :py:meth:`unsafe_eval` expressions are standard Python expressions,
  but they’re evaluated in a non-standard environment.

.. danger::
  :py:meth:`unsafe_eval` uses Python's ``eval()`` function to process the
  expression string, and carries the security risks of doing so.
  It is not recommended to process expressions without considering this.
  :py:meth:`lambda_eval` is a more secure alternative.

Standard operators
^^^^^^^^^^^^^^^^^^

You can use standard arithmetical operators for addition (+), subtraction (-),
multiplication (*), and division (/).

The module also supports unary minus (-), modulo (%), and power (**) operators.

Note that all operations are done with 32-bit integers or 32-bit floating
point values, as necessary. For example, if you add two 8-bit images, the
result will be a 32-bit integer image. If you add a floating point constant to
an 8-bit image, the result will be a 32-bit floating point image.

You can force conversion using the ``convert()``, ``float()``, and ``int()``
functions described below.

Bitwise operators
^^^^^^^^^^^^^^^^^

The module also provides operations that operate on individual bits. This
includes and (&), or (|), and exclusive or (^). You can also invert (~) all
pixel bits.

Note that the operands are converted to 32-bit signed integers before the
bitwise operation is applied. This means that you’ll get negative values if
you invert an ordinary grayscale image. You can use the and (&) operator to
mask off unwanted bits.

Bitwise operators don’t work on floating point images.

Logical operators
^^^^^^^^^^^^^^^^^

Logical operators like ``and``, ``or``, and ``not`` work
on entire images, rather than individual pixels.

An empty image (all pixels zero) is treated as false. All other images are
treated as true.

Note that ``and`` and ``or`` return the last evaluated operand,
while not always returns a boolean value.

Built-in functions
^^^^^^^^^^^^^^^^^^

These functions are applied to each individual pixel.

.. py:currentmodule:: None

.. py:function:: abs(image)
    :noindex:

    Absolute value.

.. py:function:: convert(image, mode)
    :noindex:

    Convert image to the given mode. The mode must be given as a string
    constant.

.. py:function:: float(image)
    :noindex:

    Convert image to 32-bit floating point. This is equivalent to
    convert(image, “F”).

.. py:function:: int(image)
    :noindex:

    Convert image to 32-bit integer. This is equivalent to convert(image, “I”).

    Note that 1-bit and 8-bit images are automatically converted to 32-bit
    integers if necessary to get a correct result.

.. py:function:: max(image1, image2)
    :noindex:

    Maximum value.

.. py:function:: min(image1, image2)
    :noindex:

    Minimum value.
