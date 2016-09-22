#
# The Python Imaging Library.
# $Id$
#
# XBM File handling
#
# Copyright (c) 1997-2004 by Secret Labs AB
# Copyright (c) 1996-1997 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

import re
from PIL import Image, ImageFile

__version__ = "0.6"

# XBM header
xbm_head = re.compile(
    b"\s*#define[ \t]+.*_width[ \t]+(?P<width>[0-9]+)[\r\n]+"
    b"#define[ \t]+.*_height[ \t]+(?P<height>[0-9]+)[\r\n]+"
    b"(?P<hotspot>"
    b"#define[ \t]+[^_]*_x_hot[ \t]+(?P<xhot>[0-9]+)[\r\n]+"
    b"#define[ \t]+[^_]*_y_hot[ \t]+(?P<yhot>[0-9]+)[\r\n]+"
    b")?"
    b"[\\000-\\377]*_bits\\[\\]"
)


def _accept(prefix):
    return prefix.lstrip()[:7] == b"#define"


##
# Image plugin for X11 bitmaps.

class XbmImageFile(ImageFile.ImageFile):

    format = "XBM"
    format_description = "X11 Bitmap"

    def _open(self):

        m = xbm_head.match(self.fp.read(512))

        if m:

            xsize = int(m.group("width"))
            ysize = int(m.group("height"))

            if m.group("hotspot"):
                self.info["hotspot"] = (
                    int(m.group("xhot")), int(m.group("yhot"))
                    )

            self.mode = "1"
            self.size = xsize, ysize

            self.tile = [("xbm", (0, 0)+self.size, m.end(), None)]


def _save(im, fp, filename):

    if im.mode != "1":
        raise IOError("cannot write mode %s as XBM" % im.mode)

    fp.write(("#define im_width %d\n" % im.size[0]).encode('ascii'))
    fp.write(("#define im_height %d\n" % im.size[1]).encode('ascii'))

    hotspot = im.encoderinfo.get("hotspot")
    if hotspot:
        fp.write(("#define im_x_hot %d\n" % hotspot[0]).encode('ascii'))
        fp.write(("#define im_y_hot %d\n" % hotspot[1]).encode('ascii'))

    fp.write(b"static char im_bits[] = {\n")

    ImageFile._save(im, fp, [("xbm", (0, 0)+im.size, 0, None)])

    fp.write(b"};\n")


Image.register_open(XbmImageFile.format, XbmImageFile, _accept)
Image.register_save(XbmImageFile.format, _save)

Image.register_extension(XbmImageFile.format, ".xbm")

Image.register_mime(XbmImageFile.format, "image/xbm")
