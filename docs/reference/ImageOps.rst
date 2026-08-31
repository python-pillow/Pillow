.. py:module:: PIL.ImageOps
.. py:currentmodule:: PIL.ImageOps

:py:mod:`~PIL.ImageOps` module
==============================

The :py:mod:`~PIL.ImageOps` module contains a number of ‘ready-made’ image
processing operations. This module is somewhat experimental, and most operators
only work on L and RGB images.

.. versionadded:: 1.1.3

.. autofunction:: autocontrast
.. autofunction:: colorize
.. autofunction:: crop
.. autofunction:: scale
.. autoclass:: SupportsGetMesh
    :show-inheritance:
.. autofunction:: deform
.. autofunction:: equalize
.. autofunction:: expand
.. autofunction:: flip
.. autofunction:: grayscale
.. autofunction:: invert
.. autofunction:: mirror
.. autofunction:: posterize
.. autofunction:: solarize
.. autofunction:: exif_transpose

.. _relative-resize:

Resize relative to a given size
-------------------------------

::

    from PIL import Image, ImageOps
    size = (100, 150)
    with Image.open("Tests/images/hopper.webp") as im:
        ImageOps.contain(im, size).save("imageops_contain.webp")
        ImageOps.cover(im, size).save("imageops_cover.webp")
        ImageOps.fit(im, size).save("imageops_fit.webp")
        ImageOps.pad(im, size, color="#f00").save("imageops_pad.webp")

        # thumbnail() can also be used,
        # but will modify the image object in place
        im.thumbnail(size)
        im.save("image_thumbnail.webp")

+----------------+--------------------------------------------+---------------------------------------------+-------------------------------------------+-----------------------------------------+-----------------------------------------+
|                | :py:meth:`~PIL.Image.Image.thumbnail`      | :py:meth:`~PIL.ImageOps.contain`            | :py:meth:`~PIL.ImageOps.cover`            | :py:meth:`~PIL.ImageOps.fit`            | :py:meth:`~PIL.ImageOps.pad`            |
+================+============================================+=============================================+===========================================+=========================================+=========================================+
|Given size      | ``(100, 150)``                             | ``(100, 150)``                              | ``(100, 150)``                            | ``(100, 150)``                          | ``(100, 150)``                          |
+----------------+--------------------------------------------+---------------------------------------------+-------------------------------------------+-----------------------------------------+-----------------------------------------+
|Resulting image | .. image:: ../example/image_thumbnail.webp | .. image:: ../example/imageops_contain.webp | .. image:: ../example/imageops_cover.webp | .. image:: ../example/imageops_fit.webp | .. image:: ../example/imageops_pad.webp |
+----------------+--------------------------------------------+---------------------------------------------+-------------------------------------------+-----------------------------------------+-----------------------------------------+
|Resulting size  | ``100×100``                                | ``100×100``                                 | ``150×150``                               | ``100×150``                             | ``100×150``                             |
+----------------+--------------------------------------------+---------------------------------------------+-------------------------------------------+-----------------------------------------+-----------------------------------------+

.. autofunction:: contain
.. autofunction:: cover
.. autofunction:: fit
.. autofunction:: pad
