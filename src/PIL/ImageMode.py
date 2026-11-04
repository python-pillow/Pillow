#
# The Python Imaging Library.
# $Id$
#
# standard mode descriptors
#
# History:
# 2006-03-20 fl   Added
#
# Copyright (c) 2006 by Secret Labs AB.
# Copyright (c) 2006 by Fredrik Lundh.
#
# See the README file for information on usage and redistribution.
#
from __future__ import annotations

import sys
from functools import lru_cache
from typing import NamedTuple


class ModeDescriptor(NamedTuple):
    """Wrapper for mode strings."""

    mode: str
    bands: tuple[str, ...]
    basemode: str
    basetype: str
    typestr: str

    def __str__(self) -> str:
        return self.mode


@lru_cache
def getmode(mode: str) -> ModeDescriptor:
    """Gets a mode descriptor for the given mode."""
    endian = "<" if sys.byteorder == "little" else ">"

    modes = {
        # core modes
        # Bits need to be extended to bytes
        "1": (("1",), "L", "L", "|b1"),
        "L": (("L",), "L", "L", "|u1"),
        "I": (("I",), "L", "I", f"{endian}i4"),
        "F": (("F",), "L", "F", f"{endian}f4"),
        "P": (("P",), "P", "L", "|u1"),
        "RGB": (("R", "G", "B"), "RGB", "L", "|u1"),
        "RGBX": (("R", "G", "B", "X"), "RGB", "L", "|u1"),
        "RGBA": (("R", "G", "B", "A"), "RGB", "L", "|u1"),
        "CMYK": (("C", "M", "Y", "K"), "RGB", "L", "|u1"),
        "YCbCr": (("Y", "Cb", "Cr"), "RGB", "L", "|u1"),
        # UNDONE - unsigned |u1i1i1
        "LAB": (("L", "A", "B"), "RGB", "L", "|u1"),
        "HSV": (("H", "S", "V"), "RGB", "L", "|u1"),
        # extra experimental modes
        "RGBa": (("R", "G", "B", "a"), "RGB", "L", "|u1"),
        "LA": (("L", "A"), "L", "L", "|u1"),
        "La": (("L", "a"), "L", "L", "|u1"),
        "PA": (("P", "A"), "RGB", "L", "|u1"),
    }
    if mode in modes:
        bands, base_mode, base_type, type_str = modes[mode]
        return ModeDescriptor(mode, bands, base_mode, base_type, type_str)

    mapping_modes = {
        # I;16 == I;16L, and I;32 == I;32L
        "I;16": "<u2",
        "I;16S": "<i2",
        "I;16L": "<u2",
        "I;16LS": "<i2",
        "I;16B": ">u2",
        "I;16BS": ">i2",
        "I;16N": f"{endian}u2",
        "I;16NS": f"{endian}i2",
        "I;32": "<u4",
        "I;32B": ">u4",
        "I;32L": "<u4",
        "I;32S": "<i4",
        "I;32BS": ">i4",
        "I;32LS": "<i4",
    }

    type_str = mapping_modes[mode]
    return ModeDescriptor(mode, ("I",), "L", "L", type_str)
