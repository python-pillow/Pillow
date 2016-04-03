.. py:module:: PIL.ImageDraw
.. py:currentmodule:: PIL.ImageDraw

:py:mod:`ImageDraw` Module
==========================

The :py:mod:`ImageDraw` module provide simple 2D graphics for
:py:class:`~PIL.Image.Image` objects.  You can use this module to create new
images, annotate or retouch existing images, and to generate graphics on the
fly for web use.

For a more advanced drawing library for PIL, see the `aggdraw module`_.

.. _aggdraw module: http://effbot.org/zone/aggdraw-index.htm

Example: Draw a gray cross over an image
----------------------------------------

.. code-block:: python

    from PIL import Image, ImageDraw

    im = Image.open("lena.pgm")

    draw = ImageDraw.Draw(im)
    draw.line((0, 0) + im.size, fill=128)
    draw.line((0, im.size[1], im.size[0], 0), fill=128)
    del draw

    # write to stdout
    im.save(sys.stdout, "PNG")


Concepts
--------

Coordinates
^^^^^^^^^^^

The graphics interface uses the same coordinate system as PIL itself, with (0,
0) in the upper left corner.

Colors
^^^^^^

To specify colors, you can use numbers or tuples just as you would use with
:py:meth:`PIL.Image.Image.new` or :py:meth:`PIL.Image.Image.putpixel`. For “1”,
“L”, and “I” images, use integers. For “RGB” images, use a 3-tuple containing
integer values. For “F” images, use integer or floating point values.

For palette images (mode “P”), use integers as color indexes. In 1.1.4 and
later, you can also use RGB 3-tuples or color names (see below). The drawing
layer will automatically assign color indexes, as long as you don’t draw with
more than 256 colors.

Color Names
^^^^^^^^^^^

See :ref:`color-names` for the color names supported by Pillow.

Fonts
^^^^^

PIL can use bitmap fonts or OpenType/TrueType fonts.

Bitmap fonts are stored in PIL’s own format, where each font typically consists
of a two files, one named .pil and the other usually named .pbm. The former
contains font metrics, the latter raster data.

To load a bitmap font, use the load functions in the :py:mod:`~PIL.ImageFont`
module.

To load a OpenType/TrueType font, use the truetype function in the
:py:mod:`~PIL.ImageFont` module. Note that this function depends on third-party
libraries, and may not available in all PIL builds.

Example: Draw Partial Opacity Text
----------------------------------

.. code-block:: python

    from PIL import Image, ImageDraw, ImageFont
    # get an image
    base = Image.open('Pillow/Tests/images/lena.png').convert('RGBA')

    # make a blank image for the text, initialized to transparent text color
    txt = Image.new('RGBA', base.size, (255,255,255,0))

    # get a font
    fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 40)
    # get a drawing context
    d = ImageDraw.Draw(txt)

    # draw text, half opacity
    d.text((10,10), "Hello", font=fnt, fill=(255,255,255,128))
    # draw text, full opacity
    d.text((10,60), "World", font=fnt, fill=(255,255,255,255))

    out = Image.alpha_composite(base, txt)

    out.show()



Functions
---------

.. py:class:: PIL.ImageDraw.Draw(im, mode=None)

    Creates an object that can be used to draw in the given image.

    Note that the image will be modified in place.

    :param im: The image to draw in.
    :param mode: Optional mode to use for color values.  For RGB
        images, this argument can be RGB or RGBA (to blend the
        drawing into the image).  For all other modes, this argument
        must be the same as the image mode.  If omitted, the mode
        defaults to the mode of the image.

Methods
-------

.. py:method:: PIL.ImageDraw.Draw.arc(xy, start, end, fill=None)

    Draws an arc (a portion of a circle outline) between the start and end
    angles, inside the given bounding box.

    :param xy: Four points to define the bounding box. Sequence of
            ``[(x0, y0), (x1, y1)]`` or ``[x0, y0, x1, y1]``.
    :param start: Starting angle, in degrees. Angles are measured from
            3 o'clock, increasing clockwise.
    :param end: Ending angle, in degrees.
    :param fill: Color to use for the arc.

.. py:method:: PIL.ImageDraw.Draw.bitmap(xy, bitmap, fill=None)

    Draws a bitmap (mask) at the given position, using the current fill color
    for the non-zero portions. The bitmap should be a valid transparency mask
    (mode “1”) or matte (mode “L” or “RGBA”).

    This is equivalent to doing ``image.paste(xy, color, bitmap)``.

    To paste pixel data into an image, use the
    :py:meth:`~PIL.Image.Image.paste` method on the image itself.

.. py:method:: PIL.ImageDraw.Draw.chord(xy, start, end, fill=None, outline=None)

    Same as :py:meth:`~PIL.ImageDraw.Draw.arc`, but connects the end points
    with a straight line.

    :param xy: Four points to define the bounding box. Sequence of
            ``[(x0, y0), (x1, y1)]`` or ``[x0, y0, x1, y1]``.
    :param outline: Color to use for the outline.
    :param fill: Color to use for the fill.

