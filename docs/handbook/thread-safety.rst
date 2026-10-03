.. _thread-safety:

Thread safety
=============

Pillow can be used from multiple threads,
both on the default build of Python and on the free-threaded build (:pep:`703`).

Many operations on an image release the :term:`global interpreter lock <GIL>`
while they process pixel data, so on either build,
other threads may run while an operation is still in progress.

Pillow does **not** add locks around individual images.
Sharing an image between threads is safe only in the ways described below.
Anything beyond that needs to be synchronized by your application.

Safe
----

* **Separate images in separate threads.**
  Opening, processing and saving different :py:class:`~PIL.Image.Image` objects
  concurrently is supported. This is a natural way to parallelize Pillow work.

* **Reading a shared, loaded image.**
  Several threads may read the same image at once, as long as no thread modifies it.
  This includes operations that return a new image, such as resizing, cropping,
  filtering, etc.
  Saving is safe in most cases, but some encoders may concurrently modify an image's
  ``encoderinfo``, causing issues. Conversions that do not involve palette quantization
  are also safe between threads.
  However, take care to call :py:meth:`~PIL.Image.Image.load` from a single thread
  before sharing an image, because otherwise several threads may try to read from
  the same file object at once.

* **Fonts.**
  A :py:class:`~PIL.ImageFont.FreeTypeFont` may be used by several threads at once
  to measure and render text.

Not safe
--------

* **Modifying an image while another thread uses it.**
  This includes in-place operations such as :py:meth:`~PIL.Image.Image.paste`,
  :py:meth:`~PIL.Image.Image.putpixel`, :py:meth:`~PIL.Image.Image.putdata`,
  :py:meth:`~PIL.Image.Image.putpalette`, :py:meth:`~PIL.Image.Image.putalpha`,
  drawing with :py:meth:`~PIL.ImageDraw.Draw`, and writing through the
  :py:class:`PixelAccess` class (as returned by :py:meth:`~PIL.Image.Image.load`).
  The results are undefined: the reading thread may see partly updated pixels,
  and some combinations could crash the interpreter.
  This applies to the default build as well as to the free-threaded build.

* **Changing the frame of a shared image.**
  :py:meth:`~PIL.Image.Image.seek` modifies the image,
  so a multi-frame image must not be seeked while other threads use it.
  You can use either multiple copies of the same multi-frame image file,
  or load and :py:meth:`~PIL.Image.Image.copy` them in a single thread up-front.

* **Closing an image while another thread uses it.**
  :py:meth:`~PIL.Image.Image.close` releases the image's data,
  so other threads must have finished with the image first.

* **Varying a font.**
  :py:meth:`~PIL.ImageFont.FreeTypeFont.set_variation_by_name` and
  :py:meth:`~PIL.ImageFont.FreeTypeFont.set_variation_by_axes` change the font
  in-place for every thread that uses it.
  You can use :py:meth:`~PIL.ImageFont.FreeTypeFont.font_variant` to create a
  separate variant font object instead.

If you need to modify an image that other threads are using, you'll need to
synchronize access with e.g. a :py:class:`threading.Lock` or other method.

Global settings
---------------

Module-level settings are shared by all threads. These include:

* :py:data:`PIL.Image.MAX_IMAGE_PIXELS`
* :py:data:`PIL.ImageFile.LOAD_TRUNCATED_IMAGES`
* :py:data:`PIL.ImageFile.MAXBLOCK`
* :py:data:`PIL.ImageFile.SAFEBLOCK`
* the plugin registries populated by functions such as :py:func:`PIL.Image.register_open`
* the :ref:`block allocator <block_allocator>` settings

You may wish to set these once, in a single thread, as they will affect others.
