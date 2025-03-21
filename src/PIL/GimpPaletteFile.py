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
from __future__ import annotations

import re
import warnings
from typing import IO


class GimpPaletteFile:
    """File handler for GIMP's palette format."""

    rawmode = "RGB"

    #: override if reading larger palettes is needed
    max_colors = 256
    _max_line_size = 100
    _max_file_size = 2**20  # 1MB

    def __init__(self, fp: IO[bytes]) -> None:
        if not fp.readline().startswith(b"GIMP Palette"):
            msg = "not a GIMP palette file"
            raise SyntaxError(msg)

        read = 0

        palette: list[int] = []
        while len(palette) < 3 * self.max_colors:

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
                msg = "bad palette file"
                raise SyntaxError(msg)

            # 4th column is color name and may contain spaces.
            v = s.split(maxsplit=3)
            if len(v) < 3:
                msg = "bad palette entry"
                raise ValueError(msg)

            palette += (int(v[i]) for i in range(3))

        self.palette = bytes(palette)

    def getpalette(self) -> tuple[bytes, str]:
        return self.palette, self.rawmode
