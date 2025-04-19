.. py:module:: PIL.TiffTags
.. py:currentmodule:: PIL.TiffTags

:py:mod:`~PIL.TiffTags` module
==============================

The :py:mod:`~PIL.TiffTags` module exposes many of the standard TIFF
metadata tag numbers, names, and type information.

.. method:: lookup(tag)

    :param tag: Integer tag number
    :param group: Which :py:data:`~PIL.TiffTags.TAGS_V2_GROUPS` to look in

    .. versionadded:: 8.3.0

    :returns: Taginfo namedtuple, From the :py:data:`~PIL.TiffTags.TAGS_V2` info if possible,
        otherwise just populating the value and name from :py:data:`~PIL.TiffTags.TAGS`.
        If the tag is not recognized, "unknown" is returned for the name

.. versionadded:: 3.1.0

.. class:: TagInfo

  .. method:: __init__(self, value=None, name="unknown", type=None, length=0, enum=None)

     :param value: Integer Tag Number
     :param name: Tag Name
     :param type: Integer type from :py:data:`PIL.TiffTags.TYPES`
     :param length: Array length: 0 == variable, 1 == single value, n = fixed
     :param enum: Dict of name:integer value options for an enumeration

  .. method:: cvt_enum(self, value)

     :param value: The enumerated value name
     :returns: The integer corresponding to the name.

.. versionadded:: 3.0.0

.. py:data:: PIL.TiffTags.TAGS_V2
    :type: dict

    The ``TAGS_V2`` dictionary maps 16-bit integer tag numbers to
    :py:class:`PIL.TiffTags.TagInfo` tuples for metadata fields defined in the TIFF
    spec.

.. versionadded:: 3.0.0

.. py:data:: PIL.TiffTags.TAGS_V2_GROUPS
    :type: dict

    :py:data:`~PIL.TiffTags.TAGS_V2` is one dimensional and
    doesn't account for the fact that tags actually exist in
    `different groups <https://exiftool.org/TagNames/EXIF.html>`_.
    This dictionary is used when the tag in question is part of a group.

.. versionadded:: 8.3.0

.. py:data:: PIL.TiffTags.TAGS
    :type: dict

    The ``TAGS`` dictionary maps 16-bit integer TIFF tag number to
    descriptive string names.  For instance:

        >>> from PIL.TiffTags import TAGS
        >>> TAGS[0x010e]
        'ImageDescription'

    This dictionary contains a superset of the tags in :py:data:`~PIL.TiffTags.TAGS_V2`, common
    EXIF tags, and other well known metadata tags.

.. py:data:: PIL.TiffTags.TYPES
    :type: dict

    The ``TYPES`` dictionary maps the TIFF type short integer to a
    human readable type name.

.. py:data:: PIL.TiffTags.LIBTIFF_CORE
    :type: list

    A list of supported tag IDs when writing using LibTIFF.
