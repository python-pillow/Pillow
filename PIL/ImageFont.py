#
# The Python Imaging Library.
# $Id$
#
# PIL raster font management
#
# History:
# 1996-08-07 fl   created (experimental)
# 1997-08-25 fl   minor adjustments to handle fonts from pilfont 0.3
# 1999-02-06 fl   rewrote most font management stuff in C
# 1999-03-17 fl   take pth files into account in load_path (from Richard Jones)
# 2001-02-17 fl   added freetype support
# 2001-05-09 fl   added TransposedFont wrapper class
# 2002-03-04 fl   make sure we have a "L" or "1" font
# 2002-12-04 fl   skip non-directory entries in the system path
# 2003-04-29 fl   add embedded default font
# 2003-09-27 fl   added support for truetype charmap encodings
#
# Todo:
# Adapt to PILFONT2 format (16-bit fonts, compressed, single file)
#
# Copyright (c) 1997-2003 by Secret Labs AB
# Copyright (c) 1996-2003 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

from __future__ import print_function

from PIL import Image
from PIL._util import isDirectory, isPath
import os, sys

try:
    import warnings
except ImportError:
    warnings = None

class _imagingft_not_installed:
    # module placeholder
    def __getattr__(self, id):
        raise ImportError("The _imagingft C module is not installed")

try:
    from PIL import _imagingft as core
except ImportError:
    core = _imagingft_not_installed()

# FIXME: add support for pilfont2 format (see FontFile.py)

# --------------------------------------------------------------------
# Font metrics format:
#       "PILfont" LF
#       fontdescriptor LF
#       (optional) key=value... LF
#       "DATA" LF
#       binary data: 256*10*2 bytes (dx, dy, dstbox, srcbox)
#
# To place a character, cut out srcbox and paste at dstbox,
# relative to the character position.  Then move the character
# position according to dx, dy.
# --------------------------------------------------------------------


class ImageFont:
    "PIL font wrapper"

    def _load_pilfont(self, filename):

        file = open(filename, "rb")

        for ext in (".png", ".gif", ".pbm"):
            try:
                fullname = os.path.splitext(filename)[0] + ext
                image = Image.open(fullname)
            except:
                pass
            else:
                if image and image.mode in ("1", "L"):
                    break
        else:
            raise IOError("cannot find glyph data file")

        self.file = fullname

        return self._load_pilfont_data(file, image)

    def _load_pilfont_data(self, file, image):

        # read PILfont header
        if file.readline() != b"PILfont\n":
            raise SyntaxError("Not a PILfont file")
        d = file.readline().split(b";")
        self.info = [] # FIXME: should be a dictionary
        while True:
            s = file.readline()
            if not s or s == b"DATA\n":
                break
            self.info.append(s)

        # read PILfont metrics
        data = file.read(256*20)

        # check image
        if image.mode not in ("1", "L"):
            raise TypeError("invalid font image mode")

        image.load()

        self.font = Image.core.font(image.im, data)

        # delegate critical operations to internal type
        self.getsize = self.font.getsize
        self.getmask = self.font.getmask

##
# Wrapper for FreeType fonts.  Application code should use the
# <b>truetype</b> factory function to create font objects.

class FreeTypeFont:
    "FreeType font wrapper (requires _imagingft service)"

    def __init__(self, font=None, size=10, index=0, encoding="", file=None):
        # FIXME: use service provider instead
        if file:
            if warnings:
                warnings.warn('file parameter deprecated, please use font parameter instead.', DeprecationWarning)
            font = file

        if isPath(font):
            self.font = core.getfont(font, size, index, encoding)
        else:
            self.font_bytes = font.read()
            self.font = core.getfont("", size, index, encoding, self.font_bytes)

    def getname(self):
        return self.font.family, self.font.style

    def getmetrics(self):
        return self.font.ascent, self.font.descent

    def getsize(self, text):
        return self.font.getsize(text)[0]

    def getoffset(self, text):
        return self.font.getsize(text)[1]

    def getmask(self, text, mode=""):
        return self.getmask2(text, mode)[0]

    def getmask2(self, text, mode="", fill=Image.core.fill):
        size, offset = self.font.getsize(text)
        im = fill("L", size, 0)
        self.font.render(text, im.id, mode=="1")
        return im, offset

