.. py:module:: PIL.ImageChops
.. py:currentmodule:: PIL.ImageChops

:py:mod:`~PIL.ImageChops` ("Channel Operations") Module
=======================================================

The :py:mod:`~PIL.ImageChops` module contains a number of arithmetical image
operations, called channel operations (“chops”). These can be used for various
purposes, including special effects, image compositions, algorithmic painting,
and more.

For more pre-made operations, see :py:mod:`~PIL.ImageOps`.

At this time, most channel operations are only implemented for 8-bit images
(e.g. “L” and “RGB”).

Functions
---------

Most channel operations take one or two image arguments and returns a new
image. Unless otherwise noted, the result of a channel operation is always
clipped to the range 0 to MAX (which is 255 for all modes supported by the
operations in this module).

.. autofunction:: PIL.ImageChops.add
.. autofunction:: PIL.ImageChops.add_modulo
.. autofunction:: PIL.ImageChops.blend
.. autofunction:: PIL.ImageChops.composite
.. autofunction:: PIL.ImageChops.constant
.. autofunction:: PIL.ImageChops.darker
.. autofunction:: PIL.ImageChops.difference
.. autofunction:: PIL.ImageChops.duplicate
.. autofunction:: PIL.ImageChops.invert
.. autofunction:: PIL.ImageChops.lighter
.. autofunction:: PIL.ImageChops.logical_and
.. autofunction:: PIL.ImageChops.logical_or
.. autofunction:: PIL.ImageChops.logical_xor
.. autofunction:: PIL.ImageChops.multiply
.. autofunction:: PIL.ImageChops.soft_light
.. autofunction:: PIL.ImageChops.hard_light
.. autofunction:: PIL.ImageChops.overlay
.. autofunction:: PIL.ImageChops.offset
.. autofunction:: PIL.ImageChops.screen
.. autofunction:: PIL.ImageChops.subtract
.. autofunction:: PIL.ImageChops.subtract_modulo
