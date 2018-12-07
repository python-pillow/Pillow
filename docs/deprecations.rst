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

Undocumented ImageOps functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 4.3.0

Several undocumented functions in ``ImageOps`` have been deprecated. They issue
a ``DeprecationWarning`` informing which equivalent to use from ``ImageFilter``
instead:

==========================  ============================
Deprecated                  Use instead
==========================  ============================
``ImageOps.box_blur``       ``ImageFilter.BoxBlur``
``ImageOps.gaussian_blur``  ``ImageFilter.GaussianBlur``
``ImageOps.gblur``          ``ImageFilter.GaussianBlur``
``ImageOps.usm``            ``ImageFilter.UnsharpMask``
``ImageOps.unsharp_mask``   ``ImageFilter.UnsharpMask``
==========================  ============================

PIL.OleFileIO
~~~~~~~~~~~~~

.. deprecated:: 4.0.0

The vendored version of olefile has been removed. Attempting to import
``PIL.OleFileIO`` issues a ``DeprecationWarning`` (from 4.0.0) or raises
``ImportError`` (from 5.0.0):

.. code-block:: none

    PIL.OleFileIO is deprecated. Use the olefile Python package
    instead. This module will be removed in a future version.

Removed features
----------------

Deprecated features are only removed in major releases after an appropriate
period of deprecation has passed.

Vendored olefile
~~~~~~~~~~~~~~~~

*Removed in version 4.0.0.*

The vendored version of the olefile Python package was removed in favour of the
upstream package. Install if needed (eg. ``pip install olefile``).
