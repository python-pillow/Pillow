.. py:module:: PIL.ImageColor
.. py:currentmodule:: PIL.ImageColor

:py:mod:`~PIL.ImageColor` Module
================================

The :py:mod:`~PIL.ImageColor` module contains color tables and converters from
CSS3-style color specifiers to RGB tuples. This module is used by
:py:meth:`PIL.Image.new` and the :py:mod:`~PIL.ImageDraw` module, among
others.

.. _color-names:

Color Names
-----------

The ImageColor module supports the following string formats:

* Hexadecimal color specifiers, given as ``#rgb``, ``#rgba``, ``#rrggbb`` or
  ``#rrggbbaa``, where ``r`` is red, ``g`` is green, ``b`` is blue and ``a`` is
  alpha (also called 'opacity'). For example, ``#ff0000`` specifies pure red,
  and ``#ff0000cc`` specifies red with 80% opacity (``cc`` is 204 in decimal
  form, and 204 / 255 = 0.8).

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

* Hue-Saturation-Value (HSV) functions, given as ``hsv(hue, saturation%,
  value%)`` where hue and saturation are the same as HSL, and value is between
  0% and 100% (black=0%, normal=100%). For example, ``hsv(0,100%,100%)`` is
  pure red. This format is also known as Hue-Saturation-Brightness (HSB), and
  can be given as ``hsb(hue, saturation%, brightness%)``, where each of the
  values are used as they are in HSV.

* Common HTML color names. The :py:mod:`~PIL.ImageColor` module provides some
  140 standard color names, based on the colors supported by the X Window
  system and most web browsers. color names are case insensitive. For example,
  ``red`` and ``Red`` both specify pure red.

Functions
---------

.. py:method:: getrgb(color)

    Convert a color string to an RGB tuple. If the string cannot be parsed,
    this function raises a :py:exc:`ValueError` exception.

    .. versionadded:: 1.1.4

.. py:method:: getcolor(color, mode)

    Same as :py:func:`~PIL.ImageColor.getrgb`, but converts the RGB value to a
    greyscale value if the mode is not color or a palette image. If the string
    cannot be parsed, this function raises a :py:exc:`ValueError` exception.

    .. versionadded:: 1.1.4
