#
# The Python Imaging Library.
# $Id$
#
# TIFF file handling
#
# TIFF is a flexible, if somewhat aged, image file format originally
# defined by Aldus.  Although TIFF supports a wide variety of pixel
# layouts and compression methods, the name doesn't really stand for
# "thousands of incompatible file formats," it just feels that way.
#
# To read TIFF data from a stream, the stream must be seekable.  For
# progressive decoding, make sure to use TIFF files where the tag
# directory is placed first in the file.
#
# History:
# 1995-09-01 fl   Created
# 1996-05-04 fl   Handle JPEGTABLES tag
# 1996-05-18 fl   Fixed COLORMAP support
# 1997-01-05 fl   Fixed PREDICTOR support
# 1997-08-27 fl   Added support for rational tags (from Perry Stoll)
# 1998-01-10 fl   Fixed seek/tell (from Jan Blom)
# 1998-07-15 fl   Use private names for internal variables
# 1999-06-13 fl   Rewritten for PIL 1.0 (1.0)
# 2000-10-11 fl   Additional fixes for Python 2.0 (1.1)
# 2001-04-17 fl   Fixed rewind support (seek to frame 0) (1.2)
# 2001-05-12 fl   Added write support for more tags (from Greg Couch) (1.3)
# 2001-12-18 fl   Added workaround for broken Matrox library
# 2002-01-18 fl   Don't mess up if photometric tag is missing (D. Alan Stewart)
# 2003-05-19 fl   Check FILLORDER tag
# 2003-09-26 fl   Added RGBa support
# 2004-02-24 fl   Added DPI support; fixed rational write support
# 2005-02-07 fl   Added workaround for broken Corel Draw 10 files
# 2006-01-09 fl   Added support for float/double tags (from Russell Nelson)
#
# Copyright (c) 1997-2006 by Secret Labs AB.  All rights reserved.
# Copyright (c) 1995-1997 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

from __future__ import division, print_function

from PIL import Image, ImageFile
from PIL import ImagePalette
from PIL import _binary

import collections
from fractions import Fraction
import io
import itertools
from numbers import Number
import os
import struct
import sys
import warnings

from .TiffTags import TAGS_V2, TYPES, TagInfo

__version__ = "1.3.5"
DEBUG = False  # Needs to be merged with the new logging approach.

# Set these to true to force use of libtiff for reading or writing.
READ_LIBTIFF = False
WRITE_LIBTIFF = False
IFD_LEGACY_API = True

II = b"II"  # little-endian (Intel style)
MM = b"MM"  # big-endian (Motorola style)

i8 = _binary.i8
o8 = _binary.o8

#
# --------------------------------------------------------------------
# Read TIFF files

# a few tag names, just to make the code below a bit more readable
IMAGEWIDTH = 256
IMAGELENGTH = 257
BITSPERSAMPLE = 258
COMPRESSION = 259
PHOTOMETRIC_INTERPRETATION = 262
FILLORDER = 266
IMAGEDESCRIPTION = 270
STRIPOFFSETS = 273
SAMPLESPERPIXEL = 277
ROWSPERSTRIP = 278
STRIPBYTECOUNTS = 279
X_RESOLUTION = 282
Y_RESOLUTION = 283
PLANAR_CONFIGURATION = 284
RESOLUTION_UNIT = 296
SOFTWARE = 305
DATE_TIME = 306
ARTIST = 315
PREDICTOR = 317
COLORMAP = 320
TILEOFFSETS = 324
EXTRASAMPLES = 338
SAMPLEFORMAT = 339
JPEGTABLES = 347
COPYRIGHT = 33432
IPTC_NAA_CHUNK = 33723  # newsphoto properties
PHOTOSHOP_CHUNK = 34377  # photoshop properties
ICCPROFILE = 34675
EXIFIFD = 34665
XMP = 700

# https://github.com/imagej/ImageJA/blob/master/src/main/java/ij/io/TiffDecoder.java
IMAGEJ_META_DATA_BYTE_COUNTS = 50838
IMAGEJ_META_DATA = 50839

COMPRESSION_INFO = {
    # Compression => pil compression name
    1: "raw",
    2: "tiff_ccitt",
    3: "group3",
    4: "group4",
    5: "tiff_lzw",
    6: "tiff_jpeg",  # obsolete
    7: "jpeg",
    8: "tiff_adobe_deflate",
    32771: "tiff_raw_16",  # 16-bit padding
    32773: "packbits",
    32809: "tiff_thunderscan",
    32946: "tiff_deflate",
    34676: "tiff_sgilog",
    34677: "tiff_sgilog24",
}

COMPRESSION_INFO_REV = dict([(v, k) for (k, v) in COMPRESSION_INFO.items()])

OPEN_INFO = {
    # (ByteOrder, PhotoInterpretation, SampleFormat, FillOrder, BitsPerSample,
    #  ExtraSamples) => mode, rawmode
    (II, 0, (1,), 1, (1,), ()): ("1", "1;I"),
    (MM, 0, (1,), 1, (1,), ()): ("1", "1;I"),
    (II, 0, (1,), 2, (1,), ()): ("1", "1;IR"),
    (MM, 0, (1,), 2, (1,), ()): ("1", "1;IR"),
    (II, 0, (1,), 1, (8,), ()): ("L", "L;I"),
    (MM, 0, (1,), 1, (8,), ()): ("L", "L;I"),
    (II, 0, (1,), 2, (8,), ()): ("L", "L;IR"),
    (MM, 0, (1,), 2, (8,), ()): ("L", "L;IR"),
    (II, 0, (3,), 1, (32,), ()): ("F", "F;32F"),
    (MM, 0, (3,), 1, (32,), ()): ("F", "F;32BF"),
    (II, 1, (1,), 1, (1,), ()): ("1", "1"),
    (MM, 1, (1,), 1, (1,), ()): ("1", "1"),
    (II, 1, (1,), 1, (4,), ()): ("L", "L;4"),
    # ?
    (II, 1, (1,), 2, (1,), ()): ("1", "1;R"),
    (MM, 1, (1,), 2, (1,), ()): ("1", "1;R"),
    (II, 1, (1,), 1, (8,), ()): ("L", "L"),
    (MM, 1, (1,), 1, (8,), ()): ("L", "L"),
    (II, 1, (1,), 1, (8, 8), (2,)): ("LA", "LA"),
    (MM, 1, (1,), 1, (8, 8), (2,)): ("LA", "LA"),
    (II, 1, (1,), 2, (8,), ()): ("L", "L;R"),
    (MM, 1, (1,), 2, (8,), ()): ("L", "L;R"),
    (II, 1, (1,), 1, (12,), ()): ("I;16", "I;12"),
    (II, 1, (1,), 1, (16,), ()): ("I;16", "I;16"),
    (MM, 1, (1,), 1, (16,), ()): ("I;16B", "I;16B"),
    (II, 1, (2,), 1, (16,), ()): ("I;16S", "I;16S"),
    (MM, 1, (2,), 1, (16,), ()): ("I;16BS", "I;16BS"),
    (II, 1, (1,), 1, (32,), ()): ("I", "I;32N"),
    (II, 1, (2,), 1, (32,), ()): ("I", "I;32S"),
    (MM, 1, (2,), 1, (32,), ()): ("I;32BS", "I;32BS"),
    (II, 1, (3,), 1, (32,), ()): ("F", "F;32F"),
    (MM, 1, (3,), 1, (32,), ()): ("F", "F;32BF"),
    (II, 2, (1,), 1, (8, 8, 8), ()): ("RGB", "RGB"),
    (MM, 2, (1,), 1, (8, 8, 8), ()): ("RGB", "RGB"),
    (II, 2, (1,), 2, (8, 8, 8), ()): ("RGB", "RGB;R"),
    (MM, 2, (1,), 2, (8, 8, 8), ()): ("RGB", "RGB;R"),
    (II, 2, (1,), 1, (8, 8, 8, 8), ()): ("RGBA", "RGBA"),  # missing ExtraSamples
    (MM, 2, (1,), 1, (8, 8, 8, 8), ()): ("RGBA", "RGBA"),  # missing ExtraSamples
    (II, 2, (1,), 1, (8, 8, 8, 8), (0,)): ("RGBX", "RGBX"),
    (MM, 2, (1,), 1, (8, 8, 8, 8), (0,)): ("RGBX", "RGBX"),
    (II, 2, (1,), 1, (8, 8, 8, 8), (1,)): ("RGBA", "RGBa"),
    (MM, 2, (1,), 1, (8, 8, 8, 8), (1,)): ("RGBA", "RGBa"),
    (II, 2, (1,), 1, (8, 8, 8, 8), (2,)): ("RGBA", "RGBA"),
    (MM, 2, (1,), 1, (8, 8, 8, 8), (2,)): ("RGBA", "RGBA"),
    (II, 2, (1,), 1, (8, 8, 8, 8), (999,)): ("RGBA", "RGBA"),  # Corel Draw 10
    (MM, 2, (1,), 1, (8, 8, 8, 8), (999,)): ("RGBA", "RGBA"),  # Corel Draw 10
    (II, 2, (1, 1, 1, 1), 1, (8, 8, 8, 8), (1,)): ("RGBA", "RGBA"),  # OSX Grab
    (MM, 2, (1, 1, 1, 1), 1, (8, 8, 8, 8), (1,)): ("RGBA", "RGBA"),  # OSX Grab
    (II, 3, (1,), 1, (1,), ()): ("P", "P;1"),
    (MM, 3, (1,), 1, (1,), ()): ("P", "P;1"),
    (II, 3, (1,), 2, (1,), ()): ("P", "P;1R"),
    (MM, 3, (1,), 2, (1,), ()): ("P", "P;1R"),
    (II, 3, (1,), 1, (2,), ()): ("P", "P;2"),
    (MM, 3, (1,), 1, (2,), ()): ("P", "P;2"),
    (II, 3, (1,), 2, (2,), ()): ("P", "P;2R"),
    (MM, 3, (1,), 2, (2,), ()): ("P", "P;2R"),
    (II, 3, (1,), 1, (4,), ()): ("P", "P;4"),
    (MM, 3, (1,), 1, (4,), ()): ("P", "P;4"),
    (II, 3, (1,), 2, (4,), ()): ("P", "P;4R"),
    (MM, 3, (1,), 2, (4,), ()): ("P", "P;4R"),
    (II, 3, (1,), 1, (8,), ()): ("P", "P"),
    (MM, 3, (1,), 1, (8,), ()): ("P", "P"),
    (II, 3, (1,), 1, (8, 8), (2,)): ("PA", "PA"),
    (MM, 3, (1,), 1, (8, 8), (2,)): ("PA", "PA"),
    (II, 3, (1,), 2, (8,), ()): ("P", "P;R"),
    (MM, 3, (1,), 2, (8,), ()): ("P", "P;R"),
    (II, 5, (1,), 1, (8, 8, 8, 8), ()): ("CMYK", "CMYK"),
    (MM, 5, (1,), 1, (8, 8, 8, 8), ()): ("CMYK", "CMYK"),
    (II, 6, (1,), 1, (8, 8, 8), ()): ("YCbCr", "YCbCr"),
    (MM, 6, (1,), 1, (8, 8, 8), ()): ("YCbCr", "YCbCr"),
    (II, 8, (1,), 1, (8, 8, 8), ()): ("LAB", "LAB"),
    (MM, 8, (1,), 1, (8, 8, 8), ()): ("LAB", "LAB"),
}

PREFIXES = [b"MM\000\052", b"II\052\000", b"II\xBC\000"]


def _accept(prefix):
    return prefix[:4] in PREFIXES


def _limit_rational(val, max_val):
    inv = abs(val) > 1
    f = Fraction.from_float(1 / val if inv else val).limit_denominator(max_val)
    n_d = (f.numerator, f.denominator)
    return n_d[::-1] if inv else n_d

##
# Wrapper for TIFF IFDs.

_load_dispatch = {}
_write_dispatch = {}


