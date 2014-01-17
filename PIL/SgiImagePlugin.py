#
# The Python Imaging Library.
# $Id$
#
# SGI image file handling
#
# See "The SGI Image File Format (Draft version 0.97)", Paul Haeberli.
# <ftp://ftp.sgi.com/graphics/SGIIMAGESPEC>
#
# History:
# 1995-09-10 fl   Created
#
# Copyright (c) 2008 by Karsten Hiddemann.
# Copyright (c) 1997 by Secret Labs AB.
# Copyright (c) 1995 by Fredrik Lundh.
#
# See the README file for information on usage and redistribution.
#


__version__ = "0.2"


from PIL import Image, ImageFile, _binary

i8 = _binary.i8
i16 = _binary.i16be
i32 = _binary.i32be


def _accept(prefix):
    return i16(prefix) == 474

##
# Image plugin for SGI images.

class SgiImageFile(ImageFile.ImageFile):

    format = "SGI"
    format_description = "SGI Image File Format"

    def _open(self):

        # HEAD
        s = self.fp.read(512)
        if i16(s) != 474:
            raise SyntaxError("not an SGI image file")

        # relevant header entries
        compression = i8(s[2])

        # bytes, dimension, zsize
        layout = i8(s[3]), i16(s[4:]), i16(s[10:])

        # determine mode from bytes/zsize
        if layout == (1, 2, 1) or layout == (1, 1, 1):
            self.mode = "L"
        elif layout == (1, 3, 3):
            self.mode = "RGB"
        elif layout == (1, 3, 4):
            self.mode = "RGBA"
        else:
            raise SyntaxError("unsupported SGI image mode")

        # size
        self.size = i16(s[6:]), i16(s[8:])


        # decoder info
        if compression == 0:
            offset = 512
            pagesize = self.size[0]*self.size[1]*layout[0]
            self.tile = []
            for layer in self.mode:
                self.tile.append(("raw", (0,0)+self.size, offset, (layer,0,-1)))
                offset = offset + pagesize
        elif compression == 1:
            self.tile = [("sgi_rle", (0,0)+self.size, 512, (self.mode, 0, -1))]

#
# registry

Image.register_open("SGI", SgiImageFile, _accept)

Image.register_extension("SGI", ".bw")
Image.register_extension("SGI", ".rgb")
Image.register_extension("SGI", ".rgba")

Image.register_extension("SGI", ".sgi") # really?
