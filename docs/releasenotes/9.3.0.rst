9.3.0
-----

Security
========

Initialize libtiff buffer when saving
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When saving a TIFF image to a file object using libtiff, the buffer was not
initialized. This behaviour introduced in Pillow 2.0.0, and has now been fixed.

Decode JPEG compressed BLP1 data in original mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Within the BLP image format, BLP1 data may use JPEG compression. Instead of
telling the JPEG library that this data is in BGRX mode, Pillow will now
decode the data in its natural CMYK mode, then convert it to RGB and rearrange
the channels afterwards. Trying to load the data in an incorrect mode could
result in a segmentation fault. This issue was introduced in Pillow 9.1.0.

Limit SAMPLESPERPIXEL to avoid runtime DOS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A large value in the ``SAMPLESPERPIXEL`` tag could lead to a memory and runtime DOS in
``TiffImagePlugin.py`` when setting up the context for image decoding.
This was introduced in Pillow 9.2.0, found with `OSS-Fuzz`_ and fixed by limiting
``SAMPLESPERPIXEL`` to the number of planes that we can decode.


API additions
=============

Allow default ImageDraw font to be set
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Rather than specifying a font when calling text-related ImageDraw methods, or
setting a font on each ImageDraw instance, the default font can now be set for
all future ImageDraw operations::

    from PIL import ImageDraw, ImageFont
    ImageDraw.ImageDraw.font = ImageFont.truetype("Tests/fonts/FreeMono.ttf")

Saving multiple MPO frames
^^^^^^^^^^^^^^^^^^^^^^^^^^

Multiple MPO frames can now be saved. Using the ``save_all`` argument, all of
an image's frames will be saved to file::

    from PIL import Image
    im = Image.open("frozenpond.mpo")
    im.save(out, save_all=True)

Additional images can also be appended when saving, by combining the
``save_all`` argument with the ``append_images`` argument::

    im.save(out, save_all=True, append_images=[im1, im2, ...])

Added ExifTags enums
^^^^^^^^^^^^^^^^^^^^

The data from :py:data:`~PIL.ExifTags.TAGS` and
:py:data:`~PIL.ExifTags.GPSTAGS` is now also exposed as
:py:class:`enum.IntEnum` classes: :py:data:`~PIL.ExifTags.Base` and
:py:data:`~PIL.ExifTags.GPS`.


Other changes
=============

Python 3.11 wheels
^^^^^^^^^^^^^^^^^^

Pillow 9.2.0 had wheels built against Python 3.11 beta, available as a preview to help
others prepare for 3.11, and ensure Pillow can be used immediately on release day of
3.11.0 final (2022-10-24, :pep:`664`).

Pillow 9.3.0 now officially includes binary wheels for Python 3.11 final.

Windows wheels
^^^^^^^^^^^^^^

This release contains wheels for Windows built using GitHub Actions.

Previously they were built by `Christoph Gohlke <https://www.cgohlke.com/>`_.

A huge thanks to Christoph for building Windows binaries for us for around a decade,
plus testing, and fixing over a hundred bug fixes along the way, in addition to building
and hosting unofficial Windows binaries for hundreds of Python projects!

Added DDS ATI1, ATI2 and BC6H reading
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Support has been added to read the ATI1, ATI2 and BC6H formats of DDS images.

Release GIL when converting images using matrix operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Python's Global Interpreter Lock is now released when converting images using matrix
operations.

Show all frames with ImageShow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When calling :py:meth:`~PIL.Image.Image.show` or using
:py:mod:`~PIL.ImageShow`, all frames will now be shown.

.. _OSS-Fuzz: https://github.com/google/oss-fuzz
