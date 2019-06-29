.. py:module:: PIL.ImageFilter
.. py:currentmodule:: PIL.ImageFilter

:py:mod:`ImageFilter` Module
============================

The :py:mod:`ImageFilter` module contains definitions for a pre-defined set of
filters, which can be be used with the :py:meth:`Image.filter()
<PIL.Image.Image.filter>` method.

Example: Filter an image
------------------------

.. code-block:: python

    from PIL import ImageFilter

    im1 = im.filter(ImageFilter.BLUR)

    im2 = im.filter(ImageFilter.MinFilter(3))
    im3 = im.filter(ImageFilter.MinFilter)  # same as MinFilter(3)

Filters
-------

The current version of the library provides the following set of predefined
image enhancement filters:

* **BLUR**
* **CONTOUR**
* **DETAIL**
* **EDGE_ENHANCE**
* **EDGE_ENHANCE_MORE**
* **EMBOSS**
* **FIND_EDGES**
* **SHARPEN**
* **SMOOTH**
* **SMOOTH_MORE**

.. autoclass:: PIL.ImageFilter.Color3DLUT
    :members:

.. autoclass:: PIL.ImageFilter.BoxBlur
    :members:

.. autoclass:: PIL.ImageFilter.GaussianBlur
    :members:

.. autoclass:: PIL.ImageFilter.UnsharpMask
    :members:

.. autoclass:: PIL.ImageFilter.Kernel
    :members:

.. autoclass:: PIL.ImageFilter.RankFilter
    :members:

.. autoclass:: PIL.ImageFilter.MedianFilter
    :members:

.. autoclass:: PIL.ImageFilter.MinFilter
    :members:

.. autoclass:: PIL.ImageFilter.MaxFilter
    :members:

.. autoclass:: PIL.ImageFilter.ModeFilter
    :members:
