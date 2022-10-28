.. py:module:: PIL.ExifTags
.. py:currentmodule:: PIL.ExifTags

:py:mod:`~PIL.ExifTags` Module
==============================

The :py:mod:`~PIL.ExifTags` module exposes two dictionaries which
provide constants and clear-text names for various well-known EXIF tags.

.. py:data:: TAGS
    :type: dict

    The TAGS dictionary maps 16-bit integer EXIF tag enumerations to
    descriptive string names. For instance:

        >>> from PIL.ExifTags import TAGS
        >>> TAGS[0x010e]
        'ImageDescription'

.. py:data:: GPSTAGS
    :type: dict

    The GPSTAGS dictionary maps 8-bit integer EXIF GPS enumerations to
    descriptive string names. For instance:

        >>> from PIL.ExifTags import GPSTAGS
        >>> GPSTAGS[20]
        'GPSDestLatitude'


These values are also exposed as ``enum.IntEnum`` classes.

.. py:data:: Base

    >>> from PIL.ExifTags import Base
    >>> Base.ImageDescription.value
    270
    >>> Base(270).name
    'ImageDescription'

.. py:data:: GPS

    >>> from PIL.ExifTags import GPS
    >>> GPS.GPSDestLatitude.value
    20
    >>> GPS(20).name
    'GPSDestLatitude'
