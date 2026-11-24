#
# The Python Imaging Library.
# $Id$
#
# BMP file handler
#
# Windows (and OS/2) native bitmap storage format.
#
# history:
# 1995-09-01 fl   Created
# 1996-04-30 fl   Added save
# 1997-08-27 fl   Fixed save of 1-bit images
# 1998-03-06 fl   Load P images as L where possible
# 1998-07-03 fl   Load P images as 1 where possible
# 1998-12-29 fl   Handle small palettes
# 2002-12-30 fl   Fixed load of 1-bit palette images
# 2003-04-21 fl   Fixed load of 1-bit monochrome images
# 2003-04-23 fl   Added limited support for BI_BITFIELDS compression
#
# Copyright (c) 1997-2003 by Secret Labs AB
# Copyright (c) 1995-2003 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#
from __future__ import annotations

__lazy_modules__ = {"PIL._binary"}

import os

from . import Image, ImageFile, ImagePalette
from ._binary import i16le as i16
from ._binary import i32le as i32
from ._binary import o8
from ._binary import o16le as o16
from ._binary import o32le as o32

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import IO, Any

#
# --------------------------------------------------------------------
# Read BMP file

BIT2MODE = {
    # bits => mode, rawmode
    1: ("P", "P;1"),
    4: ("P", "P;4"),
    8: ("P", "P"),
    16: ("RGB", "XRGB;1555"),
    24: ("RGB", "BGR"),
    32: ("RGB", "BGRX"),
}

USE_RAW_ALPHA = False


def _accept(prefix: bytes) -> bool:
    return prefix.startswith(b"BM")


def _dib_accept(prefix: bytes) -> bool:
    return i32(prefix) in [12, 40, 52, 56, 64, 108, 124]


