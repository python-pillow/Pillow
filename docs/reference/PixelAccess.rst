.. _PixelAccess:

:py:class:`PixelAccess` class
=============================

The PixelAccess class provides read and write access to
:py:class:`PIL.Image` data at a pixel level.

.. note:: Accessing individual pixels is fairly slow. If you are
          looping over all of the pixels in an image, there is likely
          a faster way using other parts of the Pillow API.

          :mod:`~PIL.Image`, :mod:`~PIL.ImageChops` and :mod:`~PIL.ImageOps`
          have methods for many standard operations. If you wish to perform
          a custom mapping, check out :py:meth:`~PIL.Image.Image.point`.

Example
-------

The following script loads an image, accesses one pixel from it, then
changes it. ::

    from PIL import Image

    with Image.open("hopper.jpg") as im:
        px = im.load()
    print(px[4, 4])
    px[4, 4] = (0, 0, 0)
    print(px[4, 4])

Results in the following::

    (23, 24, 68)
    (0, 0, 0)

Access using negative indexes is also possible. ::

    px[-1, -1] = (0, 0, 0)
    print(px[-1, -1])



:py:class:`PixelAccess` class
-----------------------------

.. class:: PixelAccess
  :canonical: PIL.Image.core.PixelAccess

  .. method:: __getitem__(self, xy: tuple[int, int]) -> float | tuple[int, ...]

        Returns the pixel at x,y. The pixel is returned as a single
        value for single band images or a tuple for multi-band images.

        :param xy: The pixel coordinate, given as (x, y).
        :returns: a pixel value for single band images, a tuple of
                  pixel values for multiband images.

  .. method:: __setitem__(self, xy: tuple[int, int], color: float | tuple[int, ...]) -> None

        Modifies the pixel at x,y. The color is given as a single
        numerical value for single band images, and a tuple for
        multi-band images.

        :param xy: The pixel coordinate, given as (x, y).
        :param color: The pixel value according to its mode,
                      e.g. tuple (r, g, b) for RGB mode.
