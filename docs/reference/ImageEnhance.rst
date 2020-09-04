.. py:module:: PIL.ImageEnhance
.. py:currentmodule:: PIL.ImageEnhance

:py:mod:`~PIL.ImageEnhance` Module
==================================

The :py:mod:`~PIL.ImageEnhance` module contains a number of classes that can be used
for image enhancement.

Example: Vary the sharpness of an image
---------------------------------------

.. code-block:: python

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

    This class can be used to adjust the colour balance of an image, in
    a manner similar to the controls on a colour TV set. An enhancement
    factor of 0.0 gives a black and white image. A factor of 1.0 gives
    the original image.

.. py:class:: Contrast(image)

    Adjust image contrast.

    This class can be used to control the contrast of an image, similar
    to the contrast control on a TV set. An enhancement factor of 0.0
    gives a solid grey image. A factor of 1.0 gives the original image.

.. py:class:: Brightness(image)

    Adjust image brightness.

    This class can be used to control the brightness of an image.  An
    enhancement factor of 0.0 gives a black image. A factor of 1.0 gives the
    original image.

.. py:class:: Sharpness(image)

    Adjust image sharpness.

    This class can be used to adjust the sharpness of an image. An
    enhancement factor of 0.0 gives a blurred image, a factor of 1.0 gives the
    original image, and a factor of 2.0 gives a sharpened image.
