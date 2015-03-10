from PIL import Image, ImageFile, _webp
from PIL._binary import i8, i32le
import os


_VALID_WEBP_MODES = ("RGB", "RGBA")

_VP8_MODES_BY_IDENTIFIER = (b"VP8 ", b"VP8X", b"VP8L")


def _accept(prefix):
    is_riff_file_format = prefix[:4] == b"RIFF"
    is_webp_file = prefix[8:12] == b"WEBP"
    is_valid_vp8_mode = prefix[12:16] in _VP8_MODES_BY_IDENTIFIER

    return is_riff_file_format and is_webp_file and is_valid_vp8_mode

# VP8X/VP8L/VP8 chunk parsing routines.
# Arguments:
# - chunk_size: RIFF chunk size
# - fp: file
# Return:
# - mode: RGB/RGBA
# - size: width/height
# - skip: how many bytes to skip to next chunk

def _parse_vp8x(chunk_size, fp):
    if chunk_size < 10:
        raise SyntaxError("bad VP8X chunk")
    vp8x = fp.read(10)
    if 10 != len(vp8x):
        raise SyntaxError("bad VP8X chunk")
    flags = i8(vp8x[0])
    if (flags & 0b10000):
        mode = 'RGBA'
    else:
        mode = 'RGB'
    width = (i8(vp8x[4]) | (i8(vp8x[5]) << 8) | (i8(vp8x[6]) << 16)) + 1
    height = (i8(vp8x[7]) | (i8(vp8x[8]) << 8) | (i8(vp8x[9]) << 16)) + 1
    return mode, (width, height), chunk_size - 10

def _parse_vp8l(chunk_size, fp):
    if chunk_size < 5:
        raise SyntaxError("bad VP8L chunk")
    vp8l = fp.read(5)
    if 5 != len(vp8l):
        raise SyntaxError("bad VP8L chunk")
    vp8l = [i8(b) for b in vp8l]
    # Check signature.
    if 0x2f != vp8l[0] or 0 != (vp8l[4] >> 5):
        raise SyntaxError("bad VP8L chunk")
    if (vp8l[4] & 0b10000):
        mode = 'RGBA'
    else:
        mode = 'RGB'
    # 14 bits for each...
    width = (vp8l[1] | ((vp8l[2] & 0b111111) << 8)) + 1
    height = ((vp8l[2] >> 6) | (vp8l[3] << 2) | ((vp8l[4] & 0b1111) << 10)) + 1
    return mode, (width, height), chunk_size - 5

def _parse_vp8(chunk_size, fp):
    if chunk_size < 10:
        raise SyntaxError("bad VP8 chunk")
    vp8 = fp.read(10)
    if 10 != len(vp8):
        raise SyntaxError("bad VP8 chunk")
    # Check signature.
    if 0x9d != i8(vp8[3]) or 0x01 != i8(vp8[4]) or 0x2a != i8(vp8[5]):
        raise SyntaxError("bad VP8 chunk")
    mode = 'RGB'
    width = (i8(vp8[6]) | (i8(vp8[7]) << 8)) & 0x3fff
    height = (i8(vp8[8]) | (i8(vp8[9]) << 8)) & 0x3fff
    return mode, (width, height), chunk_size - 10


