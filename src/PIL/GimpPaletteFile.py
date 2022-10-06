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


class GimpPaletteFile:
    """File handler for GIMP's palette format."""

    rawmode = "RGB"

    def __init__(self, fp):

        if fp.readline()[:12] != b"GIMP Palette":
            raise SyntaxError("not a GIMP palette file")

        self.palette = b""
        while len(self.palette) < 768:

            s = fp.readline()
            if not s:
                break

            # skip fields and comment lines
            if re.match(rb"\w+:|#", s):
                continue
            if len(s) > 100:
                raise SyntaxError("bad palette file")

            v = s.split()
            if len(v) < 3:
                raise ValueError("bad palette entry")
            for i in range(3):
                self.palette += o8(int(v[i]))

    def getpalette(self):

        return self.palette, self.rawmode
