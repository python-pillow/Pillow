#
# The Python Imaging Library.
# $Id$
#
# Windows Cursor support for PIL
#
# notes:
#       uses BmpImagePlugin.py to read the bitmap data.
#
# history:
#       96-05-27 fl     Created
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1996.
#
# See the README file for information on usage and redistribution.
#
from __future__ import annotations

from io import BytesIO
from math import ceil, log
from typing import IO

from . import BmpImagePlugin, IcoImagePlugin, Image, ImageFile
from ._binary import i16le as i16
from ._binary import i32le as i32
from ._binary import o8
from ._binary import o16le as o16
from ._binary import o32le as o32

#
# --------------------------------------------------------------------

_MAGIC = b"\x00\x00\x02\x00"


def _save(im: Image.Image, fp: IO[bytes], filename: str | bytes) -> None:
    fp.write(_MAGIC)
    bmp = im.encoderinfo.get("bitmap_format", "") == "bmp"
    s = im.encoderinfo.get(
        "sizes",
        [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    h = im.encoderinfo.get("hotspots", [(0, 0) for i in range(len(s))])

    if len(h) != len(s):
        msg = "Number of hotspots must be equal to number of cursor sizes"
        raise ValueError(msg)

    # sort and remove duplicate sizes
    sizes, hotspots = [], []
    for size, hotspot in sorted(zip(s, h), key=lambda x: x[0]):
        if size not in sizes:
            sizes.append(size)
            hotspots.append(hotspot)

    frames = []
    width, height = im.size
    for size in sizes:
        if size[0] > width or size[1] > height or size[0] > 256 or size[1] > 256:
            continue

        # TODO: invent a more convenient method for proportional scalings
        frame = im.copy()
        frame.thumbnail(size, Image.Resampling.LANCZOS, reducing_gap=None)
        frames.append(frame)

    fp.write(o16(len(frames)))  # idCount(2)
    offset = fp.tell() + len(frames) * 16
    for hotspot, frame in zip(hotspots, frames):
        width, height = frame.size
        # 0 means 256
        fp.write(o8(width if width < 256 else 0))  # bWidth(1)
        fp.write(o8(height if height < 256 else 0))  # bHeight(1)

        bits, colors = BmpImagePlugin.SAVE[frame.mode][1:] if bmp else (32, 0)
        fp.write(o8(colors))  # bColorCount(1)
        fp.write(b"\0")  # bReserved(1)
        fp.write(o16(hotspot[0]))  # x_hotspot(2)
        fp.write(o16(hotspot[1]))  # y_hotspot(2)

        image_io = BytesIO()
        if bmp:
            if bits != 32:
                and_mask = Image.new("1", size)
                ImageFile._save(
                    and_mask,
                    image_io,
                    [ImageFile._Tile("raw", (0, 0) + size, 0, ("1", 0, -1))],
                )

            frame.save(image_io, "dib")
        else:
            frame.save(image_io, "png")
        image_io.seek(0)
        image_bytes = image_io.read()
        if bmp:
            image_bytes = image_bytes[:8] + o32(height * 2) + image_bytes[12:]

        bytes_len = len(image_bytes)
        fp.write(o32(bytes_len))  # dwBytesInRes(4)
        fp.write(o32(offset))  # dwImageOffset(4)
        current = fp.tell()
        fp.seek(offset)
        fp.write(image_bytes)
        offset = offset + bytes_len
        fp.seek(current)


def _accept(prefix: bytes) -> bool:
    return prefix.startswith(_MAGIC)


##
# Image plugin for Windows Cursor files.
class CurFile(IcoImagePlugin.IcoFile):
    def __init__(self, buf: IO[bytes]) -> None:
        """
        Parse image from file-like object containing cur file data
        """

        # check if CUR
        s = buf.read(6)
        if not _accept(s):
            msg = "not a CUR file"
            raise SyntaxError(msg)

        self.buf = buf
        entry = []

        # Number of items in file
        self.nb_items = i16(s, 4)

        # Get headers for each item
        for _ in range(self.nb_items):
            s = buf.read(16)

            # See Wikipedia
            width = s[0] or 256
            height = s[1] or 256
            square = width * height

            size = i32(s, 8)

            # No. of colors in image (0 if >=8bpp)
            nb_color = s[2]

            # TODO: This needs further investigation. Cursor files do not really
            # specify their bpp like ICO's as those bits are used for the y_hotspot.
            # For now, bpp is calculated by subtracting the AND mask (equal to number
            # of pixels * 1bpp) and dividing by the number of pixels. This seems
            # to work well so far.
            BITMAP_INFO_HEADER_SIZE = 40
            bpp_without_and = ((size - BITMAP_INFO_HEADER_SIZE) * 8) // square
            if bpp_without_and != 32:
                bpp = ((size - BITMAP_INFO_HEADER_SIZE) * 8 - square) // square
            else:
                bpp = bpp_without_and

            entry.append(
                (
                    square,
                    IcoImagePlugin.IconHeader(
                        width=width,
                        height=height,
                        nb_color=nb_color,
                        reserved=s[3],
                        planes=0,
                        bpp=bpp,
                        size=size,
                        offset=i32(s, 12),
                        dim=(width, height),
                        square=square,
                        color_depth=bpp
                        or (nb_color != 0 and ceil(log(nb_color, 2)))
                        or 256,
                    ),
                    (i16(s, 4), i16(s, 6)),  # x, y
                )
            )

        entry = sorted(entry, key=lambda x: x[0], reverse=True)
        self.entry = [x[1] for x in entry]
        self.hotspots = [x[2] for x in entry]


class CurImageFile(IcoImagePlugin.IcoImageFile):
    """
    PIL read-only image support for Microsoft Windows .cur files.

    By default the largest resolution image in the file will be loaded. This
    can be changed by altering the 'size' attribute before calling 'load'.

    The info dictionary has a key 'sizes' that is a list of the sizes available
    in the icon file. It also contains key 'hotspots' that is a list of the
    cursor hotspots.

    Handles classic, XP and Vista icon formats.

    When saving, PNG compression is used. Support for this was only added in
    Windows Vista. If you are unable to view the icon in Windows, convert the
    image to "RGBA" mode before saving. This is an extension of the IcoImagePlugin.

    Raises:
        ValueError: The number of sizes and hotspots do not match.
        SyntaxError: The file is not a cursor file.
        TypeError: There are no cursors contained withing the file.
    """

    format = "CUR"
    format_description = "Windows Cursor"

    def _open(self) -> None:
        assert self.fp is not None
        self.ico = CurFile(self.fp)
        self.info["sizes"] = self.ico.sizes()
        self.info["hotspots"] = self.ico.hotspots
        if len(self.ico.entry) > 0:
            self.size = self.ico.entry[0].dim
        else:
            msg = "No cursors were found"
            raise TypeError(msg)
        self.load()


#
# --------------------------------------------------------------------

Image.register_open(CurImageFile.format, CurImageFile, _accept)
Image.register_save(CurImageFile.format, _save)
Image.register_extension(CurImageFile.format, ".cur")
