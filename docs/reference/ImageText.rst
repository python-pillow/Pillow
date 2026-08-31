.. py:module:: PIL.ImageText
.. py:currentmodule:: PIL.ImageText

:py:mod:`~PIL.ImageText` module
===============================

The :py:mod:`~PIL.ImageText` module defines a :py:class:`~PIL.ImageText.Text` class.
Instances of this class provide a way to use fonts with text strings or bytes. The
result is a simple API to apply styling to pieces of text and measure or draw them.

Example
-------

::

    from PIL import Image, ImageDraw, ImageFont, ImageText
    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 24)

    text = ImageText.Text("Hello world", font)
    text.embed_color()
    text.stroke(2, "#0f0")

    print(text.get_length())  # 154.0
    print(text.get_bbox())  # (-2, 3, 156, 22)

    im = Image.new("RGB", text.get_bbox()[2:])
    d = ImageDraw.Draw(im)
    d.text((0, 0), text, "#f00")

Comparison
----------

Without ``ImageText.Text``::

  from PIL import Image, ImageDraw
  im = Image.new(mode, size)
  d = ImageDraw.Draw(im)

  d.textlength(text, font, direction, features, language, embedded_color)
  d.multiline_textbbox(xy, text, font, anchor, spacing, align, direction, features, language, stroke_width, embedded_color)
  d.text(xy, text, fill, font, anchor, spacing, align, direction, features, language, stroke_width, stroke_fill, embedded_color)

With ``ImageText.Text``::

  from PIL import ImageText
  text = ImageText.Text(text, font, mode, spacing, direction, features, language)
  text.embed_color()
  text.stroke(stroke_width, stroke_fill)

  text.get_length()
  text.get_bbox(xy, anchor, align)

  im = Image.new(mode, size)
  d = ImageDraw.Draw(im)
  d.text(xy, text, fill, anchor=anchor, align=align)

Methods
-------

.. autoclass:: PIL.ImageText.Text
    :members:
