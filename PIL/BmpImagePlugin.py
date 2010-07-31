#
# The Python Imaging Library.
# $Id$
#
# BMP file handler
#
# Windows (and OS/2) native bitmap storage format.
#
# history:
# 1995-09-01 fl   Created
# 1996-04-30 fl   Added save
# 1997-08-27 fl   Fixed save of 1-bit images
# 1998-03-06 fl   Load P images as L where possible
# 1998-07-03 fl   Load P images as 1 where possible
# 1998-12-29 fl   Handle small palettes
# 2002-12-30 fl   Fixed load of 1-bit palette images
# 2003-04-21 fl   Fixed load of 1-bit monochrome images
# 2003-04-23 fl   Added limited support for BI_BITFIELDS compression
#
# Copyright (c) 1997-2003 by Secret Labs AB
# Copyright (c) 1995-2003 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#


__version__ = "0.7"


import string
import Image, ImageFile, ImagePalette


#
# --------------------------------------------------------------------
# Read BMP file

def i16(c):
    return ord(c[0]) + (ord(c[1])<<8)

def i32(c):
    return ord(c[0]) + (ord(c[1])<<8) + (ord(c[2])<<16) + (ord(c[3])<<24)


BIT2MODE = {
    # bits => mode, rawmode
    1: ("P", "P;1"),
    4: ("P", "P;4"),
    8: ("P", "P"),
    16: ("RGB", "BGR;15"),
    24: ("RGB", "BGR"),
    32: ("RGB", "BGRX")
}

def _accept(prefix):
    return prefix[:2] == "BM"

##
# Image plugin for the Windows BMP format.

class BmpImageFile(ImageFile.ImageFile):

    format = "BMP"
    format_description = "Windows Bitmap"

    def _bitmap(self, header = 0, offset = 0):

        if header:
            self.fp.seek(header)

        read = self.fp.read

        # CORE/INFO
        s = read(4)
        s = s + ImageFile._safe_read(self.fp, i32(s)-4)

        if len(s) == 12:

            # OS/2 1.0 CORE
            bits = i16(s[10:])
            self.size = i16(s[4:]), i16(s[6:])
            compression = 0
            lutsize = 3
            colors = 0
            direction = -1

        elif len(s) in [40, 64]:

            # WIN 3.1 or OS/2 2.0 INFO
            bits = i16(s[14:])
            self.size = i32(s[4:]), i32(s[8:])
            compression = i32(s[16:])
            lutsize = 4
            colors = i32(s[32:])
            direction = -1
            if s[11] == '\xff':
                # upside-down storage
                self.size = self.size[0], 2**32 - self.size[1]
                direction = 0

        else:
            raise IOError("Unsupported BMP header type (%d)" % len(s))

        if not colors:
            colors = 1 << bits

        # MODE
        try:
            self.mode, rawmode = BIT2MODE[bits]
        except KeyError:
            raise IOError("Unsupported BMP pixel depth (%d)" % bits)

        if compression == 3:
            # BI_BITFIELDS compression
            mask = i32(read(4)), i32(read(4)), i32(read(4))
            if bits == 32 and mask == (0xff0000, 0x00ff00, 0x0000ff):
                rawmode = "BGRX"
            elif bits == 16 and mask == (0x00f800, 0x0007e0, 0x00001f):
                rawmode = "BGR;16"
            elif bits == 16 and mask == (0x007c00, 0x0003e0, 0x00001f):
                rawmode = "BGR;15"
            else:
                # print bits, map(hex, mask)
                raise IOError("Unsupported BMP bitfields layout")
        elif compression != 0:
            raise IOError("Unsupported BMP compression (%d)" % compression)

        # LUT
        if self.mode == "P":
            palette = []
            greyscale = 1
            if colors == 2:
                indices = (0, 255)
            else:
                indices = range(colors)
            for i in indices:
                rgb = read(lutsize)[:3]
                if rgb != chr(i)*3:
                    greyscale = 0
                palette.append(rgb)
            if greyscale:
                if colors == 2:
                    self.mode = rawmode = "1"
                else:
                    self.mode = rawmode = "L"
            else:
                self.mode = "P"
                self.palette = ImagePalette.raw(
                    "BGR", string.join(palette, "")
                    )

        if not offset:
            offset = self.fp.tell()

        self.tile = [("raw",
                     (0, 0) + self.size,
                     offset,
                     (rawmode, ((self.size[0]*bits+31)>>3)&(~3), direction))]

        self.info["compression"] = compression

    def _open(self):

        # HEAD
        s = self.fp.read(14)
        if s[:2] != "BM":
            raise SyntaxError("Not a BMP file")
        offset = i32(s[10:])

        self._bitmap(offset=offset)


class DibImageFile(BmpImageFile):

    format = "DIB"
    format_description = "Windows Bitmap"

    def _open(self):
        self._bitmap()

#
# --------------------------------------------------------------------
# Write BMP file

def o16(i):
    return chr(i&255) + chr(i>>8&255)

def o32(i):
    return chr(i&255) + chr(i>>8&255) + chr(i>>16&255) + chr(i>>24&255)

SAVE = {
    "1": ("1", 1, 2),
    "L": ("L", 8, 256),
    "P": ("P", 8, 256),
    "RGB": ("BGR", 24, 0),
}

def _save(im, fp, filename, check=0):

    try:
        rawmode, bits, colors = SAVE[im.mode]
    except KeyError:
        raise IOError("cannot write mode %s as BMP" % im.mode)

    if check:
        return check

    stride = ((im.size[0]*bits+7)/8+3)&(~3)
    header = 40 # or 64 for OS/2 version 2
    offset = 14 + header + colors * 4
    image  = stride * im.size[1]

    # bitmap header
    fp.write("BM" +                     # file type (magic)
             o32(offset+image) +        # file size
             o32(0) +                   # reserved
             o32(offset))               # image data offset

    # bitmap info header
    fp.write(o32(header) +              # info header size
             o32(im.size[0]) +          # width
             o32(im.size[1]) +          # height
             o16(1) +                   # planes
             o16(bits) +                # depth
             o32(0) +                   # compression (0=uncompressed)
             o32(image) +               # size of bitmap
             o32(1) + o32(1) +          # resolution
             o32(colors) +              # colors used
             o32(colors))               # colors important

    fp.write("\000" * (header - 40))    # padding (for OS/2 format)

    if im.mode == "1":
        for i in (0, 255):
            fp.write(chr(i) * 4)
    elif im.mode == "L":
        for i in range(256):
            fp.write(chr(i) * 4)
    elif im.mode == "P":
        fp.write(im.im.getpalette("RGB", "BGRX"))

    ImageFile._save(im, fp, [("raw", (0,0)+im.size, 0, (rawmode, stride, -1))])

#
# --------------------------------------------------------------------
# Registry

Image.register_open(BmpImageFile.format, BmpImageFile, _accept)
Image.register_save(BmpImageFile.format, _save)

Image.register_extension(BmpImageFile.format, ".bmp")
