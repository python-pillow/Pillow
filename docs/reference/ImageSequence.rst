.. py:module:: PIL.ImageSequence
.. py:currentmodule:: PIL.ImageSequence

:py:mod:`~PIL.ImageSequence` Module
===================================

The :py:mod:`~PIL.ImageSequence` module contains a wrapper class that lets you
iterate over the frames of an image sequence.

Extracting frames from an animation
-----------------------------------

.. code-block:: python

    from PIL import Image, ImageSequence

    with Image.open("animation.fli") as im:
        index = 1
        for frame in ImageSequence.Iterator(im):
            frame.save(f"frame{index}.png")
            index += 1

The :py:class:`~PIL.ImageSequence.Iterator` class
-------------------------------------------------

.. autoclass:: PIL.ImageSequence.Iterator
    :members:
