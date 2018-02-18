"""
Blizzard Mipmap Format (.blp)
Jerome Leclanche <jerome@leclan.ch>

The contents of this file are hereby released in the public domain (CC0)
Full text of the CC0 license:
  https://creativecommons.org/publicdomain/zero/1.0/

BLP1 files, used mostly in Warcraft III, are not fully supported.
All types of BLP2 files used in World of Warcraft are supported.

The BLP file structure consists of a header, up to 16 mipmaps of the
texture

Texture sizes must be powers of two, though the two dimensions do
not have to be equal; 512x256 is valid, but 512x200 is not.
The first mipmap (mipmap #0) is the full size image; each subsequent
mipmap halves both dimensions. The final mipmap should be 1x1.

BLP files come in many different flavours:
* JPEG-compressed (type == 0) - only supported for BLP1.
* RAW images (type == 1, encoding == 1). Each mipmap is stored as an
  array of 8-bit values, one per pixel, left to right, top to bottom.
  Each value is an index to the palette.
* DXT-compressed (type == 1, encoding == 2):
- DXT1 compression is used if alpha_encoding == 0.
  - An additional alpha bit is used if alpha_depth == 1.
  - DXT3 compression is used if alpha_encoding == 1.
  - DXT5 compression is used if alpha_encoding == 7.
"""

import struct
from io import BytesIO

from . import Image, ImageFile


BLP_FORMAT_JPEG = 0

BLP_ENCODING_UNCOMPRESSED = 1
BLP_ENCODING_DXT = 2
BLP_ENCODING_UNCOMPRESSED_RAW_BGRA = 3

BLP_ALPHA_ENCODING_DXT1 = 0
BLP_ALPHA_ENCODING_DXT3 = 1
BLP_ALPHA_ENCODING_DXT5 = 7


def unpack_565(i):
    return (
        ((i >> 11) & 0x1f) << 3,
        ((i >> 5) & 0x3f) << 2,
        (i & 0x1f) << 3
    )


def decode_dxt1(data, alpha=False):
    """
    input: one "row" of data (i.e. will produce 4*width pixels)
    """

    blocks = len(data) // 8  # number of blocks in row
    ret = (bytearray(), bytearray(), bytearray(), bytearray())

    for block in range(blocks):
        # Decode next 8-byte block.
        idx = block * 8
        color0, color1, bits = struct.unpack("<HHI", data[idx:idx + 8])

        r0, g0, b0 = unpack_565(color0)
        r1, g1, b1 = unpack_565(color1)

        # Decode this block into 4x4 pixels
        # Accumulate the results onto our 4 row accumulators
        for j in range(4):
            for i in range(4):
                # get next control op and generate a pixel

                control = bits & 3
                bits = bits >> 2

                a = 0xFF
                if control == 0:
                    r, g, b = r0, g0, b0
                elif control == 1:
                    r, g, b = r1, g1, b1
                elif control == 2:
                    if color0 > color1:
                        r = (2 * r0 + r1) // 3
                        g = (2 * g0 + g1) // 3
                        b = (2 * b0 + b1) // 3
                    else:
                        r = (r0 + r1) // 2
                        g = (g0 + g1) // 2
                        b = (b0 + b1) // 2
                elif control == 3:
                    if color0 > color1:
                        r = (2 * r1 + r0) // 3
                        g = (2 * g1 + g0) // 3
                        b = (2 * b1 + b0) // 3
                    else:
                        r, g, b, a = 0, 0, 0, 0

                if alpha:
                    ret[j].extend([r, g, b, a])
                else:
                    ret[j].extend([r, g, b])

    return ret


def decode_dxt3(data):
    """
    input: one "row" of data (i.e. will produce 4*width pixels)
    """

    blocks = len(data) // 16  # number of blocks in row
    ret = (bytearray(), bytearray(), bytearray(), bytearray())

    for block in range(blocks):
        idx = block * 16
        block = data[idx:idx + 16]
        # Decode next 16-byte block.
        bits = struct.unpack("<8B", block[:8])
        color0, color1 = struct.unpack("<HH", block[8:12])

        code, = struct.unpack("<I", block[12:])

        r0, g0, b0 = unpack_565(color0)
        r1, g1, b1 = unpack_565(color1)

        for j in range(4):
            high = False  # Do we want the higher bits?
            for i in range(4):
                alphacode_index = (4 * j + i) // 2
                a = bits[alphacode_index]
                if high:
                    high = False
                    a >>= 4
                else:
                    high = True
                    a &= 0xf
                a *= 17  # We get a value between 0 and 15

                color_code = (code >> 2 * (4 * j + i)) & 0x03

                if color_code == 0:
                    r, g, b = r0, g0, b0
                elif color_code == 1:
                    r, g, b = r1, g1, b1
                elif color_code == 2:
                    r = (2 * r0 + r1) // 3
                    g = (2 * g0 + g1) // 3
                    b = (2 * b0 + b1) // 3
                elif color_code == 3:
                    r = (2 * r1 + r0) // 3
                    g = (2 * g1 + g0) // 3
                    b = (2 * b1 + b0) // 3

                ret[j].extend([r, g, b, a])

    return ret


def decode_dxt5(data):
    """
    input: one "row" of data (i.e. will produce 4 * width pixels)
    """

    blocks = len(data) // 16  # number of blocks in row
    ret = (bytearray(), bytearray(), bytearray(), bytearray())

    for block in range(blocks):
        idx = block * 16
        block = data[idx:idx + 16]
        # Decode next 16-byte block.
        a0, a1 = struct.unpack("<BB", block[:2])

        bits = struct.unpack("<6B", block[2:8])
        alphacode1 = (
            bits[2] | (bits[3] << 8) | (bits[4] << 16) | (bits[5] << 24)
        )
        alphacode2 = bits[0] | (bits[1] << 8)

        color0, color1 = struct.unpack("<HH", block[8:12])

        code, = struct.unpack("<I", block[12:])

        r0, g0, b0 = unpack_565(color0)
        r1, g1, b1 = unpack_565(color1)

        for j in range(4):
            for i in range(4):
                # get next control op and generate a pixel
                alphacode_index = 3 * (4 * j + i)

                if alphacode_index <= 12:
                    alphacode = (alphacode2 >> alphacode_index) & 0x07
                elif alphacode_index == 15:
                    alphacode = (alphacode2 >> 15) | ((alphacode1 << 1) & 0x06)
                else:  # alphacode_index >= 18 and alphacode_index <= 45
                    alphacode = (alphacode1 >> (alphacode_index - 16)) & 0x07

                if alphacode == 0:
                    a = a0
                elif alphacode == 1:
                    a = a1
                elif a0 > a1:
                    a = ((8 - alphacode) * a0 + (alphacode - 1) * a1) // 7
                elif alphacode == 6:
                    a = 0
                elif alphacode == 7:
                    a = 255
                else:
                    a = ((6 - alphacode) * a0 + (alphacode - 1) * a1) // 5

                color_code = (code >> 2 * (4 * j + i)) & 0x03

                if color_code == 0:
                    r, g, b = r0, g0, b0
                elif color_code == 1:
                    r, g, b = r1, g1, b1
                elif color_code == 2:
                    r = (2 * r0 + r1) // 3
                    g = (2 * g0 + g1) // 3
                    b = (2 * b0 + b1) // 3
                elif color_code == 3:
                    r = (2 * r1 + r0) // 3
                    g = (2 * g1 + g0) // 3
                    b = (2 * b1 + b0) // 3

                ret[j].extend([r, g, b, a])

    return ret


def getpalette(data):
    """
    Helper to transform a BytesIO object into a palette
    """
    palette = []
    string = BytesIO(data)
    while True:
        try:
            palette.append(struct.unpack("<4B", string.read(4)))
        except struct.error:
            break
    return palette


class BLPFormatError(NotImplementedError):
    pass


