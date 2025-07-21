.. py:module:: PIL.ImageText
.. py:currentmodule:: PIL.ImageText

:py:mod:`~PIL.ImageText` module
===============================

The :py:mod:`~PIL.ImageText` module defines a class with the same name. Instances of
this class provide a way to use fonts with text strings or bytes. The result is a
simple API to apply styling to pieces of text and measure them.

Example
-------

::

    from PIL import Image, ImageDraw, ImageFont, ImageText
    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 24)

    text = ImageText.ImageText("Hello world", font)
    text.embed_color()
    text.stroke(2, "#0f0")

    print(text.get_length())  # 154.0
    print(text.get_bbox())  # (-2, 3, 156, 22)

Methods
-------

.. autoclass:: PIL.ImageText.ImageText
    :members:
