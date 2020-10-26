#
# The Python Imaging Library.
# $Id$
#
# PPM support for PIL
#
# History:
#       96-03-24 fl     Created
#       98-03-06 fl     Write RGBA images (as RGB, that is)
#
# Copyright (c) Secret Labs AB 1997-98.
# Copyright (c) Fredrik Lundh 1996.
#
# See the README file for information on usage and redistribution.
#

import struct

from . import Image, ImageFile

#
# --------------------------------------------------------------------

b_whitespace = b"\x20\x09\x0a\x0b\x0c\x0d"

MODES = {
    # standard, plain
    b"P1": ("PPM", "1"),
    b"P2": ("PPM", "L"),
    b"P3": ("PPM", "RGB"),
    # standard, raw
    b"P4": ("raw", "1"),
    b"P5": ("raw", "L"),
    b"P6": ("raw", "RGB"),
    # extensions
    b"P0CMYK": ("raw", "CMYK"),
    # PIL extensions (for test purposes only)
    b"PyP": ("raw", "P"),
    b"PyRGBA": ("raw", "RGBA"),
    b"PyCMYK": ("raw", "CMYK"),
}


def _accept(prefix):
    return prefix[0:1] == b"P" and prefix[1] in b"0123456y"


##
# Image plugin for PBM, PGM, and PPM images.


class PpmImageFile(ImageFile.ImageFile):

    format = "PPM"
    format_description = "Pbmplus image"

    def _token(self, s=b""):
        while True:  # read until next whitespace
            c = self.fp.read(1)
            if not c or c in b_whitespace:
                break
            if c > b"\x79":
                raise ValueError("Expected ASCII value, found binary")
            s = s + c
            if len(s) > 9:
                raise ValueError("Expected int, got > 9 digits")
        return s

    def _open(self):

        # check magic
        s = self.fp.read(1)
        if s != b"P":
            raise SyntaxError("not a PPM file")
        magic_number = self._token(s)
        decoder, mode = MODES[magic_number]

        self.custom_mimetype = {
            b"P1": "image/x-portable-bitmap",
            b"P2": "image/x-portable-graymap",
            b"P3": "image/x-portable-pixmap",
            b"P4": "image/x-portable-bitmap",
            b"P5": "image/x-portable-graymap",
            b"P6": "image/x-portable-pixmap",
        }.get(magic_number)

        if mode == "1":
            self.mode = "1"
            rawmode = "1;I"
        else:
            self.mode = rawmode = mode

        for ix in range(3):
            while True:
                while True:
                    s = self.fp.read(1)
                    if s not in b_whitespace:
                        break
                    if s == b"":
                        raise ValueError("File does not extend beyond magic number")
                if s != b"#":
                    break
                s = self.fp.readline()
            s = int(self._token(s))
            if ix == 0:
                xsize = s
            elif ix == 1:
                ysize = s
                if mode == "1":
                    break
            elif ix == 2:
                # maxgrey
                if s > 255:
                    if not mode == "L":
                        raise ValueError(f"Too many colors for band: {s}")
                    if s < 2 ** 16:
                        self.mode = "I"
                        rawmode = "I;16B"
                    else:
                        self.mode = "I"
                        rawmode = "I;32B"

        self._size = xsize, ysize
        self.tile = [(decoder, (0, 0, xsize, ysize), self.fp.tell(), (rawmode, 0, 1))]


class PpmPlainDecoder(ImageFile.PyDecoder):
    _pulls_fd = True

    def decode(self, buffer):
        data = b""
        size = self.state.xsize * self.state.ysize

        if self.mode == "1":
            translate = bytes.maketrans(b"01", b"\xFF\x00")
            delete = bytes(range(48)) + bytes(range(50, 256))

        for line in self.fd:
            line = line[: line.find("#")]
            if self.mode == "1":
                bytes_per_pixel = 1
                data += line.translate(translate, delete)
            else:
                values = map(int, line.split())
                if self.mode == "L":
                    bytes_per_pixel = 1
                    data += bytes(values)
                elif self.mode == "I;16B":
                    bytes_per_pixel = 2
                    values = list(values)
                    data += struct.pack(f">{len(values)}H", *values)
                elif self.mode == "I;32B":
                    bytes_per_pixel = 4
                    values = list(values)
                    data += struct.pack(f">{len(values)}L", *values)
                else:
                    bytes_per_pixel = 3
                    data += bytes(values)

            if len(data) >= size * bytes_per_pixel:
                break

        if self.mode == "1":
            self.im.putdata(data[0:size])
        else:
            self.set_as_raw(data, rawmode=self.args[0])

        return -1, 0


def _save(im, fp, filename):
    if im.mode == "1":
        rawmode, head = "1;I", b"P4"
    elif im.mode == "L":
        rawmode, head = "L", b"P5"
    elif im.mode == "I":
        if im.getextrema()[1] < 2 ** 16:
            rawmode, head = "I;16B", b"P5"
        else:
            rawmode, head = "I;32B", b"P5"
    elif im.mode == "RGB":
        rawmode, head = "RGB", b"P6"
    elif im.mode == "RGBA":
        rawmode, head = "RGB", b"P6"
    else:
        raise OSError(f"cannot write mode {im.mode} as PPM")
    fp.write(head + ("\n%d %d\n" % im.size).encode("ascii"))
    if head == b"P6":
        fp.write(b"255\n")
    if head == b"P5":
        if rawmode == "L":
            fp.write(b"255\n")
        elif rawmode == "I;16B":
            fp.write(b"65535\n")
        elif rawmode == "I;32B":
            fp.write(b"2147483648\n")
    ImageFile._save(im, fp, [("raw", (0, 0) + im.size, 0, (rawmode, 0, 1))])

    # ALTERNATIVE: save via builtin debug function
    # im._dump(filename)


#
# --------------------------------------------------------------------


Image.register_decoder("PPM", PpmPlainDecoder)
Image.register_open(PpmImageFile.format, PpmImageFile, _accept)
Image.register_save(PpmImageFile.format, _save)

Image.register_extensions(PpmImageFile.format, [".pbm", ".pgm", ".ppm", ".pnm"])

Image.register_mime(PpmImageFile.format, "image/x-portable-anymap")
