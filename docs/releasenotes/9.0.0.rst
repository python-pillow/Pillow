9.0.0
-----

Fredrik Lundh
=============

This release is dedicated to the memory of Fredrik Lundh, aka Effbot, who died in
November 2021. Fredrik created PIL in 1995 and he was instrumental in the early
success of Python.

`Guido wrote <https://mail.python.org/archives/list/python-dev@python.org/thread/36Q5QBILL3QIFIA3KHNGFBNJQKXKN7SD/>`_:

    Fredrik was an early Python contributor (e.g. Elementtree and the 're'
    module) and his enthusiasm for the language and community were inspiring
    for all who encountered him or his work. He spent countless hours on
    comp.lang.python answering questions from newbies and advanced users alike.

    He also co-founded an early Python startup, Secret Labs AB, which among
    other software released an IDE named PythonWorks. Fredrik also created the
    Python Imaging Library (PIL) which is still THE way to interact with images
    in Python, now most often through its Pillow fork. His effbot.org site was
    a valuable resource for generations of Python users, especially its Tkinter
    documentation.

Thank you, Fredrik.

Security
========

Ensure JpegImagePlugin stops at the end of a truncated file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``JpegImagePlugin`` may append an EOF marker to the end of a truncated file, so that
the last segment of the data will still be processed by the decoder.

If the EOF marker is not detected as such however, this could lead to an infinite
loop where ``JpegImagePlugin`` keeps trying to end the file.

Remove consecutive duplicate tiles that only differ by their offset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To prevent attempts to slow down loading times for images, if an image has consecutive
duplicate tiles that only differ by their offset, only load the last tile. Credit to
Google's `OSS-Fuzz`_ project for finding this issue.

:cve:`2022-22817`: Restrict builtins available to ImageMath.eval
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To limit :py:class:`PIL.ImageMath` to working with images, Pillow
will now restrict the builtins available to :py:meth:`!PIL.ImageMath.eval`. This will
help prevent problems arising if users evaluate arbitrary expressions, such as
``ImageMath.eval("exec(exit())")``.

:cve:`2022-22815`, :cve:`2022-22816`: ImagePath.Path array handling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:cve:`2022-22815` (:cwe:`126`) and :cve:`2022-22816` (:cwe:`665`) were found when
initializing ``ImagePath.Path``.

.. _OSS-Fuzz: https://github.com/google/oss-fuzz

Backwards incompatible changes
==============================

Python 3.6
^^^^^^^^^^

Pillow has dropped support for Python 3.6, which reached end-of-life on 2021-12-23.

PILLOW_VERSION constant
^^^^^^^^^^^^^^^^^^^^^^^

``PILLOW_VERSION`` has been removed. Use ``__version__`` instead.

FreeType 2.7
^^^^^^^^^^^^

Support for FreeType 2.7 has been removed; FreeType 2.8 is the minimum supported.

We recommend upgrading to at least `FreeType`_ 2.10.4, which fixed a severe
vulnerability introduced in FreeType 2.6 (:cve:`2020-15999`).

.. _FreeType: https://freetype.org/

Image.show command parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``command`` parameter has been removed. Use a subclass of
:py:class:`PIL.ImageShow.Viewer` instead.

Image._showxv
^^^^^^^^^^^^^

``Image._showxv`` has been removed. Use :py:meth:`~PIL.Image.Image.show`
instead. If custom behaviour is required, use :py:meth:`~PIL.ImageShow.register` to add
a custom :py:class:`~PIL.ImageShow.Viewer` class.

ImageFile.raise_ioerror
^^^^^^^^^^^^^^^^^^^^^^^

:py:exc:`IOError` was merged into :py:exc:`OSError` in Python 3.3. So, ``ImageFile.raise_ioerror``
has been removed. Use ``ImageFile.raise_oserror`` instead.


API changes
===========

Added line width parameter to ImageDraw polygon
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An optional line ``width`` parameter has been added to ``ImageDraw.Draw.polygon``.


API additions
=============

ImageShow.XDGViewer
^^^^^^^^^^^^^^^^^^^

If ``xdg-open`` is present on Linux, this new :py:class:`PIL.ImageShow.Viewer` subclass
will be registered. It displays images using the application selected by the system.

It is higher in priority than the other default :py:class:`PIL.ImageShow.Viewer`
instances, so it will be preferred by ``im.show()`` or :py:func:`.ImageShow.show()`.

Added support for "title" argument to DisplayViewer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Support has been added for the "title" argument in
:py:class:`~PIL.ImageShow.UnixViewer.DisplayViewer`, so that when ``im.show()`` or
:py:func:`.ImageShow.show()` use the ``display`` command line tool, the "title"
argument will also now be supported, e.g. ``im.show(title="My Image")`` and
``ImageShow.show(im, title="My Image")``.

Other changes
=============

Convert subsequent GIF frames to RGB or RGBA
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Since each frame of a GIF can have up to 256 colors, after the first frame it is
possible for there to be too many colors to fit in a P mode image. To allow for this,
seeking to any subsequent GIF frame will now convert the image to RGB or RGBA,
depending on whether or not the first frame had transparency.

Switched to libjpeg-turbo in macOS and Linux wheels
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Pillow wheels from PyPI for macOS and Linux have switched from libjpeg to
libjpeg-turbo. It is a fork of libjpeg, popular for its speed.

Because different JPEG decoders load images differently, JPEG pixels may be
altered slightly with this change.

Added support for pickling TrueType fonts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TrueType fonts may now be pickled and unpickled. For example::

    import pickle
    from PIL import ImageFont

    font = ImageFont.truetype("arial.ttf", size=30)
    pickled_font = pickle.dumps(font, protocol=pickle.HIGHEST_PROTOCOL)

    # Later...
    unpickled_font = pickle.loads(pickled_font)

Added support for additional TGA orientations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TGA images with top right or bottom right orientations are now supported.
