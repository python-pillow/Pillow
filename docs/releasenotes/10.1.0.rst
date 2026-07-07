10.1.0
------

API changes
===========

Setting image mode
^^^^^^^^^^^^^^^^^^

If you attempt to set the mode of an image directly, e.g.
``im.mode = "RGBA"``, you will now receive an :py:exc:`AttributeError`. This is
not about removing existing functionality, but instead about raising an
explicit error to prevent later consequences. The ``convert`` method is the
correct way to change an image's mode.

Accept a list in getpixel()
^^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:meth:`~PIL.Image.Image.getpixel` now accepts a list of coordinates, as well
as a tuple. ::

    from PIL import Image
    im = Image.new("RGB", (1, 1))
    im.getpixel((0, 0))
    im.getpixel([0, 0])

BoxBlur and GaussianBlur allow for different x and y radii
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:class:`~PIL.ImageFilter.BoxBlur` and
:py:class:`~PIL.ImageFilter.GaussianBlur` now allow a sequence of x and y radii
to be specified, rather than a single number for both dimensions. ::

    from PIL import ImageFilter
    ImageFilter.BoxBlur((2, 5))
    ImageFilter.GaussianBlur((2, 5))

API additions
=============

EpsImagePlugin.gs_binary
^^^^^^^^^^^^^^^^^^^^^^^^

``EpsImagePlugin.gs_windows_binary`` stores the name of the Ghostscript
executable on Windows. ``EpsImagePlugin.gs_binary`` has now been added for all
platforms, and can be used to customise the name of the executable, or disable
use entirely through ``EpsImagePlugin.gs_binary = False``.

has_transparency_data
^^^^^^^^^^^^^^^^^^^^^

Images now have :py:attr:`~PIL.Image.Image.has_transparency_data` to indicate
whether the image has transparency data, whether in the form of an alpha
channel, a palette with an alpha channel, or a "transparency" key in the
:py:attr:`~PIL.Image.Image.info` dictionary.

Even if this attribute is true, the image might still appear solid, if all of
the values shown within are opaque.

ImageOps.cover
^^^^^^^^^^^^^^

Returns a resized version of the image, so that the requested size is covered,
while maintaining the original aspect ratio.

See :ref:`relative-resize` for a comparison between this and similar ``ImageOps``
methods.

size and font_size arguments when using default font
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pillow has had a "better than nothing" default font, which can only be drawn at
one font size. Now, if FreeType support is available, a version of
`Aileron Regular <https://dotcolon.net/fonts/aileron>`_ is loaded, which can be
drawn at chosen font sizes.

The following ``size`` and ``font_size`` arguments can now be used to specify a
font size for this new builtin font::

    ImageFont.load_default(size=24)
    draw.text((0, 0), "test", font_size=24)
    draw.textlength((0, 0), "test", font_size=24)
    draw.textbbox((0, 0), "test", font_size=24)
    draw.multiline_text((0, 0), "test", font_size=24)
    draw.multiline_textbbox((0, 0), "test", font_size=24)

Other changes
=============

Python 3.12
^^^^^^^^^^^

Pillow 10.0.0 had wheels built against Python 3.12 beta, available as a preview to help
others prepare for 3.12, and to ensure Pillow could be used immediately at the release
of 3.12.0 final (2023-10-02, :pep:`693`).

Pillow 10.1.0 now officially supports Python 3.12.

Added support for DDS BC5U and 8-bit color indexed images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Support has been added to read BC5U DDS files as RGB images, and
PALETTEINDEXED8 DDS files as P mode images.

Support reading signed 8-bit YCbCr TIFF images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TIFF images with unsigned integer data, 8 bits per sample and a photometric
interpretation of YCbCr can now be read.
