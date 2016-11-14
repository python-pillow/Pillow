File Handling in Pillow
=======================

When opening a file as an image, Pillow requires a filename,
pathlib.Path object, or a file-like object.  Pillow uses the filename
or Path to open a file, so for the rest of this article, they will all
be treated as a file-like object. 

The first four of these items are equivalent, the last is dangerous
and may fail::

    from PIL import Image
    import io
    import pathlib
    
    im = Image.open('test.jpg')

    im2 = Image.open(pathlib.Path('test.jpg'))

    f = open('test.jpg', 'rb')
    im3 = Image.open(f)
    
    with open('test.jpg', 'rb') as f:
        im4 = Image.open(io.BytesIO(f.read()))

    # Dangerous FAIL:
    with open('test.jpg', 'rb') as f:
        im5 = Image.open(f)
    im5.load() # FAILS, closed file

The documentation specifies that the file will be closed after the
``Image.Image.load()`` method is called.  This is an aspirational
specification rather than an accurate reflection of the state of the
code. 

Pillow cannot in general close and reopen a file, so any access to
that file needs to be prior to the close. 

Issues
------

The current open file handling is inconsistent at best:

* Most of the image plugins do not close the input file.
* Multi-frame images behave badly when seeking through the file, as
  it's legal to seek backward in the file until the last image is
  read, and then it's not. 
* Using the file context manager to provide a file-like object to
  Pillow is dangerous unless the context of the image is limited to
  the context of the file. 

Image Lifecycle
---------------

* ``Image.open()`` called. Path-like objects are opened as a
  file. Metadata is read from the open file. The file is left open for
  further usage.

* ``Image.Image.load()`` when the pixel data from the image is
  required, ``load()`` is called. The current frame is read into
  memory. The image can now be used independently of the underlying
  image file. 

* ``Image.Image.seek()`` in the case of multi-frame images
  (e.g. multipage TIFF and animated GIF) the image file left open so
  that seek can load the appropriate frame.  When the last frame is
  read, the image file is closed (at least in some image plugins), and
  no more seeks can occur.

* ``Image.Image.close()`` Closes the file pointer and destroys the
  core image object. This is used in the Pillow context manager
  support. e.g.::

      with Image.open('test.jpg') as img:
         ...  # image operations here. 


The lifecycle of a single frame image is relatively simple. The file
must remain open until the ``load()`` or ``close()`` function is
called. 

Multi-frame images are more complicated. The ``load()`` method is not
a terminal method, so it should not close the underlying file. The
current behavior of ``seek()`` closing the underlying file on
accessing the last frame is presumably a heuristic for closing the
file after iterating through the entire sequence. In general, Pillow
does not know if there are going to be any requests for additional
data until the caller has explicitly closed the image. 


Complications
-------------

* TiffImagePlugin has some code to pass the underlying file descriptor
  into libtiff (if working on an actual file). Since libtiff closes
  the file descriptor internally, it is duplicated prior to passing it
  into libtiff. 

* ``decoder.handles_eof`` This slightly misnamed flag indicates that
  the decoder wants to be called with a 0 length buffer when reads are
  done. Despite the comments in ``ImageFile.load()``, the only decoder
  that actually uses this flag is the Jpeg2K decoder. The use of this
  flag in Jpeg2K predated the change to the decoder that added the
  pulls_fd flag, and is therefore not used.

* I don't think that there's any way to make this safe without
  changing the lazy loading::

    # Dangerous FAIL:
    with open('test.jpg', 'rb') as f:
        im5 = Image.open(f)
    im5.load() # FAILS, closed file


Proposed File Handling
----------------------

* ``Image.Image.load()`` should close the image file, unless there are
  multiple frames.

* ``Image.Image.seek()`` should never close the image file. 

* Users of the library should call ``Image.Image.close()`` on any
  multi-frame image to ensure that the underlying file is closed. 

