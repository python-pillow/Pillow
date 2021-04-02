.. _file-handling:

File Handling in Pillow
=======================

When opening a file as an image, Pillow requires a filename, ``pathlib.Path``
object, or a file-like object. Pillow uses the filename or ``Path`` to open a
file, so for the rest of this article, they will all be treated as a file-like
object.

The following are all equivalent::

    from PIL import Image
    import io
    import pathlib

    with Image.open('test.jpg') as im:
        ...

    with Image.open(pathlib.Path('test.jpg')) as im2:
        ...

    with open('test.jpg', 'rb') as f:
        im3 = Image.open(f)
        ...

    with open('test.jpg', 'rb') as f:
        im4 = Image.open(io.BytesIO(f.read()))
        ...

If a filename or a path-like object is passed to Pillow, then the resulting
file object opened by Pillow may also be closed by Pillow after the
``Image.Image.load()`` method is called, provided the associated image does not
have multiple frames.

Pillow cannot in general close and reopen a file, so any access to
that file needs to be prior to the close.

Image Lifecycle
---------------

* ``Image.open()`` Filenames and ``Path`` objects are opened as a file.
  Metadata is read from the open file. The file is left open for further usage.

* ``Image.Image.load()`` When the pixel data from the image is
  required, ``load()`` is called. The current frame is read into
  memory. The image can now be used independently of the underlying
  image file.

  If a filename or a ``Path`` object was passed to ``Image.open()``, then the
  file object was opened by Pillow and is considered to be used exclusively by
  Pillow. So if the image is a single-frame image, the file will be closed in
  this method after the frame is read. If the image is a multi-frame image,
  (e.g. multipage TIFF and animated GIF) the image file is left open so that
  ``Image.Image.seek()`` can load the appropriate frame.

* ``Image.Image.close()`` Closes the file and destroys the core image object.
  This is used in the Pillow context manager support. e.g.::

      with Image.open('test.jpg') as img:
         ...  # image operations here.


The lifecycle of a single-frame image is relatively simple. The file must
remain open until the ``load()`` or ``close()`` function is called or the
context manager exits.

Multi-frame images are more complicated. The ``load()`` method is not
a terminal method, so it should not close the underlying file. In general,
Pillow does not know if there are going to be any requests for additional
data until the caller has explicitly closed the image.


Complications
-------------

* ``TiffImagePlugin`` has some code to pass the underlying file descriptor into
  libtiff (if working on an actual file). Since libtiff closes the file
  descriptor internally, it is duplicated prior to passing it into libtiff.

* After a file has been closed, operations that require file access will fail::

    with open('test.jpg', 'rb') as f:
        im5 = Image.open(f)
    im5.load() # FAILS, closed file

    with Image.open('test.jpg') as im6:
        pass
    im6.load() # FAILS, closed file


Proposed File Handling
----------------------

* ``Image.Image.load()`` should close the image file, unless there are
  multiple frames.

* ``Image.Image.seek()`` should never close the image file.

* Users of the library should use a context manager or call
  ``Image.Image.close()`` on any image opened with a filename or ``Path``
  object to ensure that the underlying file is closed.