class BlpImageFile(ImageFile.ImageFile):
    """
    Blizzard Mipmap Format
    """
    format = "BLP"
    format_description = "Blizzard Mipmap Format"

    def _decode_blp1(self):
        header = BytesIO(self.fp.read(28 + 16 * 4 + 16 * 4))

        magic, compression = struct.unpack("<4si", header.read(8))
        encoding, alpha_depth, alpha_encoding, has_mips = struct.unpack(
            "<4b", header.read(4)
        )
        self.size = struct.unpack("<II", header.read(8))
        encoding, subtype = struct.unpack("<ii", header.read(8))
        offsets = struct.unpack("<16I", header.read(16 * 4))
        lengths = struct.unpack("<16I", header.read(16 * 4))

        if compression == BLP_FORMAT_JPEG:
            from PIL.JpegImagePlugin import JpegImageFile
            jpeg_header_size, = struct.unpack("<I", self.fp.read(4))
            jpeg_header = self.fp.read(jpeg_header_size)
            self.fp.read(offsets[0] - self.fp.tell())  # What IS this?
            data = self.fp.read(lengths[0])
            data = jpeg_header + data
            data = BytesIO(data)
            image = JpegImageFile(data)
            image.show()
            self.tile = image.tile  # :/
            self.fp = image.fp
            self.mode = image.mode

        elif compression == 1:
            if encoding == 5:
                data = []
                palette_data = self.fp.read(256 * 4)
                palette = getpalette(palette_data)
                _data = BytesIO(self.fp.read(lengths[0]))
                self.mode = "RGB"
                self.tile = []
                while True:
                    try:
                        offset, = struct.unpack("<B", _data.read(1))
                    except struct.error:
                        break
                    b, g, r, a = palette[offset]
                    data.append(struct.pack("<BBB", r, g, b))

                data = b"".join(data)
                self.im = Image.core.new(self.mode, self.size)
                self.frombytes(data)
            else:
                raise BLPFormatError(
                    "Unknown or unsupported BLP encoding %r" % (encoding)
                )
        else:
            raise BLPFormatError(
                "Unknown or unsupported BLP compression %r" % (encoding)
            )

    def _decode_blp2(self):
        header = BytesIO(self.fp.read(20 + 16 * 4 + 16 * 4))

        magic, compression = struct.unpack("<4si", header.read(8))
        encoding, alpha_depth, alpha_encoding, has_mips = struct.unpack(
            "<4b", header.read(4)
        )
        self.size = struct.unpack("<II", header.read(8))
        offsets = struct.unpack("<16I", header.read(16 * 4))
        lengths = struct.unpack("<16I", header.read(16 * 4))
        palette_data = self.fp.read(256 * 4)

        self.mode = "RGB"
        self.tile = []

        if compression == 1:
            # Uncompressed or DirectX compression
            data = []
            self.fp.seek(offsets[0])

            if encoding == BLP_ENCODING_UNCOMPRESSED:
                palette = getpalette(palette_data)
                _data = BytesIO(self.fp.read(lengths[0]))
                while True:
                    try:
                        offset, = struct.unpack("<B", _data.read(1))
                    except struct.error:
                        break
                    b, g, r, a = palette[offset]
                    data.append(struct.pack("<BBB", r, g, b))

            elif encoding == BLP_ENCODING_DXT:
                if alpha_encoding == BLP_ALPHA_ENCODING_DXT1:
                    linesize = (self.size[0] + 3) // 4 * 8
                    for yb in range((self.size[1] + 3) // 4):
                        line_data = self.fp.read(linesize)
                        if alpha_depth:
                            self.mode = "RGBA"
                            decoded = decode_dxt1(line_data, alpha=True)
                        else:
                            decoded = decode_dxt1(line_data)
                        for d in decoded:
                            data.append(d)

                elif alpha_encoding == BLP_ALPHA_ENCODING_DXT3:
                    linesize = (self.size[0] + 3) // 4 * 16
                    self.mode = "RGBA"
                    for yb in range((self.size[1] + 3) // 4):
                        decoded = decode_dxt3(self.fp.read(linesize))
                        for d in decoded:
                            data.append(d)

                elif alpha_encoding == BLP_ALPHA_ENCODING_DXT5:
                    linesize = (self.size[0] + 3) // 4 * 16
                    self.mode = "RGBA"
                    for yb in range((self.size[1] + 3) // 4):
                        decoded = decode_dxt5(self.fp.read(linesize))
                        for d in decoded:
                            data.append(d)
                else:
                    raise BLPFormatError(
                        "Unsupported alpha encoding %r" % (alpha_encoding)
                    )

            self.im = Image.core.new(self.mode, self.size)

            data = b"".join(data)
            self.frombytes(data)

    def _open(self):
        magic = self.fp.read(4)
        self.fp.seek(0)
        if magic == b"BLP1":
            return self._decode_blp1()

        if magic == b"BLP2":
            return self._decode_blp2()

        raise ValueError("not a BLP file (magic: %r)" % (magic))


def _validate(prefix):
    return prefix[:4] in (b"BLP1", b"BLP2")


Image.register_open(BlpImageFile.format, BlpImageFile, _validate)
Image.register_extension(BlpImageFile.format, ".blp")