# =============================================================================
# Image plugin for the Windows BMP format.
# =============================================================================
class BmpImageFile(ImageFile.ImageFile):
    """Image plugin for the Windows Bitmap format (BMP)"""

    # ------------------------------------------------------------- Description
    format_description = "Windows Bitmap"
    format = "BMP"

    # -------------------------------------------------- BMP Compression values
    COMPRESSIONS = {"RAW": 0, "RLE8": 1, "RLE4": 2, "BITFIELDS": 3, "JPEG": 4, "PNG": 5}
    for k, v in COMPRESSIONS.items():
        vars()[k] = v

    def _bitmap(self, header: int = 0, offset: int = 0) -> None:
        """Read relevant info about the BMP"""
        assert self.fp is not None
        read, seek = self.fp.read, self.fp.seek
        if header:
            seek(header)
        # read bmp header size @offset 14 (this is part of the header size)
        file_info: dict[str, bool | int | tuple[int, ...]] = {
            "header_size": i32(read(4)),
            "direction": -1,
        }

        # -------------------- If requested, read header at a specific position
        # read the rest of the bmp header, without its size
        assert isinstance(file_info["header_size"], int)
        header_data = ImageFile._safe_read(self.fp, file_info["header_size"] - 4)

        # ------------------------------- Windows Bitmap v2, IBM OS/2 Bitmap v1
        # ----- This format has different offsets because of width/height types
        # 12: BITMAPCOREHEADER/OS21XBITMAPHEADER
        if file_info["header_size"] == 12:
            file_info["width"] = i16(header_data, 0)
            file_info["height"] = i16(header_data, 2)
            file_info["planes"] = i16(header_data, 4)
            file_info["bits"] = i16(header_data, 6)
            file_info["compression"] = self.COMPRESSIONS["RAW"]
            file_info["palette_padding"] = 3

        # --------------------------------------------- Windows Bitmap v3 to v5
        #  40: BITMAPINFOHEADER
        #  52: BITMAPV2HEADER
        #  56: BITMAPV3HEADER
        #  64: BITMAPCOREHEADER2/OS22XBITMAPHEADER
        # 108: BITMAPV4HEADER
        # 124: BITMAPV5HEADER
        elif file_info["header_size"] in (40, 52, 56, 64, 108, 124):
            file_info["y_flip"] = header_data[7] == 0xFF
            file_info["direction"] = 1 if file_info["y_flip"] else -1
            file_info["width"] = i32(header_data, 0)
            file_info["height"] = (
                i32(header_data, 4)
                if not file_info["y_flip"]
                else 2**32 - i32(header_data, 4)
            )
            file_info["planes"] = i16(header_data, 8)
            file_info["bits"] = i16(header_data, 10)
            file_info["compression"] = i32(header_data, 12)
            # byte size of pixel data
            file_info["data_size"] = i32(header_data, 16)
            file_info["pixels_per_meter"] = (
                i32(header_data, 20),
                i32(header_data, 24),
            )
            file_info["colors"] = i32(header_data, 28)
            file_info["palette_padding"] = 4
            assert isinstance(file_info["pixels_per_meter"], tuple)
            dpi = tuple(x / 39.3701 for x in file_info["pixels_per_meter"])
            if dpi != (0, 0):
                self.info["dpi"] = dpi
            if file_info["compression"] == self.COMPRESSIONS["BITFIELDS"]:
                masks = ["r_mask", "g_mask", "b_mask"]
                if len(header_data) >= 48:
                    if len(header_data) >= 52:
                        masks.append("a_mask")
                    else:
                        file_info["a_mask"] = 0x0
                    for idx, mask in enumerate(masks):
                        file_info[mask] = i32(header_data, 36 + idx * 4)
                else:
                    # 40 byte headers only have the three components in the
                    # bitfields masks, ref:
                    # https://msdn.microsoft.com/en-us/library/windows/desktop/dd183376(v=vs.85).aspx
                    # See also
                    # https://github.com/python-pillow/Pillow/issues/1293
                    # There is a 4th component in the RGBQuad, in the alpha
                    # location, but it is listed as a reserved component,
                    # and it is not generally an alpha channel
                    file_info["a_mask"] = 0x0
                    for mask in masks:
                        file_info[mask] = i32(read(4))
                assert isinstance(file_info["r_mask"], int)
                assert isinstance(file_info["g_mask"], int)
                assert isinstance(file_info["b_mask"], int)
                assert isinstance(file_info["a_mask"], int)
                file_info["rgb_mask"] = (
                    file_info["r_mask"],
                    file_info["g_mask"],
                    file_info["b_mask"],
                )
                file_info["rgba_mask"] = (
                    file_info["r_mask"],
                    file_info["g_mask"],
                    file_info["b_mask"],
                    file_info["a_mask"],
                )
        else:
            msg = f"Unsupported BMP header type ({file_info['header_size']})"
            raise OSError(msg)

        # ------------------ Special case : header is reported 40, which
        # ---------------------- is shorter than real size for bpp >= 16
        assert isinstance(file_info["width"], int)
        assert isinstance(file_info["height"], int)
        self._size = file_info["width"], file_info["height"]

        # ------- If color count was not found in the header, compute from bits
        assert isinstance(file_info["bits"], int)
        if not file_info.get("colors", 0):
            file_info["colors"] = 1 << file_info["bits"]
        assert isinstance(file_info["palette_padding"], int)
        assert isinstance(file_info["colors"], int)
        if offset == 14 + file_info["header_size"] and file_info["bits"] <= 8:
            offset += file_info["palette_padding"] * file_info["colors"]

        # ---------------------- Check bit depth for unusual unsupported values
        self._mode, raw_mode = BIT2MODE.get(file_info["bits"], ("", ""))
        if not self.mode:
            msg = f"Unsupported BMP pixel depth ({file_info['bits']})"
            raise OSError(msg)

        # ---------------- Process BMP with Bitfields compression (not palette)
        decoder_name = "raw"
        if file_info["compression"] == self.COMPRESSIONS["BITFIELDS"]:
            SUPPORTED: dict[int, list[tuple[int, ...]]] = {
                32: [
                    (0xFF0000, 0xFF00, 0xFF, 0x0),
                    (0xFF000000, 0xFF0000, 0xFF00, 0x0),
                    (0xFF000000, 0xFF00, 0xFF, 0x0),
                    (0xFF000000, 0xFF0000, 0xFF00, 0xFF),
                    (0xFF, 0xFF00, 0xFF0000, 0xFF000000),
                    (0xFF0000, 0xFF00, 0xFF, 0xFF000000),
                    (0xFF000000, 0xFF00, 0xFF, 0xFF0000),
                    (0x0, 0x0, 0x0, 0x0),
                ],
                24: [(0xFF0000, 0xFF00, 0xFF)],
                16: [(0xF800, 0x7E0, 0x1F), (0x7C00, 0x3E0, 0x1F)],
            }
            MASK_MODES = {
                (32, (0xFF0000, 0xFF00, 0xFF, 0x0)): "BGRX",
                (32, (0xFF000000, 0xFF0000, 0xFF00, 0x0)): "XBGR",
                (32, (0xFF000000, 0xFF00, 0xFF, 0x0)): "BGXR",
                (32, (0xFF000000, 0xFF0000, 0xFF00, 0xFF)): "ABGR",
                (32, (0xFF, 0xFF00, 0xFF0000, 0xFF000000)): "RGBA",
                (32, (0xFF0000, 0xFF00, 0xFF, 0xFF000000)): "BGRA",
                (32, (0xFF000000, 0xFF00, 0xFF, 0xFF0000)): "BGAR",
                (32, (0x0, 0x0, 0x0, 0x0)): "BGRA",
                (24, (0xFF0000, 0xFF00, 0xFF)): "BGR",
                (16, (0xF800, 0x7E0, 0x1F)): "RGB;565",
                (16, (0x7C00, 0x3E0, 0x1F)): "XRGB;1555",
            }
            if file_info["bits"] in SUPPORTED:
                if (
                    file_info["bits"] == 32
                    and file_info["rgba_mask"] in SUPPORTED[file_info["bits"]]
                ):
                    assert isinstance(file_info["rgba_mask"], tuple)
                    raw_mode = MASK_MODES[(file_info["bits"], file_info["rgba_mask"])]
                    self._mode = "RGBA" if "A" in raw_mode else self.mode
                elif (
                    file_info["bits"] in (24, 16)
                    and file_info["rgb_mask"] in SUPPORTED[file_info["bits"]]
                ):
                    assert isinstance(file_info["rgb_mask"], tuple)
                    raw_mode = MASK_MODES[(file_info["bits"], file_info["rgb_mask"])]
                else:
                    msg = "Unsupported BMP bitfields layout"
                    raise OSError(msg)
            else:
                msg = "Unsupported BMP bitfields layout"
                raise OSError(msg)
        elif file_info["compression"] == self.COMPRESSIONS["RAW"]:
            if file_info["bits"] == 32 and (
                header == 22 or USE_RAW_ALPHA  # 32-bit .cur offset
            ):
                raw_mode, self._mode = "BGRA", "RGBA"
        elif file_info["compression"] in (
            self.COMPRESSIONS["RLE8"],
            self.COMPRESSIONS["RLE4"],
        ):
            decoder_name = "bmp_rle"
        else:
            msg = f"Unsupported BMP compression ({file_info['compression']})"
            raise OSError(msg)

        # --------------- Once the header is processed, process the palette/LUT
        if self.mode == "P":  # Paletted for 1, 4 and 8 bit images
            # ---------------------------------------------------- 1-bit images
            if not (0 < file_info["colors"] <= 256):
                msg = f"Unsupported BMP Palette size ({file_info['colors']})"
                raise OSError(msg)
            else:
                padding = file_info["palette_padding"]
                palette = read(padding * file_info["colors"])

                if file_info["colors"] == 2:
                    if padding == 4:
                        # b"".join(bytes((val,) * 3 + (0,)) for val in (0, 255))
                        grayscale_palette = b"\x00\x00\x00\x00\xff\xff\xff\x00"
                    else:
                        # b"".join(bytes((val,) * 3) for val in (0, 255))
                        grayscale_palette = b"\x00\x00\x00\xff\xff\xff"
                else:
                    if padding == 4:
                        # b"".join(bytes((val,) * 3 + (0,)) for val in range(256))
                        grayscale_palette = b"\x00\x00\x00\x00\x01\x01\x01\x00\x02\x02\x02\x00\x03\x03\x03\x00\x04\x04\x04\x00\x05\x05\x05\x00\x06\x06\x06\x00\x07\x07\x07\x00\x08\x08\x08\x00\t\t\t\x00\n\n\n\x00\x0b\x0b\x0b\x00\x0c\x0c\x0c\x00\r\r\r\x00\x0e\x0e\x0e\x00\x0f\x0f\x0f\x00\x10\x10\x10\x00\x11\x11\x11\x00\x12\x12\x12\x00\x13\x13\x13\x00\x14\x14\x14\x00\x15\x15\x15\x00\x16\x16\x16\x00\x17\x17\x17\x00\x18\x18\x18\x00\x19\x19\x19\x00\x1a\x1a\x1a\x00\x1b\x1b\x1b\x00\x1c\x1c\x1c\x00\x1d\x1d\x1d\x00\x1e\x1e\x1e\x00\x1f\x1f\x1f\x00   \x00!!!\x00\"\"\"\x00###\x00$$$\x00%%%\x00&&&\x00'''\x00(((\x00)))\x00***\x00+++\x00,,,\x00---\x00...\x00///\x00000\x00111\x00222\x00333\x00444\x00555\x00666\x00777\x00888\x00999\x00:::\x00;;;\x00<<<\x00===\x00>>>\x00???\x00@@@\x00AAA\x00BBB\x00CCC\x00DDD\x00EEE\x00FFF\x00GGG\x00HHH\x00III\x00JJJ\x00KKK\x00LLL\x00MMM\x00NNN\x00OOO\x00PPP\x00QQQ\x00RRR\x00SSS\x00TTT\x00UUU\x00VVV\x00WWW\x00XXX\x00YYY\x00ZZZ\x00[[[\x00\\\\\\\x00]]]\x00^^^\x00___\x00```\x00aaa\x00bbb\x00ccc\x00ddd\x00eee\x00fff\x00ggg\x00hhh\x00iii\x00jjj\x00kkk\x00lll\x00mmm\x00nnn\x00ooo\x00ppp\x00qqq\x00rrr\x00sss\x00ttt\x00uuu\x00vvv\x00www\x00xxx\x00yyy\x00zzz\x00{{{\x00|||\x00}}}\x00~~~\x00\x7f\x7f\x7f\x00\x80\x80\x80\x00\x81\x81\x81\x00\x82\x82\x82\x00\x83\x83\x83\x00\x84\x84\x84\x00\x85\x85\x85\x00\x86\x86\x86\x00\x87\x87\x87\x00\x88\x88\x88\x00\x89\x89\x89\x00\x8a\x8a\x8a\x00\x8b\x8b\x8b\x00\x8c\x8c\x8c\x00\x8d\x8d\x8d\x00\x8e\x8e\x8e\x00\x8f\x8f\x8f\x00\x90\x90\x90\x00\x91\x91\x91\x00\x92\x92\x92\x00\x93\x93\x93\x00\x94\x94\x94\x00\x95\x95\x95\x00\x96\x96\x96\x00\x97\x97\x97\x00\x98\x98\x98\x00\x99\x99\x99\x00\x9a\x9a\x9a\x00\x9b\x9b\x9b\x00\x9c\x9c\x9c\x00\x9d\x9d\x9d\x00\x9e\x9e\x9e\x00\x9f\x9f\x9f\x00\xa0\xa0\xa0\x00\xa1\xa1\xa1\x00\xa2\xa2\xa2\x00\xa3\xa3\xa3\x00\xa4\xa4\xa4\x00\xa5\xa5\xa5\x00\xa6\xa6\xa6\x00\xa7\xa7\xa7\x00\xa8\xa8\xa8\x00\xa9\xa9\xa9\x00\xaa\xaa\xaa\x00\xab\xab\xab\x00\xac\xac\xac\x00\xad\xad\xad\x00\xae\xae\xae\x00\xaf\xaf\xaf\x00\xb0\xb0\xb0\x00\xb1\xb1\xb1\x00\xb2\xb2\xb2\x00\xb3\xb3\xb3\x00\xb4\xb4\xb4\x00\xb5\xb5\xb5\x00\xb6\xb6\xb6\x00\xb7\xb7\xb7\x00\xb8\xb8\xb8\x00\xb9\xb9\xb9\x00\xba\xba\xba\x00\xbb\xbb\xbb\x00\xbc\xbc\xbc\x00\xbd\xbd\xbd\x00\xbe\xbe\xbe\x00\xbf\xbf\xbf\x00\xc0\xc0\xc0\x00\xc1\xc1\xc1\x00\xc2\xc2\xc2\x00\xc3\xc3\xc3\x00\xc4\xc4\xc4\x00\xc5\xc5\xc5\x00\xc6\xc6\xc6\x00\xc7\xc7\xc7\x00\xc8\xc8\xc8\x00\xc9\xc9\xc9\x00\xca\xca\xca\x00\xcb\xcb\xcb\x00\xcc\xcc\xcc\x00\xcd\xcd\xcd\x00\xce\xce\xce\x00\xcf\xcf\xcf\x00\xd0\xd0\xd0\x00\xd1\xd1\xd1\x00\xd2\xd2\xd2\x00\xd3\xd3\xd3\x00\xd4\xd4\xd4\x00\xd5\xd5\xd5\x00\xd6\xd6\xd6\x00\xd7\xd7\xd7\x00\xd8\xd8\xd8\x00\xd9\xd9\xd9\x00\xda\xda\xda\x00\xdb\xdb\xdb\x00\xdc\xdc\xdc\x00\xdd\xdd\xdd\x00\xde\xde\xde\x00\xdf\xdf\xdf\x00\xe0\xe0\xe0\x00\xe1\xe1\xe1\x00\xe2\xe2\xe2\x00\xe3\xe3\xe3\x00\xe4\xe4\xe4\x00\xe5\xe5\xe5\x00\xe6\xe6\xe6\x00\xe7\xe7\xe7\x00\xe8\xe8\xe8\x00\xe9\xe9\xe9\x00\xea\xea\xea\x00\xeb\xeb\xeb\x00\xec\xec\xec\x00\xed\xed\xed\x00\xee\xee\xee\x00\xef\xef\xef\x00\xf0\xf0\xf0\x00\xf1\xf1\xf1\x00\xf2\xf2\xf2\x00\xf3\xf3\xf3\x00\xf4\xf4\xf4\x00\xf5\xf5\xf5\x00\xf6\xf6\xf6\x00\xf7\xf7\xf7\x00\xf8\xf8\xf8\x00\xf9\xf9\xf9\x00\xfa\xfa\xfa\x00\xfb\xfb\xfb\x00\xfc\xfc\xfc\x00\xfd\xfd\xfd\x00\xfe\xfe\xfe\x00\xff\xff\xff\x00"  # noqa: E501
                    else:
                        # b"".join(bytes((val,) * 3) for val in range(256))
                        grayscale_palette = b"\x00\x00\x00\x01\x01\x01\x02\x02\x02\x03\x03\x03\x04\x04\x04\x05\x05\x05\x06\x06\x06\x07\x07\x07\x08\x08\x08\t\t\t\n\n\n\x0b\x0b\x0b\x0c\x0c\x0c\r\r\r\x0e\x0e\x0e\x0f\x0f\x0f\x10\x10\x10\x11\x11\x11\x12\x12\x12\x13\x13\x13\x14\x14\x14\x15\x15\x15\x16\x16\x16\x17\x17\x17\x18\x18\x18\x19\x19\x19\x1a\x1a\x1a\x1b\x1b\x1b\x1c\x1c\x1c\x1d\x1d\x1d\x1e\x1e\x1e\x1f\x1f\x1f   !!!\"\"\"###$$$%%%&&&'''((()))***+++,,,---...///000111222333444555666777888999:::;;;<<<===>>>???@@@AAABBBCCCDDDEEEFFFGGGHHHIIIJJJKKKLLLMMMNNNOOOPPPQQQRRRSSSTTTUUUVVVWWWXXXYYYZZZ[[[\\\\\\]]]^^^___```aaabbbcccdddeeefffggghhhiiijjjkkklllmmmnnnooopppqqqrrrssstttuuuvvvwwwxxxyyyzzz{{{|||}}}~~~\x7f\x7f\x7f\x80\x80\x80\x81\x81\x81\x82\x82\x82\x83\x83\x83\x84\x84\x84\x85\x85\x85\x86\x86\x86\x87\x87\x87\x88\x88\x88\x89\x89\x89\x8a\x8a\x8a\x8b\x8b\x8b\x8c\x8c\x8c\x8d\x8d\x8d\x8e\x8e\x8e\x8f\x8f\x8f\x90\x90\x90\x91\x91\x91\x92\x92\x92\x93\x93\x93\x94\x94\x94\x95\x95\x95\x96\x96\x96\x97\x97\x97\x98\x98\x98\x99\x99\x99\x9a\x9a\x9a\x9b\x9b\x9b\x9c\x9c\x9c\x9d\x9d\x9d\x9e\x9e\x9e\x9f\x9f\x9f\xa0\xa0\xa0\xa1\xa1\xa1\xa2\xa2\xa2\xa3\xa3\xa3\xa4\xa4\xa4\xa5\xa5\xa5\xa6\xa6\xa6\xa7\xa7\xa7\xa8\xa8\xa8\xa9\xa9\xa9\xaa\xaa\xaa\xab\xab\xab\xac\xac\xac\xad\xad\xad\xae\xae\xae\xaf\xaf\xaf\xb0\xb0\xb0\xb1\xb1\xb1\xb2\xb2\xb2\xb3\xb3\xb3\xb4\xb4\xb4\xb5\xb5\xb5\xb6\xb6\xb6\xb7\xb7\xb7\xb8\xb8\xb8\xb9\xb9\xb9\xba\xba\xba\xbb\xbb\xbb\xbc\xbc\xbc\xbd\xbd\xbd\xbe\xbe\xbe\xbf\xbf\xbf\xc0\xc0\xc0\xc1\xc1\xc1\xc2\xc2\xc2\xc3\xc3\xc3\xc4\xc4\xc4\xc5\xc5\xc5\xc6\xc6\xc6\xc7\xc7\xc7\xc8\xc8\xc8\xc9\xc9\xc9\xca\xca\xca\xcb\xcb\xcb\xcc\xcc\xcc\xcd\xcd\xcd\xce\xce\xce\xcf\xcf\xcf\xd0\xd0\xd0\xd1\xd1\xd1\xd2\xd2\xd2\xd3\xd3\xd3\xd4\xd4\xd4\xd5\xd5\xd5\xd6\xd6\xd6\xd7\xd7\xd7\xd8\xd8\xd8\xd9\xd9\xd9\xda\xda\xda\xdb\xdb\xdb\xdc\xdc\xdc\xdd\xdd\xdd\xde\xde\xde\xdf\xdf\xdf\xe0\xe0\xe0\xe1\xe1\xe1\xe2\xe2\xe2\xe3\xe3\xe3\xe4\xe4\xe4\xe5\xe5\xe5\xe6\xe6\xe6\xe7\xe7\xe7\xe8\xe8\xe8\xe9\xe9\xe9\xea\xea\xea\xeb\xeb\xeb\xec\xec\xec\xed\xed\xed\xee\xee\xee\xef\xef\xef\xf0\xf0\xf0\xf1\xf1\xf1\xf2\xf2\xf2\xf3\xf3\xf3\xf4\xf4\xf4\xf5\xf5\xf5\xf6\xf6\xf6\xf7\xf7\xf7\xf8\xf8\xf8\xf9\xf9\xf9\xfa\xfa\xfa\xfb\xfb\xfb\xfc\xfc\xfc\xfd\xfd\xfd\xfe\xfe\xfe\xff\xff\xff"  # noqa: E501

                if grayscale_palette.startswith(palette):
                    # ------- If all colors are gray, white or black, ditch palette
                    self._mode = "1" if file_info["colors"] <= 2 else "L"
                    raw_mode = self.mode
                else:
                    self._mode = "P"
                    self.palette = ImagePalette.raw(
                        "BGRX" if padding == 4 else "BGR", palette
                    )

        # ---------------------------- Finally set the tile data for the plugin
        self.info["compression"] = file_info["compression"]
        args: list[Any] = [raw_mode]
        if decoder_name == "bmp_rle":
            args.append(file_info["compression"] == self.COMPRESSIONS["RLE4"])
        else:
            assert isinstance(file_info["width"], int)
            args.append(((file_info["width"] * file_info["bits"] + 31) >> 3) & (~3))
        args.append(file_info["direction"])
        self.tile = [
            ImageFile._Tile(
                decoder_name,
                (0, 0, file_info["width"], file_info["height"]),
                offset or self.fp.tell(),
                tuple(args),
            )
        ]

    def _open(self) -> None:
        """Open file, check magic number and read header"""
        # read 14 bytes: magic number, filesize, reserved, header final offset
        assert self.fp is not None
        head_data = self.fp.read(14)
        # choke if the file does not have the required magic bytes
        if not _accept(head_data):
            msg = "Not a BMP file"
            raise SyntaxError(msg)
        # read the start position of the BMP image data (u32)
        offset = i32(head_data, 10)
        # load bitmap information (offset=raster info)
        self._bitmap(offset=offset)


