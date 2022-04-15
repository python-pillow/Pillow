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


from . import Image, ImageFile
from ._binary import i16be as i16
from ._binary import o8
from ._binary import o32le as o32

#
# --------------------------------------------------------------------

b_whitespace = b"\x20\x09\x0a\x0b\x0c\x0d"

MODES = {
    # standard
    b"P4": "1",
    b"P5": "L",
    b"P6": "RGB",
    # extensions
    b"P0CMYK": "CMYK",
    # PIL extensions (for test purposes only)
    b"PyP": "P",
    b"PyRGBA": "RGBA",
    b"PyCMYK": "CMYK",
}


def _accept(prefix):
    return prefix[0:1] == b"P" and prefix[1] in b"0456y"


##
# Image plugin for PBM, PGM, and PPM images.


class PpmImageFile(ImageFile.ImageFile):

    format = "PPM"
    format_description = "Pbmplus image"

    def _read_magic(self):
        magic = b""
        # read until whitespace or longest available magic number
        for _ in range(6):
            c = self.fp.read(1)
            if not c or c in b_whitespace:
                break
            magic += c
        return magic

    def _read_token(self):
        token = b""
        while len(token) <= 10:  # read until next whitespace or limit of 10 characters
            c = self.fp.read(1)
            if not c:
                break
            elif c in b_whitespace:  # token ended
                if not token:
                    # skip whitespace at start
                    continue
                break
            elif c == b"#":
                # ignores rest of the line; stops at CR, LF or EOF
                while self.fp.read(1) not in b"\r\n":
                    pass
                continue
            token += c
        if not token:
            # Token was not even 1 byte
            raise ValueError("Reached EOF while reading header")
        elif len(token) > 10:
            raise ValueError(f"Token too long in file header: {token}")
        return token

    def _open(self):
        magic_number = self._read_magic()
        try:
            mode = MODES[magic_number]
        except KeyError:
            raise SyntaxError("not a PPM file")

        self.custom_mimetype = {
            b"P4": "image/x-portable-bitmap",
            b"P5": "image/x-portable-graymap",
            b"P6": "image/x-portable-pixmap",
        }.get(magic_number)

        if mode == "1":
            self.mode = "1"
            rawmode = "1;I"
        else:
            self.mode = rawmode = mode

        decoder_name = "raw"
        for ix in range(3):
            token = int(self._read_token())
            if ix == 0:  # token is the x size
                xsize = token
            elif ix == 1:  # token is the y size
                ysize = token
                if mode == "1":
                    break
            elif ix == 2:  # token is maxval
                maxval = token
                if maxval > 255 and mode == "L":
                    self.mode = "I"

                # If maxval matches a bit depth, use the raw decoder directly
                if maxval == 65535 and mode == "L":
                    rawmode = "I;16B"
                elif maxval != 255:
                    decoder_name = "ppm"
        args = (rawmode, 0, 1) if decoder_name == "raw" else (rawmode, maxval)

        self._size = xsize, ysize
        self.tile = [(decoder_name, (0, 0, xsize, ysize), self.fp.tell(), args)]


class PpmDecoder(ImageFile.PyDecoder):
    _pulls_fd = True

    def decode(self, buffer):
        data = bytearray()
        maxval = min(self.args[-1], 65535)
        in_byte_count = 1 if maxval < 256 else 2
        out_byte_count = 4 if self.mode == "I" else 1
        out_max = 65535 if self.mode == "I" else 255
        bands = Image.getmodebands(self.mode)
        while len(data) < self.state.xsize * self.state.ysize * bands * out_byte_count:
            pixels = self.fd.read(in_byte_count * bands)
            if len(pixels) < in_byte_count * bands:
                # eof
                break
            for b in range(bands):
                value = (
                    pixels[b] if in_byte_count == 1 else i16(pixels, b * in_byte_count)
                )
                value = min(out_max, round(value / maxval * out_max))
                data += o32(value) if self.mode == "I" else o8(value)
        rawmode = "I;32" if self.mode == "I" else self.mode
        self.set_as_raw(bytes(data), (rawmode, 0, 1))
        return -1, 0


#
# --------------------------------------------------------------------


def _save(im, fp, filename):
    if im.mode == "1":
        rawmode, head = "1;I", b"P4"
    elif im.mode == "L":
        rawmode, head = "L", b"P5"
    elif im.mode == "I":
        rawmode, head = "I;16B", b"P5"
    elif im.mode in ("RGB", "RGBA"):
        rawmode, head = "RGB", b"P6"
    else:
        raise OSError(f"cannot write mode {im.mode} as PPM")
    fp.write(head + b"\n%d %d\n" % im.size)
    if head == b"P6":
        fp.write(b"255\n")
    elif head == b"P5":
        if rawmode == "L":
            fp.write(b"255\n")
        else:
            fp.write(b"65535\n")
    ImageFile._save(im, fp, [("raw", (0, 0) + im.size, 0, (rawmode, 0, 1))])

    # ALTERNATIVE: save via builtin debug function
    # im._dump(filename)


#
# --------------------------------------------------------------------


Image.register_open(PpmImageFile.format, PpmImageFile, _accept)
Image.register_save(PpmImageFile.format, _save)

Image.register_decoder("ppm", PpmDecoder)

Image.register_extensions(PpmImageFile.format, [".pbm", ".pgm", ".ppm", ".pnm"])

Image.register_mime(PpmImageFile.format, "image/x-portable-anymap")
