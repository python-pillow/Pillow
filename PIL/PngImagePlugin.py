#
# The Python Imaging Library.
# $Id$
#
# PNG support code
#
# See "PNG (Portable Network Graphics) Specification, version 1.0;
# W3C Recommendation", 1996-10-01, Thomas Boutell (ed.).
#
# history:
# 1996-05-06 fl   Created (couldn't resist it)
# 1996-12-14 fl   Upgraded, added read and verify support (0.2)
# 1996-12-15 fl   Separate PNG stream parser
# 1996-12-29 fl   Added write support, added getchunks
# 1996-12-30 fl   Eliminated circular references in decoder (0.3)
# 1998-07-12 fl   Read/write 16-bit images as mode I (0.4)
# 2001-02-08 fl   Added transparency support (from Zircon) (0.5)
# 2001-04-16 fl   Don't close data source in "open" method (0.6)
# 2004-02-24 fl   Don't even pretend to support interlaced files (0.7)
# 2004-08-31 fl   Do basic sanity check on chunk identifiers (0.8)
# 2004-09-20 fl   Added PngInfo chunk container
# 2004-12-18 fl   Added DPI read support (based on code by Niki Spahiev)
# 2008-08-13 fl   Added tRNS support for RGB images
# 2009-03-06 fl   Support for preserving ICC profiles (by Florian Hoech)
# 2009-03-08 fl   Added zTXT support (from Lowell Alleman)
# 2009-03-29 fl   Read interlaced PNG files (from Conrado Porto Lopes Gouvua)
#
# Copyright (c) 1997-2009 by Secret Labs AB
# Copyright (c) 1996 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

from __future__ import print_function

__version__ = "0.9"

import re

from PIL import Image, ImageFile, ImagePalette, _binary
import zlib

i8 = _binary.i8
i16 = _binary.i16be
i32 = _binary.i32be

is_cid = re.compile(b"\w\w\w\w").match


_MAGIC = b"\211PNG\r\n\032\n"


_MODES = {
    # supported bits/color combinations, and corresponding modes/rawmodes
    (1, 0): ("1", "1"),
    (2, 0): ("L", "L;2"),
    (4, 0): ("L", "L;4"),
    (8, 0): ("L", "L"),
    (16,0): ("I", "I;16B"),
    (8, 2): ("RGB", "RGB"),
    (16,2): ("RGB", "RGB;16B"),
    (1, 3): ("P", "P;1"),
    (2, 3): ("P", "P;2"),
    (4, 3): ("P", "P;4"),
    (8, 3): ("P", "P"),
    (8, 4): ("LA", "LA"),
    (16,4): ("RGBA", "LA;16B"), # LA;16B->LA not yet available
    (8, 6): ("RGBA", "RGBA"),
    (16,6): ("RGBA", "RGBA;16B"),
}


_simple_palette = re.compile(b'^\xff+\x00\xff*$')

# --------------------------------------------------------------------
# Support classes.  Suitable for PNG and related formats like MNG etc.

class ChunkStream:

    def __init__(self, fp):

        self.fp = fp
        self.queue = []

        if not hasattr(Image.core, "crc32"):
            self.crc = self.crc_skip

    def read(self):
        "Fetch a new chunk. Returns header information."

        if self.queue:
            cid, pos, len = self.queue[-1]
            del self.queue[-1]
            self.fp.seek(pos)
        else:
            s = self.fp.read(8)
            cid = s[4:]
            pos = self.fp.tell()
            len = i32(s)

        if not is_cid(cid):
            raise SyntaxError("broken PNG file (chunk %s)" % repr(cid))

        return cid, pos, len

    def close(self):
        self.queue = self.crc = self.fp = None

    def push(self, cid, pos, len):

        self.queue.append((cid, pos, len))

    def call(self, cid, pos, len):
        "Call the appropriate chunk handler"

        if Image.DEBUG:
            print("STREAM", cid, pos, len)
        return getattr(self, "chunk_" + cid.decode('ascii'))(pos, len)

    def crc(self, cid, data):
        "Read and verify checksum"

        crc1 = Image.core.crc32(data, Image.core.crc32(cid))
        crc2 = i16(self.fp.read(2)), i16(self.fp.read(2))
        if crc1 != crc2:
            raise SyntaxError("broken PNG file"\
                "(bad header checksum in %s)" % cid)

    def crc_skip(self, cid, data):
        "Read checksum.  Used if the C module is not present"

        self.fp.read(4)

    def verify(self, endchunk = b"IEND"):

        # Simple approach; just calculate checksum for all remaining
        # blocks.  Must be called directly after open.

        cids = []

        while True:
            cid, pos, len = self.read()
            if cid == endchunk:
                break
            self.crc(cid, ImageFile._safe_read(self.fp, len))
            cids.append(cid)

        return cids


