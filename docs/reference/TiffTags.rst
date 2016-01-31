.. py:module:: PIL.TiffTags
.. py:currentmodule:: PIL.TiffTags

:py:mod:`TiffTags` Module
=========================

The :py:mod:`TiffTags` module exposes many of the stantard TIFF
metadata tag numbers, names, and type information.

.. method:: lookup(tag)

    :param tag: Integer tag number
    :returns: Taginfo namedtuple, From the ``TAGS_V2`` info if possible,
        otherwise just populating the value and name from ``TAGS``.
        If the tag is not recognized, "unknown" is returned for the name

.. versionadded:: 3.1.0

.. class:: TagInfo

  .. method:: __init__(self, value=None, name="unknown", type=None, length=0, enum=None)

     :param value: Integer Tag Number
     :param name: Tag Name
     :param type: Integer type from :py:attr:`PIL.TiffTags.TYPES`
     :param length: Array length: 0 == variable, 1 == single value, n = fixed
     :param enum: Dict of name:integer value options for an enumeration
   
  .. method:: cvt_enum(self, value)

     :param value: The enumerated value name
     :returns: The integer corresponding to the name. 

.. versionadded:: 3.0.0

.. py:attribute:: PIL.TiffTags.TAGS_V2

    The ``TAGS_V2`` dictionary maps 16-bit integer tag numbers to
    :py:class:`PIL.TagTypes.TagInfo` tuples for metadata fields defined in the TIFF
    spec.

.. versionadded:: 3.0.0

.. py:attribute:: PIL.TiffTags.TAGS

    The ``TAGS`` dictionary maps 16-bit integer TIFF tag number to
    descriptive string names.  For instance:

        >>> from PIL.TiffTags import TAGS
        >>> TAGS[0x010e]
        'ImageDescription'

    This dictionary contains a superset of the tags in TAGS_V2, common
    EXIF tags, and other well known metadata tags.

.. py:attribute:: PIL.TiffTags.TYPES

    The ``TYPES`` dictionary maps the TIFF type short integer to a
    human readable type name.