class WebPImageFile(ImageFile.ImageFile):

    format = "WEBP"
    format_description = "WebP image"

    def _open(self):

        header = self.fp.read(12)
        if 12 != len(header):
            raise SyntaxError("not a WebP file")

        if b'RIFF' != header[0:4] or b'WEBP' != header[8:12]:
            raise SyntaxError("not a WebP file")

        mode = None
        size = None
        lossy = None

        first_chunk = True

        while True:

            chunk_header = self.fp.read(8)
            if 8 != len(chunk_header):
                if first_chunk:
                    raise SyntaxError("not a WebP file")
                break

            chunk_fourcc = chunk_header[0:4]
            chunk_size = i32le(chunk_header[4:8])

            if first_chunk:
                if chunk_fourcc not in _VP8_MODES_BY_IDENTIFIER:
                    raise SyntaxError("not a WebP file")

            if b'VP8X' == chunk_fourcc:
                if first_chunk:
                    mode, size, chunk_size = _parse_vp8x(chunk_size, self.fp)

            elif b'VP8L' == chunk_fourcc:
                if first_chunk:
                    mode, size, chunk_size = _parse_vp8l(chunk_size, self.fp)
                lossy = False

            elif b'VP8 ' == chunk_fourcc:
                if first_chunk:
                    mode, size, chunk_size = _parse_vp8(chunk_size, self.fp)
                lossy = True

            elif b'ALPH' == chunk_fourcc:
                mode = 'RGBA'

            elif b'EXIF' == chunk_fourcc:
                exif = self.fp.read(chunk_size)
                if chunk_size != len(exif):
                    raise SyntaxError("bad EXIF chunk")
                self.info["exif"] = exif
                chunk_size = 0

            elif b'ICCP' == chunk_fourcc:
                icc_profile = self.fp.read(chunk_size)
                if chunk_size != len(icc_profile):
                    raise SyntaxError("bad ICCP chunk")
                self.info["icc_profile"] = icc_profile
                chunk_size = 0

            if chunk_size > 0:
                # Skip to next chunk.
                pos = self.fp.tell()
                self.fp.seek(chunk_size, os.SEEK_CUR)
                if self.fp.tell() != (pos + chunk_size):
                    raise SyntaxError("not a WebP file")

            first_chunk = False

        if None in (mode, size, lossy):
            raise SyntaxError("not a WebP file")

        self.mode = mode
        self.size = size
        self.info['compression'] = 'lossy' if lossy else 'lossless'
        self.tile = [('webp', (0, 0) + size, 0,
                      # Decoder params: rawmode, has_alpha, width, height.
                      (mode, 1 if 'RGBA' == mode else 0, size[0], size[1]))]

        if not lossy:
            # Incremental decoding on lossless is *really* slow, disable it.
            self.decodermaxblock = 12 + i32le(header[4:8])
            self.decoderconfig = (1,)

    def load_prepare(self):
        if not self.im:
            # Hackety hack hack hack... force block storage (one continuous
            # buffer), so we don't need to allocate a temporary output buffer
            # for the decoder.
            im = Image.core.new(self.mode, (0,0))
            self.im = im.new_block(self.mode, self.size)
        ImageFile.ImageFile.load_prepare(self)

    def draft(self, mode, size):

        if 1 != len(self.tile):
            return

        d, e, o, a = self.tile[0]

        if mode in _VALID_WEBP_MODES:
            a = mode, a[1], a[2], a[3]
            self.mode = mode

        if size:
            e = e[0], e[1], size[0], size[1]
            self.size = size

        self.tile = [(d, e, o, a)]

        return self

    def _getexif(self):
        from PIL.JpegImagePlugin import _getexif
        return _getexif(self)


def _save(im, fp, filename):
    image_mode = im.mode
    if im.mode not in _VALID_WEBP_MODES:
        raise IOError("cannot write mode %s as WEBP" % image_mode)

    lossless = im.encoderinfo.get("lossless", False)
    quality = im.encoderinfo.get("quality", 80)
    icc_profile = im.encoderinfo.get("icc_profile", "")
    exif = im.encoderinfo.get("exif", "")

    data = _webp.WebPEncode(
        im.tobytes(),
        im.size[0],
        im.size[1],
        lossless,
        float(quality),
        im.mode,
        icc_profile,
        exif
    )
    if data is None:
        raise IOError("cannot write file as WEBP (encoder returned None)")

    fp.write(data)


Image.register_open("WEBP", WebPImageFile, _accept)
Image.register_save("WEBP", _save)

Image.register_extension("WEBP", ".webp")
Image.register_mime("WEBP", "image/webp")