class BmpRleDecoder(ImageFile.PyDecoder):
    _pulls_fd = True

    def decode(self, buffer: Image.DecoderInput) -> tuple[int, int]:
        assert self.fd is not None
        rle4 = self.args[1]
        data = bytearray()
        x = 0
        dest_length = self.state.xsize * self.state.ysize
        while len(data) < dest_length:
            pixels = self.fd.read(1)
            byte = self.fd.read(1)
            if not pixels or not byte:
                break
            num_pixels = pixels[0]
            if num_pixels:
                # encoded mode
                if x + num_pixels > self.state.xsize:
                    # Too much data for row
                    num_pixels = max(0, self.state.xsize - x)
                if rle4:
                    first_pixel = o8(byte[0] >> 4)
                    second_pixel = o8(byte[0] & 0x0F)
                    for index in range(num_pixels):
                        if index % 2 == 0:
                            data += first_pixel
                        else:
                            data += second_pixel
                else:
                    data += byte * num_pixels
                x += num_pixels
            else:
                if byte[0] == 0:
                    # end of line
                    while len(data) % self.state.xsize != 0:
                        data += b"\x00"
                    x = 0
                elif byte[0] == 1:
                    # end of bitmap
                    break
                elif byte[0] == 2:
                    # delta
                    bytes_read = self.fd.read(2)
                    if len(bytes_read) < 2:
                        break
                    right, up = bytes_read
                    data += b"\x00" * min(
                        dest_length - len(data), right + up * self.state.xsize
                    )
                    x = len(data) % self.state.xsize
                else:
                    # absolute mode
                    data_count = min(dest_length - len(data), byte[0])
                    if rle4:
                        # 2 pixels per byte, padded up to a whole byte
                        byte_count = (data_count + 1) // 2
                        bytes_read = self.fd.read(byte_count)
                        for i, byte_read in enumerate(bytes_read):
                            data += o8(byte_read >> 4)
                            if i * 2 + 1 < data_count:
                                data += o8(byte_read & 0x0F)
                    else:
                        byte_count = data_count
                        bytes_read = self.fd.read(byte_count)
                        data += bytes_read
                    if len(bytes_read) < byte_count or len(data) == dest_length:
                        break
                    x += byte[0]

                    # align to 16-bit word boundary
                    if self.fd.tell() % 2 != 0:
                        self.fd.seek(1, os.SEEK_CUR)
        rawmode = "L" if self.mode in {"1", "L"} else "P"
        self.set_as_raw(bytes(data), rawmode, (0, self.args[-1]))
        return -1, 0


