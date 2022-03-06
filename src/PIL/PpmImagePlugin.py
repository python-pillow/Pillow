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

#
# --------------------------------------------------------------------

b_whitespace = b"\x20\x09\x0a\x0b\x0c\x0d"

MODES = {
    # standard, plain
    b"P1": ("ppm_plain", "1"),
    b"P2": ("ppm_plain", "L"),
    b"P3": ("ppm_plain", "RGB"),
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
            decoder, mode = MODES[magic_number]
        except KeyError:
            raise SyntaxError("not a PPM file")

        self.custom_mimetype = {
            b"P1": "image/x-portable-bitmap",
            b"P2": "image/x-portable-graymap",
            b"P3": "image/x-portable-pixmap",
            b"P4": "image/x-portable-bitmap",
            b"P5": "image/x-portable-graymap",
            b"P6": "image/x-portable-pixmap",
        }.get(magic_number)

        for ix in range(3):
            token = int(self._read_token())
            if ix == 0:  # token is the x size
                xsize = token
            elif ix == 1:  # token is the y size
                ysize = token
                if mode == "1":
                    self.mode = "1"
                    rawmode = "1;I"
                    break
                else:
                    self.mode = rawmode = mode
            elif ix == 2:  # token is maxval
                maxval = token
                if maxval > 255:
                    if not mode == "L":
                        raise ValueError(f"Too many colors for band: {maxval}")
                    if maxval < 2**16:
                        self.mode = "I"
                        rawmode = "I;16B"
                    else:
                        self.mode = "I"
                        rawmode = "I;32B"

        self._size = xsize, ysize
        self.tile = [
            (
                decoder,  # decoder
                (0, 0, xsize, ysize),  # region: whole image
                self.fp.tell(),  # offset to image data
                (rawmode, 0, 1),  # parameters for decoder
            )
        ]


#
# --------------------------------------------------------------------


class PpmPlainDecoder(ImageFile.PyDecoder):
    _pulls_fd = True

    def _read_block(self, block_size=10 ** 6):
        return bytearray(self.fd.read(block_size))

    def _find_comment_end(self, block, start=0):
        a = block.find(b"\n", start)
        b = block.find(b"\r", start)
        return min(a, b) if a * b > 0 else max(a, b)  # lowest nonnegative index (or -1)

    def _ignore_comments(self, block):
        """
        Deletes comments from block. If comment does not end in this
        block, raises a flag.
        """

        comment_spans = False
        while True:
            comment_start = block.find(b"#")  # look for next comment
            if comment_start == -1:  # no comment found
                break
            comment_end = self._find_comment_end(block, comment_start)
            if comment_end != -1:  # comment ends in this block
                block = (
                    block[:comment_start] + block[comment_end + 1 :]
                )  # delete comment
            else:  # last comment continues to next block(s)
                block = block[:comment_start]
                comment_spans = True
                break
        return block, comment_spans

    def _decode_bitonal(self):
        """
        The reason this is a separate method is that in the plain PBM
        format all data tokens are exactly one byte, and so the
        inter-token whitespace is optional.
        """
        decoded_data = bytearray()
        total_tokens = self.size

        comment_spans = False
        tokens_read = 0
        while True:
            block = self._read_block()  # read next block
            if not block:
                raise ValueError("Reached EOF while reading data")

            while block and comment_spans:
                comment_end = self._find_comment_end(block)
                if comment_end != -1:  # comment ends in this block
                    comment_spans = False
                    block = block[comment_end + 1 :]  # delete tail of previous comment
                else:  # comment spans whole block
                    block = self._read_block()

            block, comment_spans = self._ignore_comments(block)

            tokens = b"".join(block.split())

            for token in tokens:
                if token in (48, 49):
                    tokens_read += 1
                else:
                    raise ValueError(f"Invalid token for this mode: {bytes([token])}")

                decoded_data.append(token)
                if tokens_read == total_tokens:  # finished!
                    invert = bytes.maketrans(b"01", b"\xFF\x00")
                    decoded_data = decoded_data.translate(invert)
                    return decoded_data

    def _decode_blocks(self, channels=1, depth=8):
        decoded_data = bytearray()
        if depth == 32:
            maxval = 2 ** 31 - 1  # HACK: 32-bit grayscale uses signed int
        else:
            maxval = 2 ** depth - 1  # FIXME: should be passed by _open
        max_len = 10
        bytes_per_sample = depth // 8
        total_tokens = self.size * channels

        token_spans = False
        comment_spans = False
        half_token = False
        tokens_read = 0
        while True:
            block = self._read_block()  # read next block
            if not block:
                if token_spans:
                    block = bytearray(b" ")  # flush half_token
                else:
                    raise ValueError("Reached EOF while reading data")

            while block and comment_spans:
                comment_end = self._find_comment_end(block)
                if comment_end != -1:  # comment ends in this block
                    block = block[comment_end + 1 :]  # delete tail of previous comment
                    break
                else:  # comment spans whole block
                    block = self._read_block()

            block, comment_spans = self._ignore_comments(block)

            if token_spans:
                block = half_token + block  # stitch half_token to new block
                token_spans = False

            tokens = block.split()

            if block and not block[-1:].isspace():  # block might split token
                token_spans = True
                half_token = tokens.pop()  # save half token for later
                if len(half_token) > max_len:  # prevent buildup of half_token
                    raise ValueError(
                        f"Token too long found in data: {half_token[:max_len + 1]}"
                    )

            for token in tokens:
                if len(token) > max_len:
                    raise ValueError(
                        f"Token too long found in data: {token[:max_len + 1]}"
                    )
                try:
                    token = int(token)
                except ValueError:
                    raise ValueError(
                        f"Non-decimal-ASCII found in data: {token}"
                    ) from None
                tokens_read += 1
                if token > maxval:
                    raise ValueError(f"Channel value too large for this mode: {token}")
                decoded_data += token.to_bytes(bytes_per_sample, "big")
                if tokens_read == total_tokens:  # finished!
                    return decoded_data

    def decode(self, buffer):
        self.size = self.state.xsize * self.state.ysize
        rawmode = self.args[0]

        if self.mode == "1":
            decoded_data = self._decode_bitonal()
            rawmode = "1;8"
        elif self.mode == "L":
            decoded_data = self._decode_blocks(channels=1, depth=8)
        elif self.mode == "I":
            if rawmode == "I;16B":
                decoded_data = self._decode_blocks(channels=1, depth=16)
            elif rawmode == "I;32B":
                decoded_data = self._decode_blocks(channels=1, depth=32)
        elif self.mode == "RGB":
            decoded_data = self._decode_blocks(channels=3, depth=8)

        self.set_as_raw(bytes(decoded_data), rawmode)
        return -1, 0


#
# --------------------------------------------------------------------


def _save(im, fp, filename):
    if im.mode == "1":
        rawmode, head = "1;I", b"P4"
    elif im.mode == "L":
        rawmode, head = "L", b"P5"
    elif im.mode == "I":
        if im.getextrema()[1] < 2**16:
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

Image.register_decoder("ppm_plain", PpmPlainDecoder)
Image.register_open(PpmImageFile.format, PpmImageFile, _accept)
Image.register_save(PpmImageFile.format, _save)

Image.register_extensions(PpmImageFile.format, [".pbm", ".pgm", ".ppm", ".pnm"])

Image.register_mime(PpmImageFile.format, "image/x-portable-anymap")
