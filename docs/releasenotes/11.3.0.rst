11.3.0
------

Security
========

:cve:`2025-48379`: Write buffer overflow on BCn encoding
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There is a heap buffer overflow when writing a sufficiently large (>64k encoded with
default settings) image in the DDS format due to writing into a buffer without checking
for available space.

This only affects users who save untrusted data as a compressed DDS image.

* Unclear how large the potential write could be. It is likely limited by process
  segfault, so it's not necessarily deterministic. It may be practically unbounded.
* Unclear if there's a restriction on the bytes that could be emitted. It's likely that
  the only restriction is that the bytes would be emitted in chunks of 8 or 16.

This was introduced in Pillow 11.2.0 when the feature was added.

Deprecations
============

Image.fromarray mode parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``mode`` parameter in :py:meth:`~PIL.Image.fromarray()` has been deprecated. The
mode can be automatically determined from the object's shape and type instead.

.. note::

    Since pixel values do not contain information about palettes or color spaces, part
    of this functionality was restored in Pillow 12.0.0. The parameter can be used to
    place grayscale L mode data within a P mode image, or read RGB data as YCbCr for
    example.

Saving I mode images as PNG
^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to fit the 32 bits of I mode images into PNG, when PNG images can only contain
at most 16 bits for a channel, Pillow has been clipping the values. Rather than quietly
changing the data, this is now deprecated. Instead, the image can be converted to
another mode before saving::

    from PIL import Image
    im = Image.new("I", (1, 1))
    im.convert("I;16").save("out.png")

Other changes
=============

Added QOI saving
^^^^^^^^^^^^^^^^

Support has been added for saving QOI images. ``colorspace`` can be used to specify the
colorspace as sRGB with linear alpha, e.g. ``im.save("out.qoi", colorspace="sRGB")``.
By default, all channels will be linear.

Support using more screenshot utilities with ImageGrab on Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:meth:`~PIL.ImageGrab.grab` is now able to use GNOME Screenshot, grim or Spectacle
on Linux in order to take a snapshot of the screen.

Do not build against libavif < 1
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pillow only supports libavif 1.0.0 or later. In order to prevent errors when building
from source, if a user happens to have an earlier libavif on their system, Pillow will
now ignore it.

AVIF support in wheels
^^^^^^^^^^^^^^^^^^^^^^

Support for reading and writing AVIF images is now included in Pillow's wheels, except
for Windows ARM64 and iOS. libaom is available as an encoder and dav1d as a decoder.
(Thank you Frankie Dintino and Andrew Murray!)

iOS
^^^

Pillow now provides wheels that can be used on iOS ARM64 devices, and on the iOS
simulator on ARM64 and x86_64. Currently, only Python 3.13 wheels are available.
(Thank you Russell Keith-Magee and Andrew Murray!)

Python 3.14 beta
^^^^^^^^^^^^^^^^

To help other projects prepare for Python 3.14, wheels are now built for the
3.14 beta as a preview. This is not official support for Python 3.14, but rather
an opportunity for you to test how Pillow works with the beta and report any
problems.
