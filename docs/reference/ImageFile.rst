.. py:module:: PIL.ImageFile
.. py:currentmodule:: PIL.ImageFile

:py:mod:`~PIL.ImageFile` Module
===============================

The :py:mod:`~PIL.ImageFile` module provides support functions for the image open
and save functions.

In addition, it provides a :py:class:`Parser` class which can be used to decode
an image piece by piece (e.g. while receiving it over a network connection).
This class implements the same consumer interface as the standard **sgmllib**
and **xmllib** modules.

Example: Parse an image
-----------------------

.. code-block:: python

    from PIL import ImageFile

    fp = open("hopper.pgm", "rb")

    p = ImageFile.Parser()

    while 1:
        s = fp.read(1024)
        if not s:
            break
        p.feed(s)

    im = p.close()

    im.save("copy.jpg")


Classes
-------

.. autoclass:: PIL.ImageFile.Parser()
    :members:

.. autoclass:: PIL.ImageFile.PyDecoder()
    :members:

.. autoclass:: PIL.ImageFile.ImageFile()
    :member-order: bysource
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: PIL.ImageFile.StubImageFile()
    :members:
    :show-inheritance:

Constants
---------

.. autodata:: PIL.ImageFile.LOAD_TRUNCATED_IMAGES
.. autodata:: PIL.ImageFile.ERRORS
    :annotation:
