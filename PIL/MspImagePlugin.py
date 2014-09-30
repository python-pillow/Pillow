#
# The Python Imaging Library.
# $Id$
#
# MSP file handling
#
# This is the format used by the Paint program in Windows 1 and 2.
#
# History:
#       95-09-05 fl     Created
#       97-01-03 fl     Read/write MSP images
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1995-97.
#
# See the README file for information on usage and redistribution.
#


__version__ = "0.1"

from PIL import Image, ImageFile, _binary


#
# read MSP files

i16 = _binary.i16le


def _accept(prefix):
    return prefix[:4] in [b"DanM", b"LinS"]


##
# Image plugin for Windows MSP images.  This plugin supports both
# uncompressed (Windows 1.0).

class MspImageFile(ImageFile.ImageFile):

    format = "MSP"
    format_description = "Windows Paint"

    def _open(self):

        # Header
        s = self.fp.read(32)
        if s[:4] not in [b"DanM", b"LinS"]:
            raise SyntaxError("not an MSP file")

        # Header checksum
        sum = 0
        for i in range(0, 32, 2):
            sum = sum ^ i16(s[i:i+2])
        if sum != 0:
            raise SyntaxError("bad MSP checksum")

        self.mode = "1"
        self.size = i16(s[4:]), i16(s[6:])

        if s[:4] == b"DanM":
            self.tile = [("raw", (0, 0)+self.size, 32, ("1", 0, 1))]
        else:
            self.tile = [("msp", (0, 0)+self.size, 32+2*self.size[1], None)]

#
# write MSP files (uncompressed only)

o16 = _binary.o16le


def _save(im, fp, filename):

    if im.mode != "1":
        raise IOError("cannot write mode %s as MSP" % im.mode)

    # create MSP header
    header = [0] * 16

    header[0], header[1] = i16(b"Da"), i16(b"nM")  # version 1
    header[2], header[3] = im.size
    header[4], header[5] = 1, 1
    header[6], header[7] = 1, 1
    header[8], header[9] = im.size

    sum = 0
    for h in header:
        sum = sum ^ h
    header[12] = sum  # FIXME: is this the right field?

    # header
    for h in header:
        fp.write(o16(h))

    # image body
    ImageFile._save(im, fp, [("raw", (0, 0)+im.size, 32, ("1", 0, 1))])

#
# registry

Image.register_open("MSP", MspImageFile, _accept)
Image.register_save("MSP", _save)

Image.register_extension("MSP", ".msp")
