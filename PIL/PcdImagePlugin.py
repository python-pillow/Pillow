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


__version__ = "0.1"


from PIL import Image, ImageFile, _binary

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
            self.tile_post_rotate = 90 # hack
        elif orientation == 3:
            self.tile_post_rotate = -90

        self.mode = "RGB"
        self.size = 768, 512 # FIXME: not correct for rotated images!
        self.tile = [("pcd", (0,0)+self.size, 96*2048, None)]

    def draft(self, mode, size):

        if len(self.tile) != 1:
            return

        d, e, o, a = self.tile[0]

        if size:
            scale = max(self.size[0] / size[0], self.size[1] / size[1])
            for s, o in [(4,0*2048), (2,0*2048), (1,96*2048)]:
                if scale >= s:
                    break
            # e = e[0], e[1], (e[2]-e[0]+s-1)/s+e[0], (e[3]-e[1]+s-1)/s+e[1]
            # self.size = ((self.size[0]+s-1)/s, (self.size[1]+s-1)/s)

        self.tile = [(d, e, o, a)]

        return self

#
# registry

Image.register_open("PCD", PcdImageFile)

Image.register_extension("PCD", ".pcd")