##
# Wrapper that creates a transposed font from any existing font
# object.
#
# @param font A font object.
# @param orientation An optional orientation.  If given, this should
#     be one of Image.FLIP_LEFT_RIGHT, Image.FLIP_TOP_BOTTOM,
#     Image.ROTATE_90, Image.ROTATE_180, or Image.ROTATE_270.

class TransposedFont:
    "Wrapper for writing rotated or mirrored text"

    def __init__(self, font, orientation=None):
        self.font = font
        self.orientation = orientation # any 'transpose' argument, or None

    def getsize(self, text):
        w, h = self.font.getsize(text)
        if self.orientation in (Image.ROTATE_90, Image.ROTATE_270):
            return h, w
        return w, h

    def getmask(self, text, mode=""):
        im = self.font.getmask(text, mode)
        if self.orientation is not None:
            return im.transpose(self.orientation)
        return im


def load(filename):
    """
    Load a font file.  This function loads a font object from the given
    bitmap font file, and returns the corresponding font object.

    :param filename: Name of font file.
    :return: A font object.
    :exception IOError: If the file could not be read.
    """
    f = ImageFont()
    f._load_pilfont(filename)
    return f


def truetype(font=None, size=10, index=0, encoding="", filename=None):
    """
    Load a TrueType or OpenType font file, and create a font object.
    This function loads a font object from the given file, and creates
    a font object for a font of the given size.

    This function requires the _imagingft service.

    :param filename: A truetype font file. Under Windows, if the file
                     is not found in this filename, the loader also looks in
                     Windows :file:`fonts/` directory.
    :param size: The requested size, in points.
    :param index: Which font face to load (default is first available face).
    :param encoding: Which font encoding to use (default is Unicode). Common
                     encodings are "unic" (Unicode), "symb" (Microsoft
                     Symbol), "ADOB" (Adobe Standard), "ADBE" (Adobe Expert),
                     and "armn" (Apple Roman). See the FreeType documentation
                     for more information.
    :return: A font object.
    :exception IOError: If the file could not be read.
    """

    if filename:
        if warnings:
            warnings.warn('filename parameter deprecated, please use font parameter instead.', DeprecationWarning)
        font = filename

    try:
        return FreeTypeFont(font, size, index, encoding)
    except IOError:
        if sys.platform == "win32":
            # check the windows font repository
            # NOTE: must use uppercase WINDIR, to work around bugs in
            # 1.5.2's os.environ.get()
            windir = os.environ.get("WINDIR")
            if windir:
                filename = os.path.join(windir, "fonts", font)
                return FreeTypeFont(filename, size, index, encoding)
        raise


def load_path(filename):
    """
    Load font file. Same as :py:func:`~PIL.ImageFont.load`, but searches for a
    bitmap font along the Python path.

    :param filename: Name of font file.
    :return: A font object.
    :exception IOError: If the file could not be read.
    """
    for dir in sys.path:
        if isDirectory(dir):
            if not isinstance(filename, str):
                if bytes is str:
                    filename = filename.encode("utf-8")
                else:
                    filename = filename.decode("utf-8")
            try:
                return load(os.path.join(dir, filename))
            except IOError:
                pass
    raise IOError("cannot find font file")


