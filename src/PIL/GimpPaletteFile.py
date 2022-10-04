#
# Python Imaging Library
# $Id$
#
# stuff to read GIMP palette files
#
# History:
# 1997-08-23 fl     Created
# 2004-09-07 fl     Support GIMP 2.0 palette files.
#
# Copyright (c) Secret Labs AB 1997-2004.  All rights reserved.
# Copyright (c) Fredrik Lundh 1997-2004.
#
# See the README file for information on usage and redistribution.
#

import re

from ._binary import o8

_str_to_o8 = lambda v: o8(int(v))


class GimpPaletteFile:
    """File handler for GIMP's palette format."""

    rawmode = "RGB"

    def __init__(self, fp):

        palette = bytearray(b"".join([o8(i) * 3 for i in range(256)]))

        if fp.readline()[:12] != b"GIMP Palette":
            raise SyntaxError("not a GIMP palette file")

        index = 0
        for s in fp:
            # skip fields and comment lines
            if re.match(rb"\w+:|#", s):
                continue
            if len(s) > 100:
                raise SyntaxError("bad palette file")

            v = tuple(map(int, s.split()[:3]))
            if len(v) < 3:
                raise ValueError("bad palette entry")

            palette[index * 3 : index * 3 + 3] = v
            index += 1

        self.palette = bytes(palette)
        self.n_colors = index

    def getpalette(self):

        return self.palette, self.rawmode
