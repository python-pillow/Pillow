#
# The Python Imaging Library.
# $Id$
#
# XV Thumbnail file handler by Charles E. "Gene" Cash
# (gcash@magicnet.net)
#
# see xvcolor.c and xvbrowse.c in the sources to John Bradley's XV,
# available from ftp://ftp.cis.upenn.edu/pub/xv/
#
# history:
# 98-08-15 cec  created (b/w only)
# 98-12-09 cec  added color palette
# 98-12-28 fl   added to PIL (with only a few very minor modifications)
#
# To do:
# FIXME: make save work (this requires quantization support)
#

from PIL import Image, ImageFile, ImagePalette, _binary

__version__ = "0.1"

o8 = _binary.o8

_MAGIC = b"P7 332"

# standard color palette for thumbnails (RGB332)
PALETTE = b""
for r in range(8):
    for g in range(8):
        for b in range(4):
            PALETTE = PALETTE + (o8((r*255)//7)+o8((g*255)//7)+o8((b*255)//3))


def _accept(prefix):
    return prefix[:6] == _MAGIC


##
# Image plugin for XV thumbnail images.

class XVThumbImageFile(ImageFile.ImageFile):

    format = "XVThumb"
    format_description = "XV thumbnail image"

    def _open(self):

        # check magic
        if self.fp.read(6) != _MAGIC:
            raise SyntaxError("not an XV thumbnail file")

        # Skip to beginning of next line
        self.fp.readline()

        # skip info comments
        while True:
            s = self.fp.readline()
            if not s:
                raise SyntaxError("Unexpected EOF reading XV thumbnail file")
            if s[0] != b'#':
                break

        # parse header line (already read)
        s = s.strip().split()

        self.mode = "P"
        self.size = int(s[0:1]), int(s[1:2])

        self.palette = ImagePalette.raw("RGB", PALETTE)

        self.tile = [
            ("raw", (0, 0)+self.size,
             self.fp.tell(), (self.mode, 0, 1)
             )]

# --------------------------------------------------------------------

Image.register_open(XVThumbImageFile.format, XVThumbImageFile, _accept)
