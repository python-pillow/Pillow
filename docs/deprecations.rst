.. _deprecations:

Deprecations and removals
=========================

This page lists Pillow features that are deprecated, or have been removed in
past major releases, and gives the alternatives to use instead.

Deprecated features
-------------------

Below are features which are considered deprecated. Where appropriate,
a ``DeprecationWarning`` is issued.

Setting the size of TIFF images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 5.3.0

Setting the image size of a TIFF image (eg. ``im.size = (256, 256)``) issues
a ``DeprecationWarning``:

.. code-block:: none

    Setting the size of a TIFF image directly is deprecated, and will
    be removed in a future version. Use the resize method instead.

PILLOW_VERSION and VERSION constants
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 5.2.0

Two version constants – ``VERSION`` (the old PIL version, always 1.1.7) and
``PILLOW_VERSION`` – have been deprecated and will be removed in the next
major release. Use ``__version__`` instead.

Removed features
----------------

Deprecated features are only removed in major releases after an appropriate
period of deprecation has passed.

Undocumented ImageOps functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Removed in version 6.0.0.*

Several undocumented functions in ``ImageOps`` have been removed. Use the equivalents
in ``ImageFilter`` instead:

==========================  ============================
Removed                     Use instead
==========================  ============================
``ImageOps.box_blur``       ``ImageFilter.BoxBlur``
``ImageOps.gaussian_blur``  ``ImageFilter.GaussianBlur``
``ImageOps.gblur``          ``ImageFilter.GaussianBlur``
``ImageOps.usm``            ``ImageFilter.UnsharpMask``
``ImageOps.unsharp_mask``   ``ImageFilter.UnsharpMask``
==========================  ============================

PIL.OleFileIO
~~~~~~~~~~~~~

*Removed in version 6.0.0.*

PIL.OleFileIO was removed as a vendored file and in Pillow 4.0.0 (2017-01) in favour of
the upstream olefile Python package, and replaced with an ``ImportError`` in 5.0.0
(2018-01). The deprecated file has now been removed from Pillow. If needed, install from
PyPI (eg. ``pip install olefile``).