def load_default():
    """Load a "better than nothing" default font.

    .. versionadded:: 1.1.4

    :return: A font object.
    """
    from io import BytesIO
    import base64
    f = ImageFont()
    f._load_pilfont_data(
         # courB08
         BytesIO(base64.decodestring(b'''
UElMZm9udAo7Ozs7OzsxMDsKREFUQQoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAA//8AAQAAAAAAAAABAAEA
BgAAAAH/+gADAAAAAQAAAAMABgAGAAAAAf/6AAT//QADAAAABgADAAYAAAAA//kABQABAAYAAAAL
AAgABgAAAAD/+AAFAAEACwAAABAACQAGAAAAAP/5AAUAAAAQAAAAFQAHAAYAAP////oABQAAABUA
AAAbAAYABgAAAAH/+QAE//wAGwAAAB4AAwAGAAAAAf/5AAQAAQAeAAAAIQAIAAYAAAAB//kABAAB
ACEAAAAkAAgABgAAAAD/+QAE//0AJAAAACgABAAGAAAAAP/6AAX//wAoAAAALQAFAAYAAAAB//8A
BAACAC0AAAAwAAMABgAAAAD//AAF//0AMAAAADUAAQAGAAAAAf//AAMAAAA1AAAANwABAAYAAAAB
//kABQABADcAAAA7AAgABgAAAAD/+QAFAAAAOwAAAEAABwAGAAAAAP/5AAYAAABAAAAARgAHAAYA
AAAA//kABQAAAEYAAABLAAcABgAAAAD/+QAFAAAASwAAAFAABwAGAAAAAP/5AAYAAABQAAAAVgAH
AAYAAAAA//kABQAAAFYAAABbAAcABgAAAAD/+QAFAAAAWwAAAGAABwAGAAAAAP/5AAUAAABgAAAA
ZQAHAAYAAAAA//kABQAAAGUAAABqAAcABgAAAAD/+QAFAAAAagAAAG8ABwAGAAAAAf/8AAMAAABv
AAAAcQAEAAYAAAAA//wAAwACAHEAAAB0AAYABgAAAAD/+gAE//8AdAAAAHgABQAGAAAAAP/7AAT/
/gB4AAAAfAADAAYAAAAB//oABf//AHwAAACAAAUABgAAAAD/+gAFAAAAgAAAAIUABgAGAAAAAP/5
AAYAAQCFAAAAiwAIAAYAAP////oABgAAAIsAAACSAAYABgAA////+gAFAAAAkgAAAJgABgAGAAAA
AP/6AAUAAACYAAAAnQAGAAYAAP////oABQAAAJ0AAACjAAYABgAA////+gAFAAAAowAAAKkABgAG
AAD////6AAUAAACpAAAArwAGAAYAAAAA//oABQAAAK8AAAC0AAYABgAA////+gAGAAAAtAAAALsA
BgAGAAAAAP/6AAQAAAC7AAAAvwAGAAYAAP////oABQAAAL8AAADFAAYABgAA////+gAGAAAAxQAA
AMwABgAGAAD////6AAUAAADMAAAA0gAGAAYAAP////oABQAAANIAAADYAAYABgAA////+gAGAAAA
2AAAAN8ABgAGAAAAAP/6AAUAAADfAAAA5AAGAAYAAP////oABQAAAOQAAADqAAYABgAAAAD/+gAF
AAEA6gAAAO8ABwAGAAD////6AAYAAADvAAAA9gAGAAYAAAAA//oABQAAAPYAAAD7AAYABgAA////
+gAFAAAA+wAAAQEABgAGAAD////6AAYAAAEBAAABCAAGAAYAAP////oABgAAAQgAAAEPAAYABgAA
////+gAGAAABDwAAARYABgAGAAAAAP/6AAYAAAEWAAABHAAGAAYAAP////oABgAAARwAAAEjAAYA
BgAAAAD/+gAFAAABIwAAASgABgAGAAAAAf/5AAQAAQEoAAABKwAIAAYAAAAA//kABAABASsAAAEv
AAgABgAAAAH/+QAEAAEBLwAAATIACAAGAAAAAP/5AAX//AEyAAABNwADAAYAAAAAAAEABgACATcA
AAE9AAEABgAAAAH/+QAE//wBPQAAAUAAAwAGAAAAAP/7AAYAAAFAAAABRgAFAAYAAP////kABQAA
AUYAAAFMAAcABgAAAAD/+wAFAAABTAAAAVEABQAGAAAAAP/5AAYAAAFRAAABVwAHAAYAAAAA//sA
BQAAAVcAAAFcAAUABgAAAAD/+QAFAAABXAAAAWEABwAGAAAAAP/7AAYAAgFhAAABZwAHAAYAAP//
//kABQAAAWcAAAFtAAcABgAAAAD/+QAGAAABbQAAAXMABwAGAAAAAP/5AAQAAgFzAAABdwAJAAYA
AP////kABgAAAXcAAAF+AAcABgAAAAD/+QAGAAABfgAAAYQABwAGAAD////7AAUAAAGEAAABigAF
AAYAAP////sABQAAAYoAAAGQAAUABgAAAAD/+wAFAAABkAAAAZUABQAGAAD////7AAUAAgGVAAAB
mwAHAAYAAAAA//sABgACAZsAAAGhAAcABgAAAAD/+wAGAAABoQAAAacABQAGAAAAAP/7AAYAAAGn
AAABrQAFAAYAAAAA//kABgAAAa0AAAGzAAcABgAA////+wAGAAABswAAAboABQAGAAD////7AAUA
AAG6AAABwAAFAAYAAP////sABgAAAcAAAAHHAAUABgAAAAD/+wAGAAABxwAAAc0ABQAGAAD////7
AAYAAgHNAAAB1AAHAAYAAAAA//sABQAAAdQAAAHZAAUABgAAAAH/+QAFAAEB2QAAAd0ACAAGAAAA
Av/6AAMAAQHdAAAB3gAHAAYAAAAA//kABAABAd4AAAHiAAgABgAAAAD/+wAF//0B4gAAAecAAgAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAB
//sAAwACAecAAAHpAAcABgAAAAD/+QAFAAEB6QAAAe4ACAAGAAAAAP/5AAYAAAHuAAAB9AAHAAYA
AAAA//oABf//AfQAAAH5AAUABgAAAAD/+QAGAAAB+QAAAf8ABwAGAAAAAv/5AAMAAgH/AAACAAAJ
AAYAAAAA//kABQABAgAAAAIFAAgABgAAAAH/+gAE//sCBQAAAggAAQAGAAAAAP/5AAYAAAIIAAAC
DgAHAAYAAAAB//kABf/+Ag4AAAISAAUABgAA////+wAGAAACEgAAAhkABQAGAAAAAP/7AAX//gIZ
AAACHgADAAYAAAAA//wABf/9Ah4AAAIjAAEABgAAAAD/+QAHAAACIwAAAioABwAGAAAAAP/6AAT/
+wIqAAACLgABAAYAAAAA//kABP/8Ai4AAAIyAAMABgAAAAD/+gAFAAACMgAAAjcABgAGAAAAAf/5
AAT//QI3AAACOgAEAAYAAAAB//kABP/9AjoAAAI9AAQABgAAAAL/+QAE//sCPQAAAj8AAgAGAAD/
///7AAYAAgI/AAACRgAHAAYAAAAA//kABgABAkYAAAJMAAgABgAAAAH//AAD//0CTAAAAk4AAQAG
AAAAAf//AAQAAgJOAAACUQADAAYAAAAB//kABP/9AlEAAAJUAAQABgAAAAH/+QAF//4CVAAAAlgA
BQAGAAD////7AAYAAAJYAAACXwAFAAYAAP////kABgAAAl8AAAJmAAcABgAA////+QAGAAACZgAA
Am0ABwAGAAD////5AAYAAAJtAAACdAAHAAYAAAAA//sABQACAnQAAAJ5AAcABgAA////9wAGAAAC
eQAAAoAACQAGAAD////3AAYAAAKAAAAChwAJAAYAAP////cABgAAAocAAAKOAAkABgAA////9wAG
AAACjgAAApUACQAGAAD////4AAYAAAKVAAACnAAIAAYAAP////cABgAAApwAAAKjAAkABgAA////
+gAGAAACowAAAqoABgAGAAAAAP/6AAUAAgKqAAACrwAIAAYAAP////cABQAAAq8AAAK1AAkABgAA
////9wAFAAACtQAAArsACQAGAAD////3AAUAAAK7AAACwQAJAAYAAP////gABQAAAsEAAALHAAgA
BgAAAAD/9wAEAAACxwAAAssACQAGAAAAAP/3AAQAAALLAAACzwAJAAYAAAAA//cABAAAAs8AAALT
AAkABgAAAAD/+AAEAAAC0wAAAtcACAAGAAD////6AAUAAALXAAAC3QAGAAYAAP////cABgAAAt0A
AALkAAkABgAAAAD/9wAFAAAC5AAAAukACQAGAAAAAP/3AAUAAALpAAAC7gAJAAYAAAAA//cABQAA
Au4AAALzAAkABgAAAAD/9wAFAAAC8wAAAvgACQAGAAAAAP/4AAUAAAL4AAAC/QAIAAYAAAAA//oA
Bf//Av0AAAMCAAUABgAA////+gAGAAADAgAAAwkABgAGAAD////3AAYAAAMJAAADEAAJAAYAAP//
//cABgAAAxAAAAMXAAkABgAA////9wAGAAADFwAAAx4ACQAGAAD////4AAYAAAAAAAoABwASAAYA
AP////cABgAAAAcACgAOABMABgAA////+gAFAAAADgAKABQAEAAGAAD////6AAYAAAAUAAoAGwAQ
AAYAAAAA//gABgAAABsACgAhABIABgAAAAD/+AAGAAAAIQAKACcAEgAGAAAAAP/4AAYAAAAnAAoA
LQASAAYAAAAA//gABgAAAC0ACgAzABIABgAAAAD/+QAGAAAAMwAKADkAEQAGAAAAAP/3AAYAAAA5
AAoAPwATAAYAAP////sABQAAAD8ACgBFAA8ABgAAAAD/+wAFAAIARQAKAEoAEQAGAAAAAP/4AAUA
AABKAAoATwASAAYAAAAA//gABQAAAE8ACgBUABIABgAAAAD/+AAFAAAAVAAKAFkAEgAGAAAAAP/5
AAUAAABZAAoAXgARAAYAAAAA//gABgAAAF4ACgBkABIABgAAAAD/+AAGAAAAZAAKAGoAEgAGAAAA
AP/4AAYAAABqAAoAcAASAAYAAAAA//kABgAAAHAACgB2ABEABgAAAAD/+AAFAAAAdgAKAHsAEgAG
AAD////4AAYAAAB7AAoAggASAAYAAAAA//gABQAAAIIACgCHABIABgAAAAD/+AAFAAAAhwAKAIwA
EgAGAAAAAP/4AAUAAACMAAoAkQASAAYAAAAA//gABQAAAJEACgCWABIABgAAAAD/+QAFAAAAlgAK
AJsAEQAGAAAAAP/6AAX//wCbAAoAoAAPAAYAAAAA//oABQABAKAACgClABEABgAA////+AAGAAAA
pQAKAKwAEgAGAAD////4AAYAAACsAAoAswASAAYAAP////gABgAAALMACgC6ABIABgAA////+QAG
AAAAugAKAMEAEQAGAAD////4AAYAAgDBAAoAyAAUAAYAAP////kABQACAMgACgDOABMABgAA////
+QAGAAIAzgAKANUAEw==
''')), Image.open(BytesIO(base64.decodestring(b'''
iVBORw0KGgoAAAANSUhEUgAAAx4AAAAUAQAAAAArMtZoAAAEwElEQVR4nABlAJr/AHVE4czCI/4u
Mc4b7vuds/xzjz5/3/7u/n9vMe7vnfH/9++vPn/xyf5zhxzjt8GHw8+2d83u8x27199/nxuQ6Od9
M43/5z2I+9n9ZtmDBwMQECDRQw/eQIQohJXxpBCNVE6QCCAAAAD//wBlAJr/AgALyj1t/wINwq0g
LeNZUworuN1cjTPIzrTX6ofHWeo3v336qPzfEwRmBnHTtf95/fglZK5N0PDgfRTslpGBvz7LFc4F
IUXBWQGjQ5MGCx34EDFPwXiY4YbYxavpnhHFrk14CDAAAAD//wBlAJr/AgKqRooH2gAgPeggvUAA
Bu2WfgPoAwzRAABAAAAAAACQgLz/3Uv4Gv+gX7BJgDeeGP6AAAD1NMDzKHD7ANWr3loYbxsAD791
NAADfcoIDyP44K/jv4Y63/Z+t98Ovt+ub4T48LAAAAD//wBlAJr/AuplMlADJAAAAGuAphWpqhMx
in0A/fRvAYBABPgBwBUgABBQ/sYAyv9g0bCHgOLoGAAAAAAAREAAwI7nr0ArYpow7aX8//9LaP/9
SjdavWA8ePHeBIKB//81/83ndznOaXx379wAAAD//wBlAJr/AqDxW+D3AABAAbUh/QMnbQag/gAY
AYDAAACgtgD/gOqAAAB5IA/8AAAk+n9w0AAA8AAAmFRJuPo27ciC0cD5oeW4E7KA/wD3ECMAn2tt
y8PgwH8AfAxFzC0JzeAMtratAsC/ffwAAAD//wBlAJr/BGKAyCAA4AAAAvgeYTAwHd1kmQF5chkG
ABoMIHcL5xVpTfQbUqzlAAAErwAQBgAAEOClA5D9il08AEh/tUzdCBsXkbgACED+woQg8Si9VeqY
lODCn7lmF6NhnAEYgAAA/NMIAAAAAAD//2JgjLZgVGBg5Pv/Tvpc8hwGBjYGJADjHDrAwPzAjv/H
/Wf3PzCwtzcwHmBgYGcwbZz8wHaCAQMDOwMDQ8MCBgYOC3W7mp+f0w+wHOYxO3OG+e376hsMZjk3
AAAAAP//YmCMY2A4wMAIN5e5gQETPD6AZisDAwMDgzSDAAPjByiHcQMDAwMDg1nOze1lByRu5/47
c4859311AYNZzg0AAAAA//9iYGDBYihOIIMuwIjGL39/fwffA8b//xv/P2BPtzzHwCBjUQAAAAD/
/yLFBrIBAAAA//9i1HhcwdhizX7u8NZNzyLbvT97bfrMf/QHI8evOwcSqGUJAAAA//9iYBB81iSw
pEE170Qrg5MIYydHqwdDQRMrAwcVrQAAAAD//2J4x7j9AAMDn8Q/BgYLBoaiAwwMjPdvMDBYM1Tv
oJodAAAAAP//Yqo/83+dxePWlxl3npsel9lvLfPcqlE9725C+acfVLMEAAAA//9i+s9gwCoaaGMR
evta/58PTEWzr21hufPjA8N+qlnBwAAAAAD//2JiWLci5v1+HmFXDqcnULE/MxgYGBj+f6CaJQAA
AAD//2Ji2FrkY3iYpYC5qDeGgeEMAwPDvwQBBoYvcTwOVLMEAAAA//9isDBgkP///0EOg9z35v//
Gc/eeW7BwPj5+QGZhANUswMAAAD//2JgqGBgYGBgqEMXlvhMPUsAAAAA//8iYDd1AAAAAP//AwDR
w7IkEbzhVQAAAABJRU5ErkJggg==
'''))))
    return f


if __name__ == "__main__":
    # create font data chunk for embedding
    import base64, os, sys
    font = "../Images/courB08"
    print("    f._load_pilfont_data(")
    print("         # %s" % os.path.basename(font))
    print("         BytesIO(base64.decodestring(b'''")
    base64.encode(open(font + ".pil", "rb"), sys.stdout)
    print("''')), Image.open(BytesIO(base64.decodestring(b'''")
    base64.encode(open(font + ".pbm", "rb"), sys.stdout)
    print("'''))))")
