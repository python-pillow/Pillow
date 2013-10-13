.. py:module:: PIL.ImageColor
.. py:currentmodule:: PIL.ImageColor

:py:mod:`ImageColor` Module
===========================

The :py:mod:`ImageColor` module contains color tables and converters from
CSS3-style color specifiers to RGB tuples. This module is used by
:py:meth:`PIL.Image.Image.new` and the :py:mod:`~PIL.ImageDraw` module, among
others.

.. _color-names:

Color Names
-----------

The ImageColor module supports the following string formats:

* Hexadecimal color specifiers, given as ``#rgb`` or ``#rrggbb``. For example,
  ``#ff0000`` specifies pure red.

* RGB functions, given as ``rgb(red, green, blue)`` where the color values are
  integers in the range 0 to 255. Alternatively, the color values can be given
  as three percentages (0% to 100%). For example, ``rgb(255,0,0)`` and
  ``rgb(100%,0%,0%)`` both specify pure red.

* Hue-Saturation-Lightness (HSL) functions, given as ``hsl(hue, saturation%,
  lightness%)`` where hue is the color given as an angle between 0 and 360
  (red=0, green=120, blue=240), saturation is a value between 0% and 100%
  (gray=0%, full color=100%), and lightness is a value between 0% and 100%
  (black=0%, normal=50%, white=100%). For example, ``hsl(0,100%,50%)`` is pure
  red.

* Common HTML color names. The :py:mod:`~PIL.ImageColor` module provides some
  140 standard color names, based on the colors supported by the X Window
  system and most web browsers. color names are case insensitive. For example,
  ``red`` and ``Red`` both specify pure red.

Functions
---------

.. autofunction:: getrgb
.. autofunction:: getcolor
