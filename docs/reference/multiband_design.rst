.. _multiband-design:

=====================================
Multiband and high bit depth images
=====================================

.. note:: This is a **design proposal**, not a description of current
  behavior. Nothing described here is implemented yet. Discussion
  happens on :issue:`1888` and on the pull request that adds this
  document.

Problem
=======

Pillow can store images with more than 8 bits per sample only when
they have a single band: ``I;16``, ``I`` and ``F``. Multiband images
are limited to at most four 8-bit bands. As a result:

* 16-bit RGB(A) TIFF and PNG images are reduced to 8 bits per sample
  when they are opened.
* Images with more than four bands, such as satellite imagery,
  microscopy or CMYK with spot channels, cannot be opened, or lose
  bands.
* Floating point RGB(A) data, common in VFX and machine learning
  pipelines, cannot be represented at all.
* 10 and 12-bit AVIF images are reduced to 8 bits.
* :ref:`arrow-support` exports every multiband image as four
  ``uint8`` values per pixel.

This has been requested many times since :issue:`1888` was opened in
2016, and many duplicates have been closed in its favor.

Goals
=====

* Store images with an arbitrary number of bands, where each band is
  ``uint8``, ``uint16``, ``int32`` or ``float32``.
* Give bands a meaning, so that a 16-bit image can still be treated as
  RGB(A), and a five-band image can expose four of its bands as RGBA.
* Allow bands with different sample types in one image, e.g. 16-bit
  RGB with an 8-bit alpha band.
* Support every operation that works on each band independently
  (crop, resize, transpose, filters, ...) without new C code per
  operation.
* Zero-copy exchange with NumPy and Arrow consumers.
* Read and write TIFF and PNG data at full depth. Other formats can
  follow.
* Leave existing modes, their memory layout and their behavior
  unchanged.

Non-goals
=========

* Geospatial features: pyramids, tiled storage, spatial reference
  metadata. Tools built on GDAL, such as rasterio, already cover
  these. The design should not rule them out, but they are not part
  of this work.
* An OpenEXR plugin. This design is a prerequisite for one, not a
  replacement.
* Replacing the existing interleaved storage for the existing modes.

Current internals
=================

The relevant parts of ``ImagingMemoryInstance`` in
``src/libImaging/Imaging.h`` are:

* ``mode``: a ``ModeID`` enum value. ``getModeData()`` returns a
  ``ModeData`` struct for each mode, currently holding only the mode
  name.
* ``type``: one of ``IMAGING_TYPE_UINT8``, ``IMAGING_TYPE_INT32``,
  ``IMAGING_TYPE_FLOAT32`` or ``IMAGING_TYPE_I16``.
* ``depth``: unused ("ignored in this version").
* ``bands``: 1 to 4.
* ``pixelsize``: 1, 2 or 4 bytes. Multiband 8-bit modes are stored
  interleaved, four bytes per pixel, with unused bytes as padding.
* ``band_names`` and ``arrow_band_format``: added for Arrow export,
  limited to four bands.

Almost all C operations dispatch on ``mode`` or on ``image8`` /
``image32``, and assume a pixel fits in four bytes.

Prior work
==========

* :pr:`1839` (2016) added opening of 2 to 5-band ``uint16`` TIFFs.
* :pr:`8224` (2024) built on it, adding an opaque interleaved ``MB``
  mode with a variable sample size, and support in ``copy``,
  ``crop``, ``transpose`` and ``getpixel``. Review raised two
  questions that this document tries to answer: what the metadata
  design for pixel format and band layout is, and how operations work
  on pixels of arbitrary shape. Since then, image modes have changed
  from strings to the ``ModeID`` enum, so the pull request would need
  to be rewritten rather than rebased.
* :issue:`6547` proposed a per-band format struct inside interleaved
  storage. It was closed because the rewrite did not make the C code
  simpler.
* :pr:`9274` moved more per-mode data into ``ModeData``. It was closed
  for inactivity, but the direction is compatible with this proposal.

The lesson from these attempts is that interleaved storage with
arbitrary pixel sizes needs new code in nearly every C operation, and
the number of combinations to support grows quickly.

Proposal: planar storage
========================

Store each band of a multiband high bit depth image as a separate
single-band core image, using the storage that already exists:

====================  ================================
Sample type           Existing single-band core image
====================  ================================
``uint8``             ``L``
``uint16``            ``I;16``
``int32``             ``I``
``float32``           ``F``
====================  ================================

A planar image is a list of these planes, all the same size, plus
metadata describing each band.

Advantages:

* Every operation that already works on ``L``, ``I;16``, ``I`` and
  ``F`` and treats bands independently works on planar images by
  applying it to each plane. No per-operation C code is needed.
* Mixed sample types are trivial, as each plane has its own type.
* The number of bands is not baked into the storage layout.
* Each plane is already a contiguous single-band image, so it maps
  directly to an Arrow array (see below).

Costs:

* Operations that mix bands (color conversion, luminance, alpha
  compositing, ``paste`` with a mask, color management) need planar
  implementations.
* Decoders and encoders that produce or consume interleaved data need
  to shuffle between interleaved and planar layouts.
* Pixel access touches one plane per band, which is slower for
  per-pixel work than interleaved storage.

Band metadata
-------------

Each band has:

* a name, e.g. ``R``, ``G``, ``B``, ``A``, or a free-form name for
  extra bands;
* a sample type: ``uint8``, ``uint16``, ``int32`` or ``float32``;
* a role: color, alpha, or extra. Extra bands are carried through
  operations but ignored by color-aware ones.

The image as a whole records how its color bands should be
interpreted (e.g. RGB, CMYK, grayscale), so that a 16-bit RGBA image
and an 8-bit RGBA image share the same interpretation and differ only
in sample type.

How this relates to ``mode`` is an open question (see below).

Arrow mapping
-------------

A planar image maps naturally to an Arrow struct array with one child
array per band. Each child is a primitive array of ``width * height``
values of the band's type, and the field names are the band names. The
child buffers can point directly at the planes, so export is
zero-copy. This removes the four-band limit of ``band_names`` and the
four ``uint8`` layout for multiband export.

As with the existing Arrow support, each plane has to be allocated in
a single block to be exported.

Phases
======

Each phase can be released on its own.

1. **Core planar image.** Mostly at the Python level: assemble a
   planar image from existing single-band core images, with band
   metadata. Support all band-independent operations by applying them
   per plane. Create planar images from Arrow arrays (zero-copy per
   plane) and from interleaved NumPy arrays (copying). Export to
   Arrow.
2. **File formats.** Unpack decoded data into planes, and pack planes
   for encoders. TIFF first, as it already decodes 16-bit multiband
   data, then PNG, then others such as JPEG 2000, WebP and AVIF.
3. **Band-mixing operations.** Conversion to and from the existing
   modes (e.g. 16-bit RGB to ``RGB`` and back), grayscale conversion,
   alpha compositing, ``paste``, and color management.

Alternatives considered
=======================

Interleaved storage with a variable sample size (:pr:`8224`)
  Fits the existing storage model, but most C operations would need
  code for every combination of band count and sample type, and mixed
  sample types are hard to support.

Additional fixed modes, e.g. ``RGB;16`` and ``RGBA;16``
  Small and concrete, and covers the most common request (16-bit RGB
  PNG and TIFF), but every operation needs support for each new mode,
  and it does not help with float data or more than four bands. It
  could still be added as a stopgap, provided it can later be
  expressed as a planar image.

Interoperability only
  Passing arrays through Arrow or NumPy without supporting operations
  is cheap, but does not meet the goals above. Libraries such as
  tifffile and imageio already provide this.

Security considerations
=======================

* Set a maximum number of bands, enforced in C, and check for
  overflow when computing sizes from width, height, bands and sample
  size.
* ``Image.MAX_IMAGE_PIXELS`` counts pixels, not bytes.
  With many bands of up to four bytes each, the memory used per pixel
  grows considerably. Decide whether
  ``Image.DecompressionBombWarning`` and
  ``Image.DecompressionBombError`` should take bands and sample size
  into account.
* Decoders must validate that the band count and sample types from
  file headers agree with the data actually decoded.

Open questions
==============

* **Mode naming.** Should planar images have new ``mode`` strings
  (e.g. ``RGB;16``), a single generic mode with the details in band
  metadata, or a new attribute alongside ``mode``? What do
  ``Image.mode`` and ``Image.getbands()`` return?
* **Where planes live.** Should the list of planes live in Python, on
  ``Image``, or in C, as a new core image type? Python is faster to
  build; C keeps memory safety checks and Arrow export in one place.
* **Pixel access.** What do ``getpixel()``, ``putpixel()`` and
  ``getdata()`` return for planar images?
* **Bit depth within a type.** How to record that a ``uint16`` band
  holds 10 or 12-bit data (AVIF, some TIFFs), so it can be saved
  without loss.
* **Signed 16-bit and 64-bit types.** Are ``int16``, ``float16`` and
  ``float64`` needed? Converting them to the types above loses
  precision or range.
* **NumPy.** Can ``__array_interface__`` describe a planar image
  without copying, or is Arrow the zero-copy path?
* **Test images.** Small, redistributable images are needed for each
  target use case: 16-bit RGB(A) PNG and TIFF, float32 RGB TIFF,
  many-band ``uint16`` TIFF, and 10/12-bit AVIF.
