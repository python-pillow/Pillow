.. py:module:: PIL.PyAccess
.. py:currentmodule:: PIL.PyAccess

:py:mod:`PyAccess` Module
=========================

The :py:mod:`PyAccess` module provides a CFFI/Python implementation of the :ref:`PixelAccess`. This implementation is far faster on PyPy than the PixelAccess version.

.. note:: Accessing individual pixels is fairly slow. If you are
           looping over all of the pixels in an image, there is likely
           a faster way using other parts of the Pillow API.

Example
-------

The following script loads an image, accesses one pixel from it, then changes it.

.. code-block:: python
    
    from PIL import Image
    im = Image.open('hopper.jpg')
    px = im.load()
    print (px[4,4])
    px[4,4] = (0,0,0)
    print (px[4,4])

Results in the following::

    (23, 24, 68)
    (0, 0, 0)

   

:py:class:`PyAccess` Class
--------------------------

.. autoclass:: PIL.PyAccess.PyAccess()
    :members:
