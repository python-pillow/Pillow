#
# The Python Imaging Library.
# $Id$
#
# image palette object
#
# History:
# 1996-03-11 fl   Rewritten.
# 1997-01-03 fl   Up and running.
# 1997-08-23 fl   Added load hack
# 2001-04-16 fl   Fixed randint shadow bug in random()
#
# Copyright (c) 1997-2001 by Secret Labs AB
# Copyright (c) 1996-1997 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

import array
from PIL import Image, ImageColor


class ImagePalette:
    "Color palette for palette mapped images"

    def __init__(self, mode = "RGB", palette = None):
        self.mode = mode
        self.rawmode = None # if set, palette contains raw data
        self.palette = palette or list(range(256))*len(self.mode)
        self.colors = {}
        self.dirty = None
        if len(self.mode)*256 != len(self.palette):
            raise ValueError("wrong palette size")

    def getdata(self):
        """
        Get palette contents in format suitable # for the low-level
        ``im.putpalette`` primitive.

        .. warning:: This method is experimental.
        """
        if self.rawmode:
            return self.rawmode, self.palette
        return self.mode + ";L", self.tobytes()

    def tobytes(self):
        """Convert palette to bytes.

        .. warning:: This method is experimental.
        """
        if self.rawmode:
            raise ValueError("palette contains raw palette data")
        if isinstance(self.palette, bytes):
            return self.palette
        arr = array.array("B", self.palette)
        if hasattr(arr, 'tobytes'):
            #py3k has a tobytes, tostring is deprecated.
            return arr.tobytes()
        return arr.tostring()

    # Declare tostring as an alias for tobytes
    tostring = tobytes

    def getcolor(self, color):
        """Given an rgb tuple, allocate palette entry.

        .. warning:: This method is experimental.
        """
        if self.rawmode:
            raise ValueError("palette contains raw palette data")
        if isinstance(color, tuple):
            try:
                return self.colors[color]
            except KeyError:
                # allocate new color slot
                if isinstance(self.palette, bytes):
                    self.palette = [int(x) for x in self.palette]
                index = len(self.colors)
                if index >= 256:
                    raise ValueError("cannot allocate more than 256 colors")
                self.colors[color] = index
                self.palette[index] = color[0]
                self.palette[index+256] = color[1]
                self.palette[index+512] = color[2]
                self.dirty = 1
                return index
        else:
            raise ValueError("unknown color specifier: %r" % color)

    def save(self, fp):
        """Save palette to text file.

        .. warning:: This method is experimental.
        """
        if self.rawmode:
            raise ValueError("palette contains raw palette data")
        if isinstance(fp, str):
            fp = open(fp, "w")
        fp.write("# Palette\n")
        fp.write("# Mode: %s\n" % self.mode)
        for i in range(256):
            fp.write("%d" % i)
            for j in range(i, len(self.palette), 256):
                fp.write(" %d" % self.palette[j])
            fp.write("\n")
        fp.close()

# --------------------------------------------------------------------
# Internal

def raw(rawmode, data):
    palette = ImagePalette()
    palette.rawmode = rawmode
    palette.palette = data
    palette.dirty = 1
    return palette

# --------------------------------------------------------------------
# Factories

def _make_linear_lut(black, white):
    lut = []
    if black == 0:
        for i in range(256):
            lut.append(white*i//255)
    else:
        raise NotImplementedError # FIXME
    return lut

def _make_gamma_lut(exp, mode="RGB"):
    lut = []
    for i in range(256):
        lut.append(int(((i / 255.0) ** exp) * 255.0 + 0.5))
    return lut

def new(mode, data):
    return Image.core.new_palette(mode, data)

def negative(mode="RGB"):
    palette = list(range(256))
    palette.reverse()
    return ImagePalette(mode, palette * len(mode))

def random(mode="RGB"):
    from random import randint
    palette = []
    for i in range(256*len(mode)):
        palette.append(randint(0, 255))
    return ImagePalette(mode, palette)

def sepia(white="#fff0c0"):
    r, g, b = ImageColor.getrgb(white)
    r = _make_linear_lut(0, r)
    g = _make_linear_lut(0, g)
    b = _make_linear_lut(0, b)
    return ImagePalette("RGB", r + g + b)

def wedge(mode="RGB"):
    return ImagePalette(mode, list(range(256)) * len(mode))

def load(filename):

    # FIXME: supports GIMP gradients only

    fp = open(filename, "rb")

    lut = None

    if not lut:
        try:
            from PIL import GimpPaletteFile
            fp.seek(0)
            p = GimpPaletteFile.GimpPaletteFile(fp)
            lut = p.getpalette()
        except (SyntaxError, ValueError):
            #import traceback
            #traceback.print_exc()
            pass

    if not lut:
        try:
            from PIL import GimpGradientFile
            fp.seek(0)
            p = GimpGradientFile.GimpGradientFile(fp)
            lut = p.getpalette()
        except (SyntaxError, ValueError):
            #import traceback
            #traceback.print_exc()
            pass

    if not lut:
        try:
            from PIL import PaletteFile
            fp.seek(0)
            p = PaletteFile.PaletteFile(fp)
            lut = p.getpalette()
        except (SyntaxError, ValueError):
            import traceback
            traceback.print_exc()
            pass

    if not lut:
        raise IOError("cannot load palette")

    return lut # data, rawmode
