.. _PixelAccess:

:py:class:`PixelAccess` Class
=============================

The PixelAccess class provides read and write access to
:py:class:`PIL.Image` data at a pixel level.

.. note::  Accessing individual pixels is fairly slow. If you are looping over all of the pixels in an image, there is likely a faster way using other parts of the Pillow API.

Example
-------

The following script loads an image, accesses one pixel from it, then
changes it.

.. code-block:: python

    from PIL import Image
    with Image.open('hopper.jpg') as im:
        px = im.load()
    print (px[4,4])
    px[4,4] = (0,0,0)
    print (px[4,4])

Results in the following::

    (23, 24, 68)
    (0, 0, 0)

Access using negative indexes is also possible.

.. code-block:: python

    px[-1,-1] = (0,0,0)
    print (px[-1,-1])



:py:class:`PixelAccess` Class
-----------------------------------

.. class:: PixelAccess

  .. method:: __setitem__(self, xy, color):

        Modifies the pixel at x,y. The color is given as a single
        numerical value for single band images, and a tuple for
        multi-band images

        :param xy: The pixel coordinate, given as (x, y).
        :param color: The pixel value according to its mode. e.g. tuple (r, g, b) for RGB mode)

  .. method:: __getitem__(self, xy):

       Returns the pixel at x,y. The pixel is returned as a single
        value for single band images or a tuple for multiple band
        images

        :param xy: The pixel coordinate, given as (x, y).
        :returns: a pixel value for single band images, a tuple of
          pixel values for multiband images.

  .. method:: putpixel(self, xy, color):

        Modifies the pixel at x,y. The color is given as a single
        numerical value for single band images, and a tuple for
        multi-band images. In addition to this, RGB and RGBA tuples
        are accepted for P images.

        :param xy: The pixel coordinate, given as (x, y).
        :param color: The pixel value according to its mode. e.g. tuple (r, g, b) for RGB mode)

  .. method:: getpixel(self, xy):

       Returns the pixel at x,y. The pixel is returned as a single
        value for single band images or a tuple for multiple band
        images

        :param xy: The pixel coordinate, given as (x, y).
        :returns: a pixel value for single band images, a tuple of
          pixel values for multiband images.
