.. py:module:: PIL.ImageSequence
.. py:currentmodule:: PIL.ImageSequence

:py:mod:`~PIL.ImageSequence` module
===================================

The :py:mod:`~PIL.ImageSequence` module contains a wrapper class that lets you
iterate over the frames of an image sequence.

Extracting frames from an animation
-----------------------------------

::

    from PIL import Image, ImageSequence

    with Image.open("animation.fli") as im:
        index = 1
        for frame in ImageSequence.Iterator(im):
            frame.save(f"frame{index}.png")
            index += 1

``Iterator`` returns the same image object for each frame, updating it as you
iterate. To keep a frame for later use, call :py:meth:`~PIL.Image.Image.copy`
before advancing the iterator. Converting the iterator to a list does not copy
the frames.

To get a list of independent images, use :py:func:`~PIL.ImageSequence.all_frames`::

    from PIL import Image, ImageSequence

    with Image.open("animation.fli") as im:
        frames = ImageSequence.all_frames(im)

The :py:class:`~PIL.ImageSequence.Iterator` class
-------------------------------------------------

.. autoclass:: PIL.ImageSequence.Iterator
    :members:

Functions
---------

.. autofunction:: PIL.ImageSequence.all_frames
