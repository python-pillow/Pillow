.. py:module:: PIL.ImageFont
.. py:currentmodule:: PIL.ImageFont

:py:mod:`ImageFont` Module
==========================

The :py:mod:`ImageFont` module defines a class with the same name. Instances of
this class store bitmap fonts, and are used with the
:py:meth:`PIL.ImageDraw.Draw.text` method.

PIL uses its own font file format to store bitmap fonts. You can use the
:command`pilfont` utility to convert BDF and PCF font descriptors (X window
font formats) to this format.

Starting with version 1.1.4, PIL can be configured to support TrueType and
OpenType fonts (as well as other font formats supported by the FreeType
library). For earlier versions, TrueType support is only available as part of
the imToolkit package

Example
-------

.. code-block:: python

    from PIL import ImageFont, ImageDraw

    draw = ImageDraw.Draw(image)

    # use a bitmap font
    font = ImageFont.load("arial.pil")

    draw.text((10, 10), "hello", font=font)

    # use a truetype font
    font = ImageFont.truetype("arial.ttf", 15)

    draw.text((10, 25), "world", font=font)

Functions
---------

.. autofunction:: PIL.ImageFont.load
.. autofunction:: PIL.ImageFont.load_path
.. autofunction:: PIL.ImageFont.truetype
.. autofunction:: PIL.ImageFont.load_default

Methods
-------

.. py:method:: PIL.ImageFont.ImageFont.getsize(text)

    :return: (width, height)

.. py:method:: PIL.ImageFont.ImageFont.getmask(text, mode='')

    Create a bitmap for the text.

    If the font uses antialiasing, the bitmap should have mode “L” and use a
    maximum value of 255. Otherwise, it should have mode “1”.

    :param text: Text to render.
    :param mode: Used by some graphics drivers to indicate what mode the
                 driver prefers; if empty, the renderer may return either
                 mode. Note that the mode is always a string, to simplify
                 C-level implementations.

                 .. versionadded:: 1.1.5
    :return: An internal PIL storage memory instance as defined by the
             :py:mod:`PIL.Image.core` interface module.