class ImageFileDirectory_v2(collections.MutableMapping):
    """This class represents a TIFF tag directory.  To speed things up, we
    don't decode tags unless they're asked for.

    Exposes a dictionary interface of the tags in the directory::

        ifd = ImageFileDirectory_v2()
        ifd[key] = 'Some Data'
        ifd.tagtype[key] = 2
        print(ifd[key])
        'Some Data'

    Individual values are returned as the strings or numbers, sequences are
    returned as tuples of the values.

    The tiff metadata type of each item is stored in a dictionary of
    tag types in
    `~PIL.TiffImagePlugin.ImageFileDirectory_v2.tagtype`. The types
    are read from a tiff file, guessed from the type added, or added
    manually.

    Data Structures:

        * self.tagtype = {}

          * Key: numerical tiff tag number
          * Value: integer corresponding to the data type from `~PIL.TiffTags.TYPES`

    .. versionadded:: 3.0.0
    """
    """
    Documentation:

        'internal' data structures:
        * self._tags_v2 = {} Key: numerical tiff tag number
                             Value: decoded data, as tuple for multiple values
        * self._tagdata = {} Key: numerical tiff tag number
                             Value: undecoded byte string from file
        * self._tags_v1 = {} Key: numerical tiff tag number
                             Value: decoded data in the v1 format

    Tags will be found in the private attributes self._tagdata, and in
    self._tags_v2 once decoded.

    Self.legacy_api is a value for internal use, and shouldn't be
    changed from outside code. In cooperation with the
    ImageFileDirectory_v1 class, if legacy_api is true, then decoded
    tags will be populated into both _tags_v1 and _tags_v2. _Tags_v2
    will be used if this IFD is used in the TIFF save routine. Tags
    should be read from tags_v1 if legacy_api == true.

    """

    def __init__(self, ifh=b"II\052\0\0\0\0\0", prefix=None):
        """Initialize an ImageFileDirectory.

        To construct an ImageFileDirectory from a real file, pass the 8-byte
        magic header to the constructor.  To only set the endianness, pass it
        as the 'prefix' keyword argument.

        :param ifh: One of the accepted magic headers (cf. PREFIXES); also sets
              endianness.
        :param prefix: Override the endianness of the file.
        """
        if ifh[:4] not in PREFIXES:
            raise SyntaxError("not a TIFF file (header %r not valid)" % ifh)
        self._prefix = prefix if prefix is not None else ifh[:2]
        if self._prefix == MM:
            self._endian = ">"
        elif self._prefix == II:
            self._endian = "<"
        else:
            raise SyntaxError("not a TIFF IFD")
        self.reset()
        self.next, = self._unpack("L", ifh[4:])
        self._legacy_api = False

    prefix = property(lambda self: self._prefix)
    offset = property(lambda self: self._offset)
    legacy_api = property(lambda self: self._legacy_api)

    @legacy_api.setter
    def legacy_api(self, value):
        raise Exception("Not allowing setting of legacy api")

    def reset(self):
        self._tags_v1 = {}  # will remain empty if legacy_api is false
        self._tags_v2 = {}  # main tag storage
        self._tagdata = {}
        self.tagtype = {}   # added 2008-06-05 by Florian Hoech
        self._next = None
        self._offset = None

    def __str__(self):
        return str(dict(self))

    def as_dict(self):
        """Return a dictionary of the image's tags.

        use `dict(ifd)` instead.

        .. deprecated:: 3.0.0
        """
        # FIXME Deprecate: use dict(self)
        return dict(self)

    def named(self):
        """
        :returns: dict of name|key: value

        Returns the complete tag dictionary, with named tags where possible.
        """
        return dict((TAGS_V2.get(code, TagInfo()).name, value)
                    for code, value in self.items())

    def __len__(self):
        return len(set(self._tagdata) | set(self._tags_v2))

    def __getitem__(self, tag):
        if tag not in self._tags_v2:  # unpack on the fly
            data = self._tagdata[tag]
            typ = self.tagtype[tag]
            size, handler = self._load_dispatch[typ]
            self[tag] = handler(self, data, self.legacy_api)  # check type
        val = self._tags_v2[tag]
        if self.legacy_api and not isinstance(val, (tuple, bytes)):
            val = val,
        return val

    def __contains__(self, tag):
        return tag in self._tags_v2 or tag in self._tagdata

    if bytes is str:
        def has_key(self, tag):
            return tag in self

    def __setitem__(self, tag, value):
        self._setitem(tag, value, self.legacy_api)

    def _setitem(self, tag, value, legacy_api):
        basetypes = (Number, bytes, str)
        if bytes is str:
            basetypes += unicode,

        info = TAGS_V2.get(tag, TagInfo())
        values = [value] if isinstance(value, basetypes) else value

        if tag not in self.tagtype:
            try:
                self.tagtype[tag] = info.type
            except KeyError:
                self.tagtype[tag] = 7
                if all(isinstance(v, int) for v in values):
                    if all(v < 2 ** 16 for v in values):
                        self.tagtype[tag] = 3
                    else:
                        self.tagtype[tag] = 4
                elif all(isinstance(v, float) for v in values):
                    self.tagtype[tag] = 12
                else:
                    if bytes is str:
                        # Never treat data as binary by default on Python 2.
                        self.tagtype[tag] = 2
                    else:
                        if all(isinstance(v, str) for v in values):
                            self.tagtype[tag] = 2

        if self.tagtype[tag] == 7 and bytes is not str:
            values = [value.encode("ascii", 'replace') if isinstance(value, str) else value
                      for value in values]

        values = tuple(info.cvt_enum(value) for value in values)

        dest = self._tags_v1 if legacy_api else self._tags_v2

        if info.length == 1:
            if legacy_api and self.tagtype[tag] in [5, 10]:
                values = values,
            dest[tag], = values
        else:
            dest[tag] = values

    def __delitem__(self, tag):
        self._tags_v2.pop(tag, None)
        self._tags_v1.pop(tag, None)
        self._tagdata.pop(tag, None)

    def __iter__(self):
        return iter(set(self._tagdata) | set(self._tags_v2))

    def _unpack(self, fmt, data):
        return struct.unpack(self._endian + fmt, data)

    def _pack(self, fmt, *values):
        return struct.pack(self._endian + fmt, *values)

    def _register_loader(idx, size):
        def decorator(func):
            from PIL.TiffTags import TYPES
            if func.__name__.startswith("load_"):
                TYPES[idx] = func.__name__[5:].replace("_", " ")
            _load_dispatch[idx] = size, func
            return func
        return decorator

    def _register_writer(idx):
        def decorator(func):
            _write_dispatch[idx] = func
            return func
        return decorator

    def _register_basic(idx_fmt_name):
        from PIL.TiffTags import TYPES
        idx, fmt, name = idx_fmt_name
        TYPES[idx] = name
        size = struct.calcsize("=" + fmt)
        _load_dispatch[idx] = size, lambda self, data, legacy_api=True: (
            self._unpack("{0}{1}".format(len(data) // size, fmt), data))
        _write_dispatch[idx] = lambda self, *values: (
            b"".join(self._pack(fmt, value) for value in values))

    list(map(_register_basic,
             [(3, "H", "short"), (4, "L", "long"),
              (6, "b", "signed byte"), (8, "h", "signed short"),
              (9, "l", "signed long"), (11, "f", "float"), (12, "d", "double")]))

    @_register_loader(1, 1)  # Basic type, except for the legacy API.
    def load_byte(self, data, legacy_api=True):
        return (data if legacy_api else
                tuple(map(ord, data) if bytes is str else data))

    @_register_writer(1)  # Basic type, except for the legacy API.
    def write_byte(self, data):
        return data

    @_register_loader(2, 1)
    def load_string(self, data, legacy_api=True):
        if data.endswith(b"\0"):
            data = data[:-1]
        return data.decode("latin-1", "replace")

    @_register_writer(2)
    def write_string(self, value):
        # remerge of https://github.com/python-pillow/Pillow/pull/1416
        if sys.version_info[0] == 2:
            value = value.decode('ascii', 'replace')
        return b"" + value.encode('ascii', 'replace') + b"\0"

    @_register_loader(5, 8)
    def load_rational(self, data, legacy_api=True):
        vals = self._unpack("{0}L".format(len(data) // 4), data)
        combine = lambda a, b: (a, b) if legacy_api else a / b
        return tuple(combine(num, denom)
                     for num, denom in zip(vals[::2], vals[1::2]))

    @_register_writer(5)
    def write_rational(self, *values):
        return b"".join(self._pack("2L", *_limit_rational(frac, 2 ** 31))
                        for frac in values)

    @_register_loader(7, 1)
    def load_undefined(self, data, legacy_api=True):
        return data

    @_register_writer(7)
    def write_undefined(self, value):
        return value

    @_register_loader(10, 8)
    def load_signed_rational(self, data, legacy_api=True):
        vals = self._unpack("{0}l".format(len(data) // 4), data)
        combine = lambda a, b: (a, b) if legacy_api else a / b
        return tuple(combine(num, denom)
                     for num, denom in zip(vals[::2], vals[1::2]))

    @_register_writer(10)
    def write_signed_rational(self, *values):
        return b"".join(self._pack("2L", *_limit_rational(frac, 2 ** 30))
                        for frac in values)

    def _ensure_read(self, fp, size):
        ret = fp.read(size)
        if len(ret) != size:
            raise IOError("Corrupt EXIF data.  " +
                          "Expecting to read %d bytes but only got %d. " %
                          (size, len(ret)))
        return ret

    def load(self, fp):

        self.reset()
        self._offset = fp.tell()

        try:
            for i in range(self._unpack("H", self._ensure_read(fp, 2))[0]):
                tag, typ, count, data = self._unpack("HHL4s", self._ensure_read(fp, 12))
                if DEBUG:
                    tagname = TAGS_V2.get(tag, TagInfo()).name
                    typname = TYPES.get(typ, "unknown")
                    print("tag: %s (%d) - type: %s (%d)" %
                          (tagname, tag, typname, typ), end=" ")

                try:
                    unit_size, handler = self._load_dispatch[typ]
                except KeyError:
                    if DEBUG:
                        print("- unsupported type", typ)
                    continue  # ignore unsupported type
                size = count * unit_size
                if size > 4:
                    here = fp.tell()
                    offset, = self._unpack("L", data)
                    if DEBUG:
                        print("Tag Location: %s - Data Location: %s" %
                              (here, offset), end=" ")
                    fp.seek(offset)
                    data = ImageFile._safe_read(fp, size)
                    fp.seek(here)
                else:
                    data = data[:size]

                if len(data) != size:
                    warnings.warn("Possibly corrupt EXIF data.  "
                                  "Expecting to read %d bytes but only got %d. "
                                  "Skipping tag %s" % (size, len(data), tag))
                    continue

                self._tagdata[tag] = data
                self.tagtype[tag] = typ

                if DEBUG:
                    if size > 32:
                        print("- value: <table: %d bytes>" % size)
                    else:
                        print("- value:", self[tag])

            self.next, = self._unpack("L", self._ensure_read(fp, 4))
        except IOError as msg:
            warnings.warn(str(msg))
            return

    def save(self, fp):

        if fp.tell() == 0:  # skip TIFF header on subsequent pages
            # tiff header -- PIL always starts the first IFD at offset 8
            fp.write(self._prefix + self._pack("HL", 42, 8))

        # FIXME What about tagdata?
        fp.write(self._pack("H", len(self._tags_v2)))

        entries = []
        offset = fp.tell() + len(self._tags_v2) * 12 + 4
        stripoffsets = None

        # pass 1: convert tags to binary format
        # always write tags in ascending order
        for tag, value in sorted(self._tags_v2.items()):
            if tag == STRIPOFFSETS:
                stripoffsets = len(entries)
            typ = self.tagtype.get(tag)
            if DEBUG:
                print("Tag %s, Type: %s, Value: %s" % (tag, typ, value))
            values = value if isinstance(value, tuple) else (value,)
            data = self._write_dispatch[typ](self, *values)
            if DEBUG:
                tagname = TAGS_V2.get(tag, TagInfo()).name
                typname = TYPES.get(typ, "unknown")
                print("save: %s (%d) - type: %s (%d)" %
                      (tagname, tag, typname, typ), end=" ")
                if len(data) >= 16:
                    print("- value: <table: %d bytes>" % len(data))
                else:
                    print("- value:", values)

            # count is sum of lengths for string and arbitrary data
            count = len(data) if typ in [2, 7] else len(values)
            # figure out if data fits into the entry
            if len(data) <= 4:
                entries.append((tag, typ, count, data.ljust(4, b"\0"), b""))
            else:
                entries.append((tag, typ, count, self._pack("L", offset), data))
                offset += (len(data) + 1) // 2 * 2  # pad to word

        # update strip offset data to point beyond auxiliary data
        if stripoffsets is not None:
            tag, typ, count, value, data = entries[stripoffsets]
            if data:
                raise NotImplementedError(
                    "multistrip support not yet implemented")
            value = self._pack("L", self._unpack("L", value)[0] + offset)
            entries[stripoffsets] = tag, typ, count, value, data

        # pass 2: write entries to file
        for tag, typ, count, value, data in entries:
            if DEBUG > 1:
                print(tag, typ, count, repr(value), repr(data))
            fp.write(self._pack("HHL4s", tag, typ, count, value))

        # -- overwrite here for multi-page --
        fp.write(b"\0\0\0\0")  # end of entries

        # pass 3: write auxiliary data to file
        for tag, typ, count, value, data in entries:
            fp.write(data)
            if len(data) & 1:
                fp.write(b"\0")

        return offset

ImageFileDirectory_v2._load_dispatch = _load_dispatch
ImageFileDirectory_v2._write_dispatch = _write_dispatch
for idx, name in TYPES.items():
    name = name.replace(" ", "_")
    setattr(ImageFileDirectory_v2, "load_" + name, _load_dispatch[idx][1])
    setattr(ImageFileDirectory_v2, "write_" + name, _write_dispatch[idx])
del _load_dispatch, _write_dispatch, idx, name


# Legacy ImageFileDirectory support.
class ImageFileDirectory_v1(ImageFileDirectory_v2):
    """This class represents the **legacy** interface to a TIFF tag directory.

    Exposes a dictionary interface of the tags in the directory::

        ifd = ImageFileDirectory_v1()
        ifd[key] = 'Some Data'
        ifd.tagtype[key] = 2
        print ifd[key]
        ('Some Data',)

    Also contains a dictionary of tag types as read from the tiff image file,
    `~PIL.TiffImagePlugin.ImageFileDirectory_v1.tagtype`.

    Values are returned as a tuple.

    ..  deprecated:: 3.0.0
    """
    def __init__(self, *args, **kwargs):
        ImageFileDirectory_v2.__init__(self, *args, **kwargs)
        self._legacy_api = True

    tags = property(lambda self: self._tags_v1)
    tagdata = property(lambda self: self._tagdata)

    @classmethod
    def from_v2(cls, original):
        """ Returns an
        :py:class:`~PIL.TiffImagePlugin.ImageFileDirectory_v1`
        instance with the same data as is contained in the original
        :py:class:`~PIL.TiffImagePlugin.ImageFileDirectory_v2`
        instance.

        :returns: :py:class:`~PIL.TiffImagePlugin.ImageFileDirectory_v1`

        """

        ifd = cls(prefix=original.prefix)
        ifd._tagdata = original._tagdata
        ifd.tagtype = original.tagtype
        ifd.next = original.next  # an indicator for multipage tiffs
        return ifd

    def to_v2(self):
        """ Returns an
        :py:class:`~PIL.TiffImagePlugin.ImageFileDirectory_v2`
        instance with the same data as is contained in the original
        :py:class:`~PIL.TiffImagePlugin.ImageFileDirectory_v1`
        instance.

        :returns: :py:class:`~PIL.TiffImagePlugin.ImageFileDirectory_v2`

        """

        ifd = ImageFileDirectory_v2(prefix=self.prefix)
        ifd._tagdata = dict(self._tagdata)
        ifd.tagtype = dict(self.tagtype)
        ifd._tags_v2 = dict(self._tags_v2)
        return ifd

    def __contains__(self, tag):
        return tag in self._tags_v1 or tag in self._tagdata

    def __len__(self):
        return len(set(self._tagdata) | set(self._tags_v1))

    def __iter__(self):
        return iter(set(self._tagdata) | set(self._tags_v1))

    def __setitem__(self, tag, value):
        for legacy_api in (False, True):
            self._setitem(tag, value, legacy_api)

    def __getitem__(self, tag):
        if tag not in self._tags_v1:  # unpack on the fly
            data = self._tagdata[tag]
            typ = self.tagtype[tag]
            size, handler = self._load_dispatch[typ]
            for legacy in (False, True):
                self._setitem(tag, handler(self, data, legacy), legacy)
        val = self._tags_v1[tag]
        if not isinstance(val, (tuple, bytes)):
            val = val,
        return val


# undone -- switch this pointer when IFD_LEGACY_API == False
ImageFileDirectory = ImageFileDirectory_v1


##
# Image plugin for TIFF files.

class TiffImageFile(ImageFile.ImageFile):

    format = "TIFF"
    format_description = "Adobe TIFF"

    def _open(self):
        "Open the first image in a TIFF file"

        # Header
        ifh = self.fp.read(8)

        # image file directory (tag dictionary)
        self.tag_v2 = ImageFileDirectory_v2(ifh)

        # legacy tag/ifd entries will be filled in later
        self.tag = self.ifd = None

        # setup frame pointers
        self.__first = self.__next = self.tag_v2.next
        self.__frame = -1
        self.__fp = self.fp
        self._frame_pos = []
        self._n_frames = None
        self._is_animated = None

        if DEBUG:
            print("*** TiffImageFile._open ***")
            print("- __first:", self.__first)
            print("- ifh: ", ifh)

        # and load the first frame
        self._seek(0)

    @property
    def n_frames(self):
        if self._n_frames is None:
            current = self.tell()
            try:
                while True:
                    self._seek(self.tell() + 1)
            except EOFError:
                self._n_frames = self.tell() + 1
            self.seek(current)
        return self._n_frames

    @property
    def is_animated(self):
        if self._is_animated is None:
            current = self.tell()

            try:
                self.seek(1)
                self._is_animated = True
            except EOFError:
                self._is_animated = False

            self.seek(current)
        return self._is_animated

    def seek(self, frame):
        "Select a given frame as current image"
        self._seek(max(frame, 0))  # Questionable backwards compatibility.
        # Create a new core image object on second and
        # subsequent frames in the image. Image may be
        # different size/mode.
        Image._decompression_bomb_check(self.size)
        self.im = Image.core.new(self.mode, self.size)

    def _seek(self, frame):
        self.fp = self.__fp
        while len(self._frame_pos) <= frame:
            if not self.__next:
                raise EOFError("no more images in TIFF file")
            if DEBUG:
                print("Seeking to frame %s, on frame %s, "
                      "__next %s, location: %s" %
                      (frame, self.__frame, self.__next, self.fp.tell()))
            # reset python3 buffered io handle in case fp
            # was passed to libtiff, invalidating the buffer
            self.fp.tell()
            self.fp.seek(self.__next)
            self._frame_pos.append(self.__next)
            if DEBUG:
                print("Loading tags, location: %s" % self.fp.tell())
            self.tag_v2.load(self.fp)
            self.__next = self.tag_v2.next
            self.__frame += 1
        self.fp.seek(self._frame_pos[frame])
        self.tag_v2.load(self.fp)
        # fill the legacy tag/ifd entries
        self.tag = self.ifd = ImageFileDirectory_v1.from_v2(self.tag_v2)
        self.__frame = frame
        self._setup()

    def tell(self):
        "Return the current frame number"
        return self.__frame

    def _decoder(self, rawmode, layer, tile=None):
        "Setup decoder contexts"

        args = None
        if rawmode == "RGB" and self._planar_configuration == 2:
            rawmode = rawmode[layer]
        compression = self._compression
        if compression == "raw":
            args = (rawmode, 0, 1)
        elif compression == "jpeg":
            args = rawmode, ""
            if JPEGTABLES in self.tag_v2:
                # Hack to handle abbreviated JPEG headers
                # FIXME This will fail with more than one value
                self.tile_prefix, = self.tag_v2[JPEGTABLES]
        elif compression == "packbits":
            args = rawmode
        elif compression == "tiff_lzw":
            args = rawmode
            if PREDICTOR in self.tag_v2:
                # Section 14: Differencing Predictor
                self.decoderconfig = (self.tag_v2[PREDICTOR],)

        if ICCPROFILE in self.tag_v2:
            self.info['icc_profile'] = self.tag_v2[ICCPROFILE]

        return args

    def _load_libtiff(self):
        """ Overload method triggered when we detect a compressed tiff
            Calls out to libtiff """

        pixel = Image.Image.load(self)

        if self.tile is None:
            raise IOError("cannot load this image")
        if not self.tile:
            return pixel

        self.load_prepare()

        if not len(self.tile) == 1:
            raise IOError("Not exactly one tile")

        # (self._compression, (extents tuple),
        #   0, (rawmode, self._compression, fp))
        extents = self.tile[0][1]
        args = self.tile[0][3] + (self.tag_v2.offset,)
        decoder = Image._getdecoder(self.mode, 'libtiff', args,
                                    self.decoderconfig)
        try:
            decoder.setimage(self.im, extents)
        except ValueError:
            raise IOError("Couldn't set the image")

        if hasattr(self.fp, "getvalue"):
            # We've got a stringio like thing passed in. Yay for all in memory.
            # The decoder needs the entire file in one shot, so there's not
            # a lot we can do here other than give it the entire file.
            # unless we could do something like get the address of the
            # underlying string for stringio.
            #
            # Rearranging for supporting byteio items, since they have a fileno
            # that returns an IOError if there's no underlying fp. Easier to
            # deal with here by reordering.
            if DEBUG:
                print("have getvalue. just sending in a string from getvalue")
            n, err = decoder.decode(self.fp.getvalue())
        elif hasattr(self.fp, "fileno"):
            # we've got a actual file on disk, pass in the fp.
            if DEBUG:
                print("have fileno, calling fileno version of the decoder.")
            self.fp.seek(0)
            # 4 bytes, otherwise the trace might error out
            n, err = decoder.decode(b"fpfp")
        else:
            # we have something else.
            if DEBUG:
                print("don't have fileno or getvalue. just reading")
            # UNDONE -- so much for that buffer size thing.
            n, err = decoder.decode(self.fp.read())

        self.tile = []
        self.readonly = 0
        # libtiff closed the fp in a, we need to close self.fp, if possible
        if hasattr(self.fp, 'close'):
            if not self.__next:
                self.fp.close()
        self.fp = None  # might be shared

        if err < 0:
            raise IOError(err)

        self.load_end()

        return Image.Image.load(self)

    def _setup(self):
        "Setup this image object based on current tags"

        if 0xBC01 in self.tag_v2:
            raise IOError("Windows Media Photo files not yet supported")

        # extract relevant tags
        self._compression = COMPRESSION_INFO[self.tag_v2.get(COMPRESSION, 1)]
        self._planar_configuration = self.tag_v2.get(PLANAR_CONFIGURATION, 1)

        # photometric is a required tag, but not everyone is reading
        # the specification
        photo = self.tag_v2.get(PHOTOMETRIC_INTERPRETATION, 0)

        fillorder = self.tag_v2.get(FILLORDER, 1)

        if DEBUG:
            print("*** Summary ***")
            print("- compression:", self._compression)
            print("- photometric_interpretation:", photo)
            print("- planar_configuration:", self._planar_configuration)
            print("- fill_order:", fillorder)

        # size
        xsize = self.tag_v2.get(IMAGEWIDTH)
        ysize = self.tag_v2.get(IMAGELENGTH)
        self.size = xsize, ysize

        if DEBUG:
            print("- size:", self.size)

        format = self.tag_v2.get(SAMPLEFORMAT, (1,))

        # mode: check photometric interpretation and bits per pixel
        key = (
            self.tag_v2.prefix, photo, format, fillorder,
            self.tag_v2.get(BITSPERSAMPLE, (1,)),
            self.tag_v2.get(EXTRASAMPLES, ())
            )
        if DEBUG:
            print("format key:", key)
        try:
            self.mode, rawmode = OPEN_INFO[key]
        except KeyError:
            if DEBUG:
                print("- unsupported format")
            raise SyntaxError("unknown pixel mode")

        if DEBUG:
            print("- raw mode:", rawmode)
            print("- pil mode:", self.mode)

        self.info["compression"] = self._compression

        xres = self.tag_v2.get(X_RESOLUTION, (1, 1))
        yres = self.tag_v2.get(Y_RESOLUTION, (1, 1))

        if xres and not isinstance(xres, tuple):
            xres = (xres, 1.)
        if yres and not isinstance(yres, tuple):
            yres = (yres, 1.)
        if xres and yres:
            xres = xres[0] / (xres[1] or 1)
            yres = yres[0] / (yres[1] or 1)
            resunit = self.tag_v2.get(RESOLUTION_UNIT, 1)
            if resunit == 2:  # dots per inch
                self.info["dpi"] = xres, yres
            elif resunit == 3:  # dots per centimeter. convert to dpi
                self.info["dpi"] = xres * 2.54, yres * 2.54
            else:  # No absolute unit of measurement
                self.info["resolution"] = xres, yres

        # build tile descriptors
        x = y = l = 0
        self.tile = []
        if STRIPOFFSETS in self.tag_v2:
            # striped image
            offsets = self.tag_v2[STRIPOFFSETS]
            h = self.tag_v2.get(ROWSPERSTRIP, ysize)
            w = self.size[0]
            if READ_LIBTIFF or self._compression in ["tiff_ccitt", "group3",
                                                     "group4", "tiff_jpeg",
                                                     "tiff_adobe_deflate",
                                                     "tiff_thunderscan",
                                                     "tiff_deflate",
                                                     "tiff_sgilog",
                                                     "tiff_sgilog24",
                                                     "tiff_raw_16"]:
                # if DEBUG:
                #     print "Activating g4 compression for whole file"

                # Decoder expects entire file as one tile.
                # There's a buffer size limit in load (64k)
                # so large g4 images will fail if we use that
                # function.
                #
                # Setup the one tile for the whole image, then
                # replace the existing load function with our
                # _load_libtiff function.

                self.load = self._load_libtiff

                # To be nice on memory footprint, if there's a
                # file descriptor, use that instead of reading
                # into a string in python.

                # libtiff closes the file descriptor, so pass in a dup.
                try:
                    fp = hasattr(self.fp, "fileno") and \
                        os.dup(self.fp.fileno())
                    # flush the file descriptor, prevents error on pypy 2.4+
                    # should also eliminate the need for fp.tell for py3
                    # in _seek
                    if hasattr(self.fp, "flush"):
                        self.fp.flush()
                except IOError:
                    # io.BytesIO have a fileno, but returns an IOError if
                    # it doesn't use a file descriptor.
                    fp = False

                # libtiff handles the fillmode for us, so 1;IR should
                # actually be 1;I. Including the R double reverses the
                # bits, so stripes of the image are reversed.  See
                # https://github.com/python-pillow/Pillow/issues/279
                if fillorder == 2:
                    key = (
                        self.tag_v2.prefix, photo, format, 1,
                        self.tag_v2.get(BITSPERSAMPLE, (1,)),
                        self.tag_v2.get(EXTRASAMPLES, ())
                        )
                    if DEBUG:
                        print("format key:", key)
                    # this should always work, since all the
                    # fillorder==2 modes have a corresponding
                    # fillorder=1 mode
                    self.mode, rawmode = OPEN_INFO[key]
                # libtiff always returns the bytes in native order.
                # we're expecting image byte order. So, if the rawmode
                # contains I;16, we need to convert from native to image
                # byte order.
                if self.mode in ('I;16B', 'I;16') and 'I;16' in rawmode:
                    rawmode = 'I;16N'

                # Offset in the tile tuple is 0, we go from 0,0 to
                # w,h, and we only do this once -- eds
                a = (rawmode, self._compression, fp)
                self.tile.append(
                    (self._compression,
                     (0, 0, w, ysize),
                     0, a))
                a = None

            else:
                for i in range(len(offsets)):
                    a = self._decoder(rawmode, l, i)
                    self.tile.append(
                        (self._compression,
                            (0, min(y, ysize), w, min(y+h, ysize)),
                            offsets[i], a))
                    if DEBUG:
                        print("tiles: ", self.tile)
                    y = y + h
                    if y >= self.size[1]:
                        x = y = 0
                        l += 1
                    a = None
        elif TILEOFFSETS in self.tag_v2:
            # tiled image
            w = self.tag_v2.get(322)
            h = self.tag_v2.get(323)
            a = None
            for o in self.tag_v2[TILEOFFSETS]:
                if not a:
                    a = self._decoder(rawmode, l)
                # FIXME: this doesn't work if the image size
                # is not a multiple of the tile size...
                self.tile.append(
                    (self._compression,
                        (x, y, x+w, y+h),
                        o, a))
                x = x + w
                if x >= self.size[0]:
                    x, y = 0, y + h
                    if y >= self.size[1]:
                        x = y = 0
                        l += 1
                        a = None
        else:
            if DEBUG:
                print("- unsupported data organization")
            raise SyntaxError("unknown data organization")

        # fixup palette descriptor

        if self.mode == "P":
            palette = [o8(b // 256) for b in self.tag_v2[COLORMAP]]
            self.palette = ImagePalette.raw("RGB;L", b"".join(palette))
#
# --------------------------------------------------------------------
# Write TIFF files

# little endian is default except for image modes with
# explicit big endian byte-order

SAVE_INFO = {
    # mode => rawmode, byteorder, photometrics,
    #           sampleformat, bitspersample, extra
    "1": ("1", II, 1, 1, (1,), None),
    "L": ("L", II, 1, 1, (8,), None),
    "LA": ("LA", II, 1, 1, (8, 8), 2),
    "P": ("P", II, 3, 1, (8,), None),
    "PA": ("PA", II, 3, 1, (8, 8), 2),
    "I": ("I;32S", II, 1, 2, (32,), None),
    "I;16": ("I;16", II, 1, 1, (16,), None),
    "I;16S": ("I;16S", II, 1, 2, (16,), None),
    "F": ("F;32F", II, 1, 3, (32,), None),
    "RGB": ("RGB", II, 2, 1, (8, 8, 8), None),
    "RGBX": ("RGBX", II, 2, 1, (8, 8, 8, 8), 0),
    "RGBA": ("RGBA", II, 2, 1, (8, 8, 8, 8), 2),
    "CMYK": ("CMYK", II, 5, 1, (8, 8, 8, 8), None),
    "YCbCr": ("YCbCr", II, 6, 1, (8, 8, 8), None),
    "LAB": ("LAB", II, 8, 1, (8, 8, 8), None),

    "I;32BS": ("I;32BS", MM, 1, 2, (32,), None),
    "I;16B": ("I;16B", MM, 1, 1, (16,), None),
    "I;16BS": ("I;16BS", MM, 1, 2, (16,), None),
    "F;32BF": ("F;32BF", MM, 1, 3, (32,), None),
}


def _save(im, fp, filename):

    try:
        rawmode, prefix, photo, format, bits, extra = SAVE_INFO[im.mode]
    except KeyError:
        raise IOError("cannot write mode %s as TIFF" % im.mode)

    ifd = ImageFileDirectory_v2(prefix=prefix)

    compression = im.encoderinfo.get('compression',
                                     im.info.get('compression', 'raw'))

    libtiff = WRITE_LIBTIFF or compression != 'raw'

    # required for color libtiff images
    ifd[PLANAR_CONFIGURATION] = getattr(im, '_planar_configuration', 1)

    ifd[IMAGEWIDTH] = im.size[0]
    ifd[IMAGELENGTH] = im.size[1]

    # write any arbitrary tags passed in as an ImageFileDirectory
    info = im.encoderinfo.get("tiffinfo", {})
    if DEBUG:
        print("Tiffinfo Keys: %s" % list(info))
    if isinstance(info, ImageFileDirectory_v1):
        info = info.to_v2()
    for key in info:
        ifd[key] = info.get(key)
        try:
            ifd.tagtype[key] = info.tagtype[key]
        except:
            pass  # might not be an IFD, Might not have populated type

    # additions written by Greg Couch, gregc@cgl.ucsf.edu
    # inspired by image-sig posting from Kevin Cazabon, kcazabon@home.com
    if hasattr(im, 'tag_v2'):
        # preserve tags from original TIFF image file
        for key in (RESOLUTION_UNIT, X_RESOLUTION, Y_RESOLUTION,
                    IPTC_NAA_CHUNK, PHOTOSHOP_CHUNK, XMP):
            if key in im.tag_v2:
                ifd[key] = im.tag_v2[key]
            ifd.tagtype[key] = im.tag_v2.tagtype.get(key, None)

        # preserve ICC profile (should also work when saving other formats
        # which support profiles as TIFF) -- 2008-06-06 Florian Hoech
        if "icc_profile" in im.info:
            ifd[ICCPROFILE] = im.info["icc_profile"]

    for key, name in [(IMAGEDESCRIPTION, "description"),
                      (X_RESOLUTION, "resolution"),
                      (Y_RESOLUTION, "resolution"),
                      (X_RESOLUTION, "x_resolution"),
                      (Y_RESOLUTION, "y_resolution"),
                      (RESOLUTION_UNIT, "resolution_unit"),
                      (SOFTWARE, "software"),
                      (DATE_TIME, "date_time"),
                      (ARTIST, "artist"),
                      (COPYRIGHT, "copyright")]:
        name_with_spaces = name.replace("_", " ")
        if "_" in name and name_with_spaces in im.encoderinfo:
            warnings.warn("%r is deprecated; use %r instead" %
                          (name_with_spaces, name), DeprecationWarning)
            ifd[key] = im.encoderinfo[name.replace("_", " ")]
        if name in im.encoderinfo:
            ifd[key] = im.encoderinfo[name]

    dpi = im.encoderinfo.get("dpi")
    if dpi:
        ifd[RESOLUTION_UNIT] = 2
        ifd[X_RESOLUTION] = dpi[0]
        ifd[Y_RESOLUTION] = dpi[1]

    if bits != (1,):
        ifd[BITSPERSAMPLE] = bits
        if len(bits) != 1:
            ifd[SAMPLESPERPIXEL] = len(bits)
    if extra is not None:
        ifd[EXTRASAMPLES] = extra
    if format != 1:
        ifd[SAMPLEFORMAT] = format

    ifd[PHOTOMETRIC_INTERPRETATION] = photo

    if im.mode == "P":
        lut = im.im.getpalette("RGB", "RGB;L")
        ifd[COLORMAP] = tuple(i8(v) * 256 for v in lut)

    # data orientation
    stride = len(bits) * ((im.size[0]*bits[0]+7)//8)
    ifd[ROWSPERSTRIP] = im.size[1]
    ifd[STRIPBYTECOUNTS] = stride * im.size[1]
    ifd[STRIPOFFSETS] = 0  # this is adjusted by IFD writer
    # no compression by default:
    ifd[COMPRESSION] = COMPRESSION_INFO_REV.get(compression, 1)

    if libtiff:
        if DEBUG:
            print("Saving using libtiff encoder")
            print("Items: %s" % sorted(ifd.items()))
        _fp = 0
        if hasattr(fp, "fileno"):
            try:
                fp.seek(0)
                _fp = os.dup(fp.fileno())
            except io.UnsupportedOperation:
                pass

        # ICC Profile crashes.
        blocklist = [STRIPOFFSETS, STRIPBYTECOUNTS, ROWSPERSTRIP, ICCPROFILE]
        atts = {}
        # bits per sample is a single short in the tiff directory, not a list.
        atts[BITSPERSAMPLE] = bits[0]
        # Merge the ones that we have with (optional) more bits from
        # the original file, e.g x,y resolution so that we can
        # save(load('')) == original file.
        legacy_ifd = {}
        if hasattr(im, 'tag'):
            legacy_ifd = im.tag.to_v2()
        for k, v in itertools.chain(ifd.items(),
                                    getattr(im, 'tag_v2', {}).items(),
                                    legacy_ifd.items()):
            if k not in atts and k not in blocklist:
                if isinstance(v, unicode if bytes is str else str):
                    atts[k] = v.encode('ascii', 'replace') + b"\0"
                else:
                    atts[k] = v

        if DEBUG:
            print("Converted items: %s" % sorted(atts.items()))

        # libtiff always expects the bytes in native order.
        # we're storing image byte order. So, if the rawmode
        # contains I;16, we need to convert from native to image
        # byte order.
        if im.mode in ('I;16B', 'I;16'):
            rawmode = 'I;16N'

        a = (rawmode, compression, _fp, filename, atts)
        # print(im.mode, compression, a, im.encoderconfig)
        e = Image._getencoder(im.mode, 'libtiff', a, im.encoderconfig)
        e.setimage(im.im, (0, 0)+im.size)
        while True:
            # undone, change to self.decodermaxblock:
            l, s, d = e.encode(16*1024)
            if not _fp:
                fp.write(d)
            if s:
                break
        if s < 0:
            raise IOError("encoder error %d when writing image file" % s)

    else:
        offset = ifd.save(fp)

        ImageFile._save(im, fp, [
            ("raw", (0, 0)+im.size, offset, (rawmode, stride, 1))
            ])

    # -- helper for multi-page save --
    if "_debug_multipage" in im.encoderinfo:
        # just to access o32 and o16 (using correct byte order)
        im._debug_multipage = ifd

#
# --------------------------------------------------------------------
# Register

Image.register_open(TiffImageFile.format, TiffImageFile, _accept)
Image.register_save(TiffImageFile.format, _save)

Image.register_extension(TiffImageFile.format, ".tif")
Image.register_extension(TiffImageFile.format, ".tiff")

Image.register_mime(TiffImageFile.format, "image/tiff")
