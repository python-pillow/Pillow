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

__lazy_modules__ = {"gzip", "math", "zlib"}

import gzip
import math
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
            and headers[b"ZCMPTYPE"] == b"'GZIP_1  '"
        ):
            no_prefix_size = self._get_size(headers, prefix) or (0, 0)
            number_of_bits = int(headers[b"BITPIX"])
            offset = no_prefix_size[0] * no_prefix_size[1] * (number_of_bits // 8)

            prefix = b"Z"
            decoder_name = "fits_gzip"

        size = self._get_size(headers, prefix)
        if not size:
            return "", 0, ()

        self._size = size

        number_of_bits = int(headers[prefix + b"BITPIX"])
        if number_of_bits == 8:
            self._mode = rawmode = "L"
        elif number_of_bits == 16:
            # FITS 16-bit integers are signed (FITS Standard 4.0, Section 5.2);
            # unsigned data is stored as signed with BZERO=32768
            self._mode = "I"
            rawmode = "I;16BS"
        elif number_of_bits == 32:
            self._mode = "I"
            rawmode = "I;32B"
        elif number_of_bits == -32 or (decoder_name == "raw" and number_of_bits == -64):
            self._mode = "F"
            rawmode = f"F;{number_of_bits * -1}BF"
        else:
            msg = "Unsupported number of bits"
            raise OSError(msg)

        # The physical value is BZERO + BSCALE * array value (FITS Standard 4.0,
        # Section 4.4.2.5). Scaling is left to the caller; the keywords are
        # exposed in im.info.
        for keyword in (b"BZERO", b"BSCALE"):
            value = headers.get(keyword)
            if value is None:
                continue
            try:
                # parse integers directly, so values beyond float precision survive
                number: int | float = int(value)
            except ValueError:
                try:
                    number = float(value.replace(b"D", b"E"))
                except ValueError:
                    continue
            self.info[keyword.decode("ascii")] = number

        args: tuple[str | int, ...]
        if decoder_name == "raw":
            args = (rawmode, 0, -1)
        else:
            args = (number_of_bits,)
        return decoder_name, offset, args


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
            # The decompressed payload is either widened to 4-byte groups, as in
            # existing files, or holds consecutive samples (see #10309)
            widened = len(value) == self.state.xsize * self.state.ysize * 4
            for y in range(self.state.ysize):
                row = bytearray()
                for x in range(self.state.xsize):
                    if number_of_bytes == 2:
                        # 16-bit integers are signed; expand to the 4-byte "I" rawmode
                        sample = (
                            value[offset + 2 : offset + 4]
                            if widened
                            else value[offset : offset + 2]
                        )
                        pixel = int.from_bytes(sample, "big", signed=True)
                        row += pixel.to_bytes(4, "little", signed=True)
                    elif widened:
                        row += value[offset + 4 - number_of_bytes : offset + 4][::-1]
                    else:
                        row += value[offset : offset + number_of_bytes][::-1]
                    offset += 4 if widened else number_of_bytes
                rows.append(row)
        data = bytes([pixel for row in rows[::-1] for pixel in row])
        # The rows are little-endian; the default rawmodes for "I" and "F"
        # are native-endian, so pass explicit little-endian ones for big-endian hosts
        if self.mode == "I":
            self.set_as_raw(data, "I;32S")
        elif self.mode == "F":
            self.set_as_raw(data, "F;32F")
        else:
            self.set_as_raw(data)
        return -1, 0


# --------------------------------------------------------------------
# Registry

Image.register_open(FitsImageFile.format, FitsImageFile, _accept)
Image.register_decoder("fits_gzip", FitsGzipDecoder)

Image.register_extensions(FitsImageFile.format, [".fit", ".fits"])
