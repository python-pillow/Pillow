.. py:module:: PIL.ExifTags
.. py:currentmodule:: PIL.ExifTags

:py:mod:`~PIL.ExifTags` Module
==============================

The :py:mod:`~PIL.ExifTags` module exposes four dictionaries which
provide constants and clear-text names for various well-known EXIF tags.

.. py:data:: TAGS
    :type: dict

    The TAGS dictionary maps 16-bit integer EXIF tag enumerations to
    descriptive string names. For instance:

        >>> from PIL.ExifTags import TAGS
        >>> TAGS[0x010e]
        'ImageDescription'

.. py:data:: TAG_CODES
    :type: dict

    The TAG_CODES dictionary maps descriptive string names to 16-bit integer EXIF
    tag enumerations. For instance:

        >>> from PIL.ExifTags import TAG_CODES
        >>> TAG_CODES['ImageDescription']
        0x010e

.. py:data:: GPSTAGS
    :type: dict

    The GPSTAGS dictionary maps 8-bit integer EXIF gps enumerations to
    descriptive string names. For instance:

        >>> from PIL.ExifTags import GPSTAGS
        >>> GPSTAGS[20]
        'GPSDestLatitude'

.. py:data:: GPS_CODES
    :type: dict

    The GPS_CODES dictionary maps descriptive string names to 8-bit integer EXIF
    gps enumerations. For instance:

        >>> from PIL.ExifTags import GPSTAGS
        >>> GPS_CODES['GPSDestLatitude']
        20
