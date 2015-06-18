#
# The Python Imaging Library.
# $Id$
#
# Sun image file handling
#
# History:
# 1995-09-10 fl   Created
# 1996-05-28 fl   Fixed 32-bit alignment
# 1998-12-29 fl   Import ImagePalette module
# 2001-12-18 fl   Fixed palette loading (from Jean-Claude Rimbault)
#
# Copyright (c) 1997-2001 by Secret Labs AB
# Copyright (c) 1995-1996 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#


__version__ = "0.3"


from PIL import Image, ImageFile, ImagePalette, _binary

i16 = _binary.i16be
i32 = _binary.i32be


def _accept(prefix):
    return len(prefix) >= 4 and i32(prefix) == 0x59a66a95


##
# Image plugin for Sun raster files.

class SunImageFile(ImageFile.ImageFile):

    format = "SUN"
    format_description = "Sun Raster File"

    def _open(self):

        # HEAD
        s = self.fp.read(32)
        if i32(s) != 0x59a66a95:
            raise SyntaxError("not an SUN raster file")

        offset = 32

        self.size = i32(s[4:8]), i32(s[8:12])

        depth = i32(s[12:16])
        if depth == 1:
            self.mode, rawmode = "1", "1;I"
        elif depth == 8:
            self.mode = rawmode = "L"
        elif depth == 24:
            self.mode, rawmode = "RGB", "BGR"
        else:
            raise SyntaxError("unsupported mode")

        compression = i32(s[20:24])

        if i32(s[24:28]) != 0:
            length = i32(s[28:32])
            offset = offset + length
            self.palette = ImagePalette.raw("RGB;L", self.fp.read(length))
            if self.mode == "L":
                self.mode = rawmode = "P"

        stride = (((self.size[0] * depth + 7) // 8) + 3) & (~3)

        if compression == 1:
            self.tile = [("raw", (0, 0)+self.size, offset, (rawmode, stride))]
        elif compression == 2:
            self.tile = [("sun_rle", (0, 0)+self.size, offset, rawmode)]

#
# registry

Image.register_open("SUN", SunImageFile, _accept)

Image.register_extension("SUN", ".ras")
