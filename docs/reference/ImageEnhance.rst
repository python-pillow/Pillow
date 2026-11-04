.. py:module:: PIL.ImageEnhance
.. py:currentmodule:: PIL.ImageEnhance

:py:mod:`~PIL.ImageEnhance` module
==================================

The :py:mod:`~PIL.ImageEnhance` module contains a number of classes that can be used
for image enhancement.

Image modes
-----------

Enhancement does not automatically convert unsupported :ref:`image modes
<concept-modes>`. For example, enhancing a palette image (``P``) or a 16-bit
grayscale image (``I;16``) can raise ``ValueError: image has wrong mode``.

Convert a palette image to ``RGB`` before enhancement, or to ``RGBA`` to preserve
transparency::

    from PIL import Image, ImageEnhance

    with Image.open("palette.png") as image:
        rgba_image = image.convert("RGBA")
    enhanced = ImageEnhance.Contrast(rgba_image).enhance(1.3)

For a 16-bit grayscale image, converting directly to ``L`` clips values above
255 rather than scaling them to the 8-bit range. If an 8-bit result is suitable,
scale the values before converting. This example maps the full unsigned 16-bit
range, 0 to 65535, to 0 to 255::

    from PIL import Image, ImageEnhance

    with Image.open("grayscale16.tif") as image:
        grayscale = image.convert("I").point(lambda value: value / 256).convert("L")
    enhanced = ImageEnhance.Contrast(grayscale).enhance(1.3)

The conversion to ``I`` allows the same scaling operation for both little-endian
and big-endian 16-bit images. This reduces the image to 256 gray levels and does
not preserve its original precision. It also does not stretch the image's actual
minimum and maximum to fill the output range; data using only part of the 16-bit
range may need a different scaling factor. Enhancement in the original 16-bit
mode is not supported.

Example: Vary the sharpness of an image
---------------------------------------

::

    from PIL import ImageEnhance

    enhancer = ImageEnhance.Sharpness(image)

    for i in range(8):
        factor = i / 4.0
        enhancer.enhance(factor).show(f"Sharpness {factor:f}")

Also see the :file:`enhancer.py` demo program in the :file:`Scripts/`
directory.

Classes
-------

All enhancement classes implement a common interface, containing a single
method:

.. _enhancement-factor:

.. py:class:: _Enhance

    .. py:method:: enhance(factor)

        Returns an enhanced image.

        :param factor: A floating point value controlling the enhancement.
                       Factor 1.0 always returns a copy of the original image,
                       lower factors mean less color (brightness, contrast,
                       etc), and higher values more. There are no restrictions
                       on this value.

.. py:class:: Color(image)

    Adjust image color balance.

    This class can be used to adjust the colour balance of an image, in a
    manner similar to the controls on a colour TV set. An
    :ref:`enhancement factor <enhancement-factor>` of 0.0 gives a black and
    white image. A factor of 1.0 gives the original image.

.. py:class:: Contrast(image)

    Adjust image contrast.

    This class can be used to control the contrast of an image, similar to the
    contrast control on a TV set. An
    :ref:`enhancement factor <enhancement-factor>` of 0.0 gives a solid gray
    image, a factor of 1.0 gives the original image, and greater values
    increase the contrast of the image.

.. py:class:: Brightness(image)

    Adjust image brightness.

    This class can be used to control the brightness of an image. An
    :ref:`enhancement factor <enhancement-factor>` of 0.0 gives a black image,
    a factor of 1.0 gives the original image, and greater values increase the
    brightness of the image.

.. py:class:: Sharpness(image)

    Adjust image sharpness.

    This class can be used to adjust the sharpness of an image. An
    :ref:`enhancement factor <enhancement-factor>` of 0.0 gives a blurred
    image, a factor of 1.0 gives the original image, and a factor of 2.0 gives
    a sharpened image.
