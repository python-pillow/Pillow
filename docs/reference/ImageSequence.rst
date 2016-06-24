.. py:module:: PIL.ImageSequence
.. py:currentmodule:: PIL.ImageSequence

:py:mod:`ImageSequence` Module
==============================

The :py:mod:`ImageSequence` module contains a wrapper class that lets you
iterate over the frames of an image sequence.

Extracting frames from an animation
-----------------------------------

.. code-block:: python

    from PIL import Image, ImageSequence

    im = Image.open("animation.fli")

    index = 1
    for frame in ImageSequence.Iterator(im):
        frame.save("frame%d.png" % index)
        index += 1

The :py:class:`~PIL.ImageSequence.Iterator` class
-------------------------------------------------

.. autoclass:: PIL.ImageSequence.Iterator
