#
# The Python Imaging Library
# $Id$
#
# load a GIMP brush file
#
# History:
#       96-03-14 fl     Created
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1996.
#
# See the README file for information on usage and redistribution.
#

from PIL import Image, ImageFile, _binary

i32 = _binary.i32be


def _accept(prefix):
    return i32(prefix) >= 20 and i32(prefix[4:8]) == 1


##
# Image plugin for the GIMP brush format.

class GbrImageFile(ImageFile.ImageFile):

    format = "GBR"
    format_description = "GIMP brush file"

    def _open(self):

        header_size = i32(self.fp.read(4))
        version = i32(self.fp.read(4))
        if header_size < 20 or version != 1:
            raise SyntaxError("not a GIMP brush")

        width = i32(self.fp.read(4))
        height = i32(self.fp.read(4))
        bytes = i32(self.fp.read(4))
        if width <= 0 or height <= 0 or bytes != 1:
            raise SyntaxError("not a GIMP brush")

        comment = self.fp.read(header_size - 20)[:-1]

        self.mode = "L"
        self.size = width, height

        self.info["comment"] = comment

        # Since the brush is so small, we read the data immediately
        self.data = self.fp.read(width * height)

    def load(self):

        if not self.data:
            return

        # create an image out of the brush data block
        self.im = Image.core.new(self.mode, self.size)
        self.im.frombytes(self.data)
        self.data = b""

#
# registry

Image.register_open("GBR", GbrImageFile, _accept)

Image.register_extension("GBR", ".gbr")
