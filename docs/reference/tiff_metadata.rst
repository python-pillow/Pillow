Tiff Metadata
=============

Pillow currently reads TIFF metadata in pure python and writes either
through its own writer (if writing an uncompressed tiff) or libtiff. 

Basic overview
++++++++++++++

TIFF is Tagged Image File Format -- the metadata is stored as a well
known tag number, a type, a quantity, and the data. Many tags are
defined in the spec and implemented in libtiff, but there's also the
possibility to add custom tags that aren't specified in the spec. The
metadata is packed into a structure known as the Image File Directory,
or IFD. We define many of these tags in :py:mod:`~PIL.TiffTags`.

The Tiff IFD is also used in other file formats (like JPEG) to store
EXIF information or other metadata. 

Writing Metadata in Libtiff
+++++++++++++++++++++++++++

There are three categories of metadata::

* Built in, but not special cases
* Special cases, built in
* Custom tags

These categories aren't listed in the docs anywhere, it's from a dive
through libtif's tif_dir.c and the various headers. 

Metadata is set using a single api call to ``TIFFVSetField(tiff, tag,
*args)`` which has a var args setup, so the function signature changes
based on the tag passed in. The count and data sizes are defined in
the libtiff directory headers. There are many different memcopys that
are performed with **no** validation of the input parameters, either
in type or quantity. These lead to a segfault in the best case.

.. Warning::
  This is a security nightmare.  

Because of this security nightmare, we're whitelisting and testing
individual tiff tags for writing. The complexity of this simple
interface means that we have to essentially duplicate the logic of the
libtiff interface to put the parameters in the right configuration. We
are whitelisting these tags in :py:mod:`~PIL.TiffTags.LIBTIFF_CORE`.


Built In
--------

There is a long list (in theory, you have to go through the code for
them) of built in items that regular. These have one of three call
signatures:

* Individual: ``TIFFVSetField(tiff, tag, item)``
* Multiple, passcount=0: ``TIFFVSetField(tiff, tag, items* )``
* Multiple, passcount=1: ``TIFFVSetField(tiff, tag, ct, items* )``


In libtiff4, the individual integer like numeric items are passed as
32 bit ints (signed or unsigned as appropriate) even if the actual
item is a short or char. The individual rational and floating point
types are all passed as a double.

The multiple value items are passed as pointers to packed arrays of
the correct type, short for short. 

UNDONE -- This isn't quite true: The count is only used for items
where field_passcount is true. Then if ``field->writecount`` ==
``TIFF_VARIABLE2``, then it's a ``uint32``, otherwise count is an int.
Otherwise, if ``field_writecount`` is ``TIFF_VARIABLE`` or
``TIFF_VARIABLE2``, then the count is not passed and 1 item is read.  If it's
``TIFF_SPP``, then it's set to samplesperpixel. Otherwise, it's set to
the ``field_writecount``.


Special Cases
-------------

There are a set of special cases in the ``tif_dir.c:_TIFFVSetField``
function where tag by tag, the individual items are pulled. These are
mainly items that are specifically used by the tiff decoder. The
individual items all follow the pattern of the built ins above, but
the array based items are special, each in their own way.

* Where there are two shorts passed in, they are passed as separate
  parameters rather than a packed array. (e.g. ``TIFFTAG_PAGENUMBER``)

* ``TIFFTAG_REFERENCEBLACKWHITE`` is just passed as an array of 6
  ``float``, there's no count of items. 

* ``TIFFTAG_COLORMAP`` is passed as three pointers to arrays of ``short``

* ``TIFFTAG_TRANSFERFUNCTION`` is passed as 1 or 3 pointers to arrays
  of ``short``

* ``TIFFTAG_INKNAMES`` is passed as a length and a ``char*``.

* ``TIFFTAG_SUBIFD`` is passed as a length and pointer to ``uint32`` 
  UNDONE -- is this length in bytes, or in integers, and does this
  change in libtiff5?

Custom Tags
-----------

These are tags that are not defined in libtiff. To use these, we would
need to define the tag for that image by passing in the appropriate
definition. 

.. Note::
  Custom tags are currently unimplemented.


Writing Metadata in Python
++++++++++++++++++++++++++

UNDONE -- review/expand this on down. 

When writing a TIFF file using python, the IFD is written using the
code at
:py:mod:`~PIL.TiffImagePlugin.ImageFileDirectory_v2.save`. This uses
the types from the IFD to control the writing. This leads to safe but
possibly out of spec writing.   

Metadata Storage in Pillow
++++++++++++++++++++++++++

* See TiffImagePlugin
* tags_v2 vs tags

Reading Metadata in TiffImagePlugin
+++++++++++++++++++++++++++++++++++

* Type confusion between file and spec.