# --------------------------------------------------------------------
# PNG chunk container (for use with save(pnginfo=))

class PngInfo:

    def __init__(self):
        self.chunks = []

    def add(self, cid, data):
        self.chunks.append((cid, data))

    def add_text(self, key, value, zip=0):
        # The tEXt chunk stores latin-1 text
        if not isinstance(key, bytes):
            key = key.encode('latin-1', 'strict')

        if not isinstance(value, bytes):
            value = value.encode('latin-1', 'replace')

        if zip:
            import zlib
            self.add(b"zTXt", key + b"\0\0" + zlib.compress(value))
        else:
            self.add(b"tEXt", key + b"\0" + value)

# --------------------------------------------------------------------
# PNG image stream (IHDR/IEND)

class PngStream(ChunkStream):

    def __init__(self, fp):

        ChunkStream.__init__(self, fp)

        # local copies of Image attributes
        self.im_info = {}
        self.im_text = {}
        self.im_size = (0,0)
        self.im_mode = None
        self.im_tile = None
        self.im_palette = None

    def chunk_iCCP(self, pos, len):

        # ICC profile
        s = ImageFile._safe_read(self.fp, len)
        # according to PNG spec, the iCCP chunk contains:
        # Profile name  1-79 bytes (character string)
        # Null separator        1 byte (null character)
        # Compression method    1 byte (0)
        # Compressed profile    n bytes (zlib with deflate compression)
        i = s.find(b"\0")
        if Image.DEBUG:
            print("iCCP profile name", s[:i])
            print("Compression method", i8(s[i]))
        comp_method = i8(s[i])
        if comp_method != 0:
            raise SyntaxError("Unknown compression method %s in iCCP chunk" % comp_method)
        try:
            icc_profile = zlib.decompress(s[i+2:])
        except zlib.error:
            icc_profile = None # FIXME
        self.im_info["icc_profile"] = icc_profile
        return s

    def chunk_IHDR(self, pos, len):

        # image header
        s = ImageFile._safe_read(self.fp, len)
        self.im_size = i32(s), i32(s[4:])
        try:
            self.im_mode, self.im_rawmode = _MODES[(i8(s[8]), i8(s[9]))]
        except:
            pass
        if i8(s[12]):
            self.im_info["interlace"] = 1
        if i8(s[11]):
            raise SyntaxError("unknown filter category")
        return s

    def chunk_IDAT(self, pos, len):

        # image data
        self.im_tile = [("zip", (0,0)+self.im_size, pos, self.im_rawmode)]
        self.im_idat = len
        raise EOFError

    def chunk_IEND(self, pos, len):

        # end of PNG image
        raise EOFError

    def chunk_PLTE(self, pos, len):

        # palette
        s = ImageFile._safe_read(self.fp, len)
        if self.im_mode == "P":
            self.im_palette = "RGB", s
        return s

    def chunk_tRNS(self, pos, len):

        # transparency
        s = ImageFile._safe_read(self.fp, len)
        if self.im_mode == "P":
            if _simple_palette.match(s):
                i = s.find(b"\0")
                if i >= 0:
                    self.im_info["transparency"] = i
            else:
                self.im_info["transparency"] = s
        elif self.im_mode == "L":
            self.im_info["transparency"] = i16(s)
        elif self.im_mode == "RGB":
            self.im_info["transparency"] = i16(s), i16(s[2:]), i16(s[4:])
        return s

    def chunk_gAMA(self, pos, len):

        # gamma setting
        s = ImageFile._safe_read(self.fp, len)
        self.im_info["gamma"] = i32(s) / 100000.0
        return s

    def chunk_pHYs(self, pos, len):

        # pixels per unit
        s = ImageFile._safe_read(self.fp, len)
        px, py = i32(s), i32(s[4:])
        unit = i8(s[8])
        if unit == 1: # meter
            dpi = int(px * 0.0254 + 0.5), int(py * 0.0254 + 0.5)
            self.im_info["dpi"] = dpi
        elif unit == 0:
            self.im_info["aspect"] = px, py
        return s

    def chunk_tEXt(self, pos, len):

        # text
        s = ImageFile._safe_read(self.fp, len)
        try:
            k, v = s.split(b"\0", 1)
        except ValueError:
            k = s; v = b"" # fallback for broken tEXt tags
        if k:
            if bytes is not str:
                k = k.decode('latin-1', 'strict')
                v = v.decode('latin-1', 'replace')

            self.im_info[k] = self.im_text[k] = v
        return s

    def chunk_zTXt(self, pos, len):

        # compressed text
        s = ImageFile._safe_read(self.fp, len)
        try:
            k, v = s.split(b"\0", 1)
        except ValueError:
            k = s; v = b""
        if v:
            comp_method = i8(v[0])
        else:
            comp_method = 0
        if comp_method != 0:
            raise SyntaxError("Unknown compression method %s in zTXt chunk" % comp_method)
        import zlib
        try:
            v = zlib.decompress(v[1:])
        except zlib.error:
            v = b""

        if k:
            if bytes is not str:
                k = k.decode('latin-1', 'strict')
                v = v.decode('latin-1', 'replace')

            self.im_info[k] = self.im_text[k] = v
        return s

