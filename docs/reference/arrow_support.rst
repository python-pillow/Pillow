=============
Arrow Support
=============

Arrow is an in memory data exchange format that is the spritual
successor to the numpy array interface. It provides for zero copy
access to columnar data, which in our case is Image data.

The goal with Arrow is to provide native zero-copy interop with any
arrow provider or consumer in the Python ecosystem.

.. warning:: Zero-copy does not mean zero allocation -- The internal
memory layout of Pillow images contains an allocation for row
pointers, so there is a non-zero, but significantly smaller than a
full copy memory cost to reading an arrow image.


Data Formats
============

Pillow currently supports exporting arrow images in all modes
**except** for ``BGR;15``, ``BGR;16`` and ``BGR;24``. This is due to
line length packing in these modes making for non-continuous memory.

For single band images, the exported array is width*height elements,
with each pixel corresponding to the appropriate arrow type.

For multiband images, the exported array is width*height fixed length
4 element arrays of uint8. This is memory compatible with the raw
image storage of 4 bytes per pixel.

Mode ``1`` images are exported as 1 uint8 byte/pixel, as this is
consistent with the internal storage.

Pillow will accept, but not produce, one other format. For any
multichannel image with 32 bit storage per pixel, Pillow will accept
an array of width*height int32 elements, which will then be
interpreted using the mode specific interpretation of the bytes.

The image mode must match the arrow band format when reading single
channel images

Memory Allocator
================

Pillow's default memory allocator, the :ref:`block_allocator`,
allocates up to a 16MB block for images by default. Larger images
overflow into additional blocks. Arrow requires a single continuous
memory allocation, so images allocated in multiple blocks cannot be
exported in the arrow format.

To enable the single block allocator::

  from PIL import Image
  Image.core.set_use_block_allocator(1)

Note that this is a global setting, not a per image setting.

Unsupported Features
====================

* Table/Dataframe protocol. We currently support a single array.
* Null markers, producing or consuming. Null values are inferred from
  the mode. e.g. RGB images are stored in the first three bytes of
  each 32 bit pixel, and the last byte is an implied null.
* Schema Negotiation. There is an optional schema for the requested
  datatype in the arrow source interface. We currently ignore that
  parameter.
* Array Metadata.

Internal Details
================

Python Arrow C interface:
https://arrow.apache.org/docs/format/CDataInterface/PyCapsuleInterface.html

The memory that is exported from the arrow interface is shared -- not
copied, so the lifetime of the memory allocation is no longer strictly
tied to the life of the python object.

The core imaging struct now has a refcount associated with it, and the
lifetime of the core image struct is now divorced from the python
image object. Creating an arrow reference to the image increments the
refcount, and the imaging struct is only released when the refcount
reaches 0.
