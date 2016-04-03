#
# The Python Imaging Library.
# $Id$
#
# PCD file handling
#
# History:
#       96-05-10 fl     Created
#       96-05-27 fl     Added draft mode (128x192, 256x384)
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1996.
#
# See the README file for information on usage and redistribution.
#


from PIL import Image, ImageFile, _binary

__version__ = "0.1"

i8 = _binary.i8


##
# Image plugin for PhotoCD images.  This plugin only reads the 768x512
# image from the file; higher resolutions are encoded in a proprietary
# encoding.

class PcdImageFile(ImageFile.ImageFile):

    format = "PCD"
    format_description = "Kodak PhotoCD"

    def _open(self):

        # rough
        self.fp.seek(2048)
        s = self.fp.read(2048)

        if s[:4] != b"PCD_":
            raise SyntaxError("not a PCD file")

        orientation = i8(s[1538]) & 3
        if orientation == 1:
            self.tile_post_rotate = 90  # hack
        elif orientation == 3:
            self.tile_post_rotate = -90

        self.mode = "RGB"
        self.size = 768, 512  # FIXME: not correct for rotated images!
        self.tile = [("pcd", (0, 0)+self.size, 96*2048, None)]

#
# registry

Image.register_open(PcdImageFile.format, PcdImageFile)

Image.register_extension(PcdImageFile.format, ".pcd")