# --------------------------------------------------------------------
# PNG reader

def _accept(prefix):
    return prefix[:8] == _MAGIC

##
# Image plugin for PNG images.

class PngImageFile(ImageFile.ImageFile):

    format = "PNG"
    format_description = "Portable network graphics"

    def _open(self):

        if self.fp.read(8) != _MAGIC:
            raise SyntaxError("not a PNG file")

        #
        # Parse headers up to the first IDAT chunk

        self.png = PngStream(self.fp)

        while True:

            #
            # get next chunk

            cid, pos, len = self.png.read()

            try:
                s = self.png.call(cid, pos, len)
            except EOFError:
                break
            except AttributeError:
                if Image.DEBUG:
                    print(cid, pos, len, "(unknown)")
                s = ImageFile._safe_read(self.fp, len)

            self.png.crc(cid, s)

        #
        # Copy relevant attributes from the PngStream.  An alternative
        # would be to let the PngStream class modify these attributes
        # directly, but that introduces circular references which are
        # difficult to break if things go wrong in the decoder...
        # (believe me, I've tried ;-)

        self.mode = self.png.im_mode
        self.size = self.png.im_size
        self.info = self.png.im_info
        self.text = self.png.im_text # experimental
        self.tile = self.png.im_tile

        if self.png.im_palette:
            rawmode, data = self.png.im_palette
            self.palette = ImagePalette.raw(rawmode, data)

        self.__idat = len # used by load_read()


    def verify(self):
        "Verify PNG file"

        if self.fp is None:
            raise RuntimeError("verify must be called directly after open")

        # back up to beginning of IDAT block
        self.fp.seek(self.tile[0][2] - 8)

        self.png.verify()
        self.png.close()

        self.fp = None

    def load_prepare(self):
        "internal: prepare to read PNG file"

        if self.info.get("interlace"):
            self.decoderconfig = self.decoderconfig + (1,)

        ImageFile.ImageFile.load_prepare(self)

    def load_read(self, bytes):
        "internal: read more image data"

        while self.__idat == 0:
            # end of chunk, skip forward to next one

            self.fp.read(4) # CRC

            cid, pos, len = self.png.read()

            if cid not in [b"IDAT", b"DDAT"]:
                self.png.push(cid, pos, len)
                return b""

            self.__idat = len # empty chunks are allowed

        # read more data from this chunk
        if bytes <= 0:
            bytes = self.__idat
        else:
            bytes = min(bytes, self.__idat)

        self.__idat = self.__idat - bytes

        return self.fp.read(bytes)


    def load_end(self):
        "internal: finished reading image data"

        self.png.close()
        self.png = None


