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
import warnings

from ._binary import o8


class GimpPaletteFile:
    """File handler for GIMP's palette format."""

    rawmode = "RGB"

    #: override if reading larger palettes is needed
    max_colors = 256
    _max_line_size = 100
    _max_file_size = 2**20

    def __init__(self, fp):

        if fp.readline()[:12] != b"GIMP Palette":
            raise SyntaxError("not a GIMP palette file")

        read = 0

        self.palette = b""
        while len(self.palette) < 3 * self.max_colors:

            s = fp.readline(self._max_file_size)
            if not s:
                break

            read += len(s)
            if read >= self._max_file_size:
                warnings.warn(
                    f"Palette file truncated at {self._max_file_size - len(s)} bytes"
                )
                break

            # skip fields and comment lines
            if re.match(rb"\w+:|#", s):
                continue
            if len(s) > self._max_line_size:
                raise SyntaxError("bad palette file")

            # 4th column is color name and may contain spaces.
            v = s.split(None, 4)
            if len(v) < 3:
                raise ValueError("bad palette entry")
            for i in range(3):
                self.palette += o8(int(v[i]))

    def getpalette(self):

        return self.palette, self.rawmode

    @property
    def n_colors(self):
        return len(self.palette) / 3
