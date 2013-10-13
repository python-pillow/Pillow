.. py:module:: PIL.ImageEnhance
.. py:currentmodule:: PIL.ImageEnhance

:py:mod:`ImageEnhance` Module
=============================

The :py:mod:`ImageEnhance` module contains a number of classes that can be used
for image enhancement.

Example: Vary the sharpness of an image
---------------------------------------

.. code-block:: python

    from PIL import ImageEnhance

    enhancer = ImageEnhance.Sharpness(image)

    for i in range(8):
        factor = i / 4.0
        enhancer.enhance(factor).show("Sharpness %f" % factor)

Also see the :file:`enhancer.py` demo program in the :file:`Scripts/`
directory.

Classes
-------

All enhancement classes implement a common interface, containing a single
method:

.. autoclass:: PIL.ImageEnhance._Enhance
    :members:

.. autoclass:: PIL.ImageEnhance.Color
.. autoclass:: PIL.ImageEnhance.Contrast
.. autoclass:: PIL.ImageEnhance.Brightness
.. autoclass:: PIL.ImageEnhance.Sharpness