# --------------------------------------------------------------------
# PNG writer

o8 = _binary.o8
o16 = _binary.o16be
o32 = _binary.o32be

_OUTMODES = {
    # supported PIL modes, and corresponding rawmodes/bits/color combinations
    "1":   ("1",       b'\x01\x00'),
    "L;1": ("L;1",     b'\x01\x00'),
    "L;2": ("L;2",     b'\x02\x00'),
    "L;4": ("L;4",     b'\x04\x00'),
    "L":   ("L",       b'\x08\x00'),
    "LA":  ("LA",      b'\x08\x04'),
    "I":   ("I;16B",   b'\x10\x00'),
    "P;1": ("P;1",     b'\x01\x03'),
    "P;2": ("P;2",     b'\x02\x03'),
    "P;4": ("P;4",     b'\x04\x03'),
    "P":   ("P",       b'\x08\x03'),
    "RGB": ("RGB",     b'\x08\x02'),
    "RGBA":("RGBA",    b'\x08\x06'),
}

def putchunk(fp, cid, *data):
    "Write a PNG chunk (including CRC field)"

    data = b"".join(data)

    fp.write(o32(len(data)) + cid)
    fp.write(data)
    hi, lo = Image.core.crc32(data, Image.core.crc32(cid))
    fp.write(o16(hi) + o16(lo))

class _idat:
    # wrap output from the encoder in IDAT chunks

    def __init__(self, fp, chunk):
        self.fp = fp
        self.chunk = chunk
    def write(self, data):
        self.chunk(self.fp, b"IDAT", data)