# =============================================================================
# Image plugin for the DIB format (BMP alias)
# =============================================================================
class DibImageFile(BmpImageFile):
    format = "DIB"
    format_description = "Windows Bitmap"

    def _open(self) -> None:
        self._bitmap()


#
# --------------------------------------------------------------------
# Write BMP file


SAVE = {
    "1": ("1", 1, 2),
    "L": ("L", 8, 256),
    "P": ("P", 8, 256),
    "RGB": ("BGR", 24, 0),
    "RGBA": ("BGRA", 32, 0),
}


def _dib_save(im: Image.Image, fp: IO[bytes], filename: str | bytes) -> None:
    _save(im, fp, filename, False)


def _save(
    im: Image.Image, fp: IO[bytes], filename: str | bytes, bitmap_header: bool = True
) -> None:
    try:
        rawmode, bits, colors = SAVE[im.mode]
    except KeyError as e:
        msg = f"cannot write mode {im.mode} as BMP"
        raise OSError(msg) from e

    info = im.encoderinfo

    dpi = info.get("dpi", (96, 96))

    # 1 meter == 39.3701 inches
    ppm = tuple(int(x * 39.3701 + 0.5) for x in dpi)

    stride = ((im.size[0] * bits + 7) // 8 + 3) & (~3)
    # Use a BITMAPV4HEADER for RGBA BMP images (not DIB)
    header = 108 if im.mode == "RGBA" and bitmap_header else 40
    image = stride * im.size[1]

    if im.mode == "1":
        palette = b"".join(o8(i) * 3 + b"\x00" for i in (0, 255))
    elif im.mode == "L":
        palette = b"".join(o8(i) * 3 + b"\x00" for i in range(256))
    elif im.mode == "P":
        # Colors used should not be zero, as that is treated as the maximum
        palette = im.im.getpalette("BGRX") or b"\x00\x00\x00\x00"
        colors = len(palette) // 4
    else:
        palette = None

    # bitmap header
    if bitmap_header:
        offset = 14 + header + colors * 4
        file_size = offset + image
        if file_size > 2**32 - 1:
            msg = "File size is too large for the BMP format"
            raise ValueError(msg)
        fp.write(
            b"BM"  # file type (magic)
            + o32(file_size)  # file size
            + o32(0)  # reserved
            + o32(offset)  # image data offset
        )

    # bitmap info header
    fp.write(
        o32(header)  # info header size
        + o32(im.size[0])  # width
        + o32(im.size[1])  # height
        + o16(1)  # planes
        + o16(bits)  # depth
        + o32(BmpImageFile.COMPRESSIONS["BITFIELDS" if header == 108 else "RAW"])
        + o32(image)  # size of bitmap
        + o32(ppm[0])  # resolution
        + o32(ppm[1])  # resolution
        + o32(colors)  # colors used
        + o32(colors)  # colors important
    )

    if header == 108:
        # BITMAPV4HEADER
        fp.write(
            o32(0x00FF0000)  # red mask
            + o32(0x0000FF00)  # green mask
            + o32(0x000000FF)  # blue mask
            + o32(0xFF000000)  # alpha mask
            + b"sRGB"[::-1]  # LCS_sRGB color space
            + b"\0" * 48  # endpoints and gamma
        )

    if palette:
        fp.write(palette)

    ImageFile._save(im, fp, [ImageFile._Tile("raw", args=(rawmode, stride, -1))])


#
# --------------------------------------------------------------------
# Registry


Image.register_open(BmpImageFile.format, BmpImageFile, _accept)
Image.register_save(BmpImageFile.format, _save)

Image.register_extension(BmpImageFile.format, ".bmp")

Image.register_mime(BmpImageFile.format, "image/bmp")

Image.register_decoder("bmp_rle", BmpRleDecoder)

Image.register_open(DibImageFile.format, DibImageFile, _dib_accept)
Image.register_save(DibImageFile.format, _dib_save)

Image.register_extension(DibImageFile.format, ".dib")

Image.register_mime(DibImageFile.format, "image/bmp")
