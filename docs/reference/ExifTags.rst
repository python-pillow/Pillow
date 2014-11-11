.. py:module:: PIL.ExifTags
.. py:currentmodule:: PIL.ExifTags

:py:mod:`ExifTags` Module
==========================

The :py:mod:`ExifTags` module exposes two dictionaries which
provide constants and clear-text names for various well-known EXIF tags.

.. py:class:: PIL.ExifTags.TAGS

    The TAG dictionary maps 16-bit integer EXIF tag enumerations to
    descriptive string names.  For instance:

        >>> from PIL.ExifTags import TAGS
        >>> TAGS[0x010e]
        'ImageDescription'

.. py:class:: PIL.ExifTags.GPSTAGS

    The GPSTAGS dictionary maps 8-bit integer EXIF gps enumerations to
    descriptive string names.  For instance:

        >>> from PIL.ExifTags import GPSTAGS
        >>> GPSTAGS[20]
        'GPSDestLatitude'
