#
# The Python Imaging Library
# $Id$
#
# FITS file handling
#
# Copyright (c) 1998-2003 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#
from __future__ import annotations

__lazy_modules__ = {"gzip", "math", "re", "zlib"}

import gzip
import math
import re
import zlib

from . import Image, ImageFile


def _accept(prefix: bytes) -> bool:
    return prefix.startswith(b"SIMPLE")


class FitsImageFile(ImageFile.ImageFile):
    format = "FITS"
    format_description = "FITS"

    def _open(self) -> None:
        assert self.fp is not None

        headers: dict[bytes, bytes] = {}
        header_in_progress = False
        decoder_name = ""
        while True:
            header = self.fp.read(80)
            if not header:
                msg = "Truncated FITS file"
                raise OSError(msg)
            keyword = header[:8].strip()
            if keyword in (b"SIMPLE", b"XTENSION"):
                header_in_progress = True
            elif headers and not header_in_progress:
                # This is now a data unit
                break
            elif keyword == b"END":
                # Seek to the end of the header unit
                self.fp.seek(math.ceil(self.fp.tell() / 2880) * 2880)
                if not decoder_name:
                    decoder_name, offset, args = self._parse_headers(headers)
                if decoder_name == "fits_rice":
                    self.tile = self._get_rice_tiles(headers, self.fp.tell())
                    return

                header_in_progress = False
                continue

            if decoder_name:
                # Keep going to read past the headers
                continue

            value = header[8:].split(b"/")[0].strip()
            if value.startswith(b"="):
                value = value[1:].strip()
            if not headers and (not _accept(keyword) or value != b"T"):
                msg = "Not a FITS file"
                raise SyntaxError(msg)
            headers[keyword] = value

        if not decoder_name:
            msg = "No image data"
            raise ValueError(msg)

        offset += self.fp.tell() - 80
        self.tile = [ImageFile._Tile(decoder_name, None, offset, args)]

    def _get_size(
        self, headers: dict[bytes, bytes], prefix: bytes
    ) -> tuple[int, int] | None:
        naxis = int(headers[prefix + b"NAXIS"])
        if naxis == 0:
            return None

        if naxis == 1:
            return 1, int(headers[prefix + b"NAXIS1"])
        else:
            return int(headers[prefix + b"NAXIS1"]), int(headers[prefix + b"NAXIS2"])

    def _parse_headers(
        self, headers: dict[bytes, bytes]
    ) -> tuple[str, int, tuple[str | int, ...]]:
        prefix = b""
        decoder_name = "raw"
        offset = 0
        if (
            headers.get(b"XTENSION") == b"'BINTABLE'"
            and headers.get(b"ZIMAGE") == b"T"
            and headers[b"ZCMPTYPE"].strip(b" '") in (b"GZIP_1", b"RICE_1", b"RICE_ONE")
        ):
            prefix = b"Z"
            if headers[b"ZCMPTYPE"].strip(b" '") in (b"RICE_1", b"RICE_ONE"):
                decoder_name = "fits_rice"
                if int(headers[b"ZNAXIS"]) not in (1, 2):
                    msg = "Unsupported FITS RICE image dimensions"
                    raise OSError(msg)
            else:
                no_prefix_size = self._get_size(headers, b"") or (0, 0)
                number_of_bits = int(headers[b"BITPIX"])
                offset = no_prefix_size[0] * no_prefix_size[1] * (number_of_bits // 8)
                decoder_name = "fits_gzip"

        size = self._get_size(headers, prefix)
        if not size:
            return "", 0, ()

        self._size = size

        number_of_bits = int(headers[prefix + b"BITPIX"])
        if decoder_name == "fits_rice" and number_of_bits not in (8, 16, 32):
            msg = "Unsupported FITS RICE pixel type"
            raise OSError(msg)
        if number_of_bits == 8:
            self._mode = rawmode = "L"
        elif number_of_bits == 16:
            if decoder_name == "fits_rice":
                self._mode = "I"
                rawmode = "I;16BS"
            else:
                self._mode = "I;16"
                rawmode = "I;16B"
        elif number_of_bits == 32:
            self._mode = "I"
            rawmode = "I;32B"
        elif number_of_bits == -32 or (decoder_name == "raw" and number_of_bits == -64):
            self._mode = "F"
            rawmode = f"F;{number_of_bits * -1}BF"
        else:
            msg = "Unsupported number of bits"
            raise OSError(msg)

        args: tuple[str | int, ...]
        if decoder_name == "raw":
            args = (rawmode, 0, -1)
        else:
            args = (number_of_bits,)
        return decoder_name, offset, args

    def _get_rice_tiles(
        self, headers: dict[bytes, bytes], data_offset: int
    ) -> list[ImageFile._Tile]:
        assert self.fp is not None
        if min(self.size) <= 0:
            msg = "Invalid FITS RICE image size"
            raise OSError(msg)
        Image._decompression_bomb_check(self.size)

        row_size = int(headers[b"NAXIS1"])
        row_count = int(headers[b"NAXIS2"])
        table_size = row_size * row_count
        heap_offset = int(headers.get(b"THEAP", table_size))
        heap_size = table_size + int(headers[b"PCOUNT"]) - heap_offset
        if row_size <= 0 or row_count <= 0 or heap_offset < table_size or heap_size < 0:
            msg = "Invalid FITS RICE heap"
            raise OSError(msg)

        column_offset = 0
        descriptor_offset = descriptor_size = 0
        widths = {
            b"L": 1,
            b"B": 1,
            b"I": 2,
            b"J": 4,
            b"K": 8,
            b"A": 1,
            b"E": 4,
            b"D": 8,
            b"C": 8,
            b"M": 16,
            b"P": 8,
            b"Q": 16,
        }
        for column in range(1, int(headers[b"TFIELDS"]) + 1):
            suffix = str(column).encode()
            form = headers[b"TFORM" + suffix].strip(b" '")
            match = re.fullmatch(
                rb"(\d*)([LXBIJKAEDCMPQ])(?:[LXBIJKAEDCM](?:\(\d+\))?)?", form
            )
            if match is None:
                msg = "Unsupported FITS RICE table column"
                raise OSError(msg)
            repeat = int(match[1] or b"1")
            code = match[2]
            if headers.get(b"TTYPE" + suffix, b"").strip(b" '") == b"COMPRESSED_DATA":
                if (
                    re.fullmatch(rb"1?[PQ]B(?:\(\d+\))?", form) is None
                    or descriptor_size
                ):
                    msg = "Invalid FITS RICE compressed data column"
                    raise OSError(msg)
                descriptor_offset = column_offset
                descriptor_size = widths[code]
            column_offset += (
                (repeat + 7) // 8 if code == b"X" else repeat * widths[code]
            )
        if not descriptor_size or column_offset != row_size:
            msg = "Invalid FITS RICE table row"
            raise OSError(msg)

        parameters = {}
        for keyword, value in headers.items():
            if keyword.startswith(b"ZNAME"):
                name = value.strip(b" '")
                if name in (b"BLOCKSIZE", b"BYTEPIX"):
                    parameters[name] = int(headers[b"ZVAL" + keyword[5:]])
        blocksize = parameters.get(b"BLOCKSIZE", 32)
        bytepix = parameters.get(b"BYTEPIX", 4)
        bitpix = int(headers[b"ZBITPIX"])
        if (
            not 0 < blocksize <= 2**31 - 1
            or bytepix not in (1, 2, 4)
            or bytepix * 8 < bitpix
        ):
            msg = "Invalid FITS RICE compression parameters"
            raise OSError(msg)

        naxis = int(headers[b"ZNAXIS"])
        width = int(headers[b"ZNAXIS1"])
        height = int(headers[b"ZNAXIS2"]) if naxis == 2 else 1
        tile_width = int(headers.get(b"ZTILE1", width))
        tile_height = int(headers.get(b"ZTILE2", 1)) if naxis == 2 else 1
        if tile_width <= 0 or tile_height <= 0:
            msg = "Invalid FITS RICE tile size"
            raise OSError(msg)
        tiles_across = (width + tile_width - 1) // tile_width
        tiles_down = (height + tile_height - 1) // tile_height
        if tiles_across * tiles_down != row_count:
            msg = "Invalid FITS RICE tile count"
            raise OSError(msg)

        tiles = []
        for row in range(row_count):
            self.fp.seek(data_offset + row * row_size + descriptor_offset)
            descriptor = ImageFile._safe_read(self.fp, descriptor_size)
            length = int.from_bytes(
                descriptor[: descriptor_size // 2], "big", signed=True
            )
            offset = int.from_bytes(
                descriptor[descriptor_size // 2 :], "big", signed=True
            )
            if length <= 0 or offset < 0 or offset + length > heap_size:
                msg = "Invalid FITS RICE tile descriptor"
                raise OSError(msg)
            x = row % tiles_across * tile_width
            y = row // tiles_across * tile_height
            x_end = min(x + tile_width, width)
            y_end = min(y + tile_height, height)
            extents = (
                (x, height - y_end, x_end, height - y)
                if naxis == 2
                else (0, width - x_end, 1, width - x)
            )
            tiles.append(
                ImageFile._Tile(
                    "fits_rice_tile",
                    extents,
                    data_offset + heap_offset + offset,
                    (
                        {8: "L", 16: "I;16BS", 32: "I;32BS"}[bitpix],
                        bytepix,
                        blocksize,
                        length,
                    ),
                )
            )
        return tiles


class FitsRiceDecoder(ImageFile.PyDecoder):
    _pulls_fd = True

    def decode(self, buffer: Image.DecoderInput) -> tuple[int, int]:
        assert self.fd is not None
        assert self.im is not None
        decoder = Image._getdecoder(self.mode, "fits_rice", self.args)
        try:
            decoder.setimage(self.im, self.state.extents())
            remaining = self.args[-1]
            pending = b""
            while True:
                if not pending:
                    pending = self.fd.read(min(remaining, ImageFile.MAXBLOCK))
                    remaining -= len(pending)
                    if not pending:
                        msg = "Truncated FITS Rice data"
                        raise OSError(msg)
                consumed, error = decoder.decode(pending)
                if error < 0:
                    msg = "Corrupt FITS Rice data"
                    raise OSError(msg)
                if consumed < 0:
                    return -1, 0
                pending = pending[consumed:]
        finally:
            decoder.cleanup()


class FitsGzipDecoder(ImageFile.PyDecoder):
    _pulls_fd = True

    def decode(self, buffer: Image.DecoderInput) -> tuple[int, int]:
        assert self.fd is not None
        with gzip.open(self.fd) as fp:
            try:
                value = fp.read(self.state.xsize * self.state.ysize * 4)
            except EOFError as e:
                msg = "Truncated FITS gzip data"
                raise OSError(msg) from e
            except zlib.error as e:
                msg = "Corrupt FITS gzip data"
                raise OSError(msg) from e

            rows = []
            offset = 0
            number_of_bytes = abs(self.args[0]) // 8
            for y in range(self.state.ysize):
                row = bytearray()
                for x in range(self.state.xsize):
                    row += value[
                        offset + 4 - 1 : offset + (4 - number_of_bytes) - 1 : -1
                    ]
                    offset += 4
                rows.append(row)
        self.set_as_raw(bytes([pixel for row in rows[::-1] for pixel in row]))
        return -1, 0


# --------------------------------------------------------------------
# Registry

Image.register_open(FitsImageFile.format, FitsImageFile, _accept)
Image.register_decoder("fits_gzip", FitsGzipDecoder)
Image.register_decoder("fits_rice_tile", FitsRiceDecoder)

Image.register_extensions(FitsImageFile.format, [".fit", ".fits"])