def _save(im, fp, filename, chunk=putchunk, check=0):
    # save an image to disk (called by the save method)

    mode = im.mode

    if mode == "P":

        #
        # attempt to minimize storage requirements for palette images
        if "bits" in im.encoderinfo:
            # number of bits specified by user
            colors = 1 << im.encoderinfo["bits"]
        else:
            # check palette contents
            if im.palette:
                colors = len(im.palette.getdata()[1])//3
            else:
                colors = 256

        if colors <= 2:
            bits = 1
        elif colors <= 4:
            bits = 2
        elif colors <= 16:
            bits = 4
        else:
            bits = 8
        if bits != 8:
            mode = "%s;%d" % (mode, bits)

    # encoder options
    if "dictionary" in im.encoderinfo:
        dictionary = im.encoderinfo["dictionary"]
    else:
        dictionary = b""

    im.encoderconfig = ("optimize" in im.encoderinfo,
        im.encoderinfo.get("compress_level", -1),
        im.encoderinfo.get("compress_type", -1),
        dictionary)

    # get the corresponding PNG mode
    try:
        rawmode, mode = _OUTMODES[mode]
    except KeyError:
        raise IOError("cannot write mode %s as PNG" % mode)

    if check:
        return check

    #
    # write minimal PNG file

    fp.write(_MAGIC)

    chunk(fp, b"IHDR",
          o32(im.size[0]), o32(im.size[1]),     #  0: size
          mode,                                 #  8: depth/type
          b'\0',                                # 10: compression
          b'\0',                                # 11: filter category
          b'\0')                                # 12: interlace flag

    if im.mode == "P":
        palette_byte_number = (2 ** bits) * 3
        palette_bytes = im.im.getpalette("RGB")[:palette_byte_number]
        while len(palette_bytes) < palette_byte_number:
            palette_bytes += b'\0'
        chunk(fp, b"PLTE", palette_bytes)

    transparency = im.encoderinfo.get('transparency',im.info.get('transparency', None))
    
    if transparency:
        if im.mode == "P":
            # limit to actual palette size
            alpha_bytes = 2**bits
            if isinstance(transparency, bytes):
                chunk(fp, b"tRNS", transparency[:alpha_bytes])
            else:
                transparency = max(0, min(255, transparency))
                alpha = b'\xFF' * transparency + b'\0'
                chunk(fp, b"tRNS", alpha[:alpha_bytes])
        elif im.mode == "L":
            transparency = max(0, min(65535, transparency))
            chunk(fp, b"tRNS", o16(transparency))
        elif im.mode == "RGB":
            red, green, blue = transparency
            chunk(fp, b"tRNS", o16(red) + o16(green) + o16(blue))
        else:
            if "transparency" in im.encoderinfo:
                # don't bother with transparency if it's an RGBA
                # and it's in the info dict. It's probably just stale. 
                raise IOError("cannot use transparency for this mode")
    else:
        if im.mode == "P" and im.im.getpalettemode() == "RGBA":
            alpha = im.im.getpalette("RGBA", "A")
            alpha_bytes = 2**bits
            chunk(fp, b"tRNS", alpha[:alpha_bytes])

    if 0:
        # FIXME: to be supported some day
        chunk(fp, b"gAMA", o32(int(gamma * 100000.0)))

    dpi = im.encoderinfo.get("dpi")
    if dpi:
        chunk(fp, b"pHYs",
              o32(int(dpi[0] / 0.0254 + 0.5)),
              o32(int(dpi[1] / 0.0254 + 0.5)),
              b'\x01')

    info = im.encoderinfo.get("pnginfo")
    if info:
        for cid, data in info.chunks:
            chunk(fp, cid, data)

    # ICC profile writing support -- 2008-06-06 Florian Hoech
    if "icc_profile" in im.info:
        # ICC profile
        # according to PNG spec, the iCCP chunk contains:
        # Profile name  1-79 bytes (character string)
        # Null separator        1 byte (null character)
        # Compression method    1 byte (0)
        # Compressed profile    n bytes (zlib with deflate compression)
        try:
            import ICCProfile
            p = ICCProfile.ICCProfile(im.info["icc_profile"])
            name = p.tags.desc.get("ASCII", p.tags.desc.get("Unicode", p.tags.desc.get("Macintosh", p.tags.desc.get("en", {}).get("US", "ICC Profile")))).encode("latin1", "replace")[:79]
        except ImportError:
            name = b"ICC Profile"
        data = name + b"\0\0" + zlib.compress(im.info["icc_profile"])
        chunk(fp, b"iCCP", data)

    ImageFile._save(im, _idat(fp, chunk), [("zip", (0,0)+im.size, 0, rawmode)])

    chunk(fp, b"IEND", b"")

    try:
        fp.flush()
    except:
        pass


# --------------------------------------------------------------------
# PNG chunk converter

def getchunks(im, **params):
    """Return a list of PNG chunks representing this image."""

    class collector:
        data = []
        def write(self, data):
            pass
        def append(self, chunk):
            self.data.append(chunk)

    def append(fp, cid, *data):
        data = b"".join(data)
        hi, lo = Image.core.crc32(data, Image.core.crc32(cid))
        crc = o16(hi) + o16(lo)
        fp.append((cid, data, crc))

    fp = collector()

    try:
        im.encoderinfo = params
        _save(im, fp, None, append)
    finally:
        del im.encoderinfo

    return fp.data


# --------------------------------------------------------------------
# Registry

Image.register_open("PNG", PngImageFile, _accept)
Image.register_save("PNG", _save)

Image.register_extension("PNG", ".png")

Image.register_mime("PNG", "image/png")