.. py:method:: PIL.ImageDraw.Draw.ellipse(xy, fill=None, outline=None)

    Draws an ellipse inside the given bounding box.

    :param xy: Four points to define the bounding box. Sequence of either
            ``[(x0, y0), (x1, y1)]`` or ``[x0, y0, x1, y1]``.
    :param outline: Color to use for the outline.
    :param fill: Color to use for the fill.

.. py:method:: PIL.ImageDraw.Draw.line(xy, fill=None, width=0)

    Draws a line between the coordinates in the **xy** list.

    :param xy: Sequence of either 2-tuples like ``[(x, y), (x, y), ...]`` or
               numeric values like ``[x, y, x, y, ...]``.
    :param fill: Color to use for the line.
    :param width: The line width, in pixels. Note that line
        joins are not handled well, so wide polylines will not look good.

        .. versionadded:: 1.1.5

        .. note:: This option was broken until version 1.1.6.

.. py:method:: PIL.ImageDraw.Draw.pieslice(xy, start, end, fill=None, outline=None)

    Same as arc, but also draws straight lines between the end points and the
    center of the bounding box.

    :param xy: Four points to define the bounding box. Sequence of
            ``[(x0, y0), (x1, y1)]`` or ``[x0, y0, x1, y1]``.
    :param start: Starting angle, in degrees. Angles are measured from
            3 o'clock, increasing clockwise.
    :param end: Ending angle, in degrees.
    :param fill: Color to use for the fill.
    :param outline: Color to use for the outline.

.. py:method:: PIL.ImageDraw.Draw.point(xy, fill=None)

    Draws points (individual pixels) at the given coordinates.

    :param xy: Sequence of either 2-tuples like ``[(x, y), (x, y), ...]`` or
               numeric values like ``[x, y, x, y, ...]``.
    :param fill: Color to use for the point.

.. py:method:: PIL.ImageDraw.Draw.polygon(xy, fill=None, outline=None)

    Draws a polygon.

    The polygon outline consists of straight lines between the given
    coordinates, plus a straight line between the last and the first
    coordinate.

    :param xy: Sequence of either 2-tuples like ``[(x, y), (x, y), ...]`` or
               numeric values like ``[x, y, x, y, ...]``.
    :param outline: Color to use for the outline.
    :param fill: Color to use for the fill.

.. py:method:: PIL.ImageDraw.Draw.rectangle(xy, fill=None, outline=None)

    Draws a rectangle.

    :param xy: Four points to define the bounding box. Sequence of either
            ``[(x0, y0), (x1, y1)]`` or ``[x0, y0, x1, y1]``. The second point
            is just outside the drawn rectangle.
    :param outline: Color to use for the outline.
    :param fill: Color to use for the fill.

.. py:method:: PIL.ImageDraw.Draw.shape(shape, fill=None, outline=None)

    .. warning:: This method is experimental.

    Draw a shape.

.. py:method:: PIL.ImageDraw.Draw.text(xy, text, fill=None, font=None, anchor=None, spacing=0, align="left")

    Draws the string at the given position.

    :param xy: Top left corner of the text.
    :param text: Text to be drawn. If it contains any newline characters,
                 the text is passed on to multiline_text()
    :param fill: Color to use for the text.
    :param font: An :py:class:`~PIL.ImageFont.ImageFont` instance.
    :param spacing: If the text is passed on to multiline_text(),
                    the number of pixels between lines.
    :param align: If the text is passed on to multiline_text(),
                  "left", "center" or "right".


.. py:method:: PIL.ImageDraw.Draw.multiline_text(xy, text, fill=None, font=None, anchor=None, spacing=0, align="left")

    Draws the string at the given position.

    :param xy: Top left corner of the text.
    :param text: Text to be drawn.
    :param fill: Color to use for the text.
    :param font: An :py:class:`~PIL.ImageFont.ImageFont` instance.
    :param spacing: The number of pixels between lines.
    :param align: "left", "center" or "right".

.. py:method:: PIL.ImageDraw.Draw.textsize(text, font=None, spacing=0)

    Return the size of the given string, in pixels.

    :param text: Text to be measured. If it contains any newline characters,
                 the text is passed on to multiline_textsize()
    :param font: An :py:class:`~PIL.ImageFont.ImageFont` instance.
    :param spacing: If the text is passed on to multiline_textsize(),
                    the number of pixels between lines.

.. py:method:: PIL.ImageDraw.Draw.multiline_textsize(text, font=None, spacing=0)

    Return the size of the given string, in pixels.

    :param text: Text to be measured.
    :param font: An :py:class:`~PIL.ImageFont.ImageFont` instance.
    :param spacing: The number of pixels between lines.

Legacy API
----------

The :py:class:`~PIL.ImageDraw.Draw` class contains a constructor and a number
of methods which are provided for backwards compatibility only. For this to
work properly, you should either use options on the drawing primitives, or
these methods. Do not mix the old and new calling conventions.


.. py:function:: PIL.ImageDraw.ImageDraw(image)

    :rtype: :py:class:`~PIL.ImageDraw.Draw`

.. py:method:: PIL.ImageDraw.Draw.setfont(font)

    .. deprecated:: 1.1.5

    Sets the default font to use for the text method.

    :param font: An :py:class:`~PIL.ImageFont.ImageFont` instance.
