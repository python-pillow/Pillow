.. py:module:: PIL.ExifTags
.. py:currentmodule:: PIL.ExifTags

:py:mod:`~PIL.ExifTags` module
==============================

The :py:mod:`~PIL.ExifTags` module exposes several :py:class:`enum.IntEnum`
classes which provide constants and clear-text names for various well-known
EXIF tags.

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

.. py:data:: Interop

    >>> from PIL.ExifTags import Interop
    >>> Interop.RelatedImageFileFormat.value
    4096
    >>> Interop(4096).name
    'RelatedImageFileFormat'

.. py:data:: IFD

    >>> from PIL.ExifTags import IFD
    >>> IFD.Exif.value
    34665
    >>> IFD(34665).name
    'Exif

.. py:data:: LightSource

    >>> from PIL.ExifTags import LightSource
    >>> LightSource.Unknown.value
    0
    >>> LightSource(0).name
    'Unknown'

Two of these values are also exposed as dictionaries.

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
