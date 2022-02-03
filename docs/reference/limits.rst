Limits
------

This page is documentation to the various fundamental size limits in
the Pillow implementation.

Internal Limits
===============

* Image sizes cannot be negative. These are checked both in
  ``Storage.c`` and ``Image.py``

* Image sizes may be 0. (Although not in 3.4)

* Maximum pixel dimensions are limited to INT32, or 2^31 by the sizes
  in the image header.

* Individual allocations are limited to 2GB in ``Storage.c``

* The 2GB allocation puts an upper limit to the xsize of the image of
  either 2^31 for 'L' or 2^29 for 'RGB'

* Individual memory mapped segments are limited to 2GB in map.c based
  on the overflow checks. This requires that any memory mapped image
  is smaller than 2GB, as calculated by ``y*stride`` (so 2Gpx for 'L'
  images, and .5Gpx for 'RGB'

Format Size Limits
==================

* ICO: Max size is 256x256

* Webp: 16383x16383 (underlying library size limit:
  https://developers.google.com/speed/webp/docs/api)
