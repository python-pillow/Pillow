#
# The Python Imaging Library.
# $Id$
#
# GIF file handling
#
# History:
# 1995-09-01 fl   Created
# 1996-12-14 fl   Added interlace support
# 1996-12-30 fl   Added animation support
# 1997-01-05 fl   Added write support, fixed local colour map bug
# 1997-02-23 fl   Make sure to load raster data in getdata()
# 1997-07-05 fl   Support external decoder (0.4)
# 1998-07-09 fl   Handle all modes when saving (0.5)
# 1998-07-15 fl   Renamed offset attribute to avoid name clash
# 2001-04-16 fl   Added rewind support (seek to frame 0) (0.6)
# 2001-04-17 fl   Added palette optimization (0.7)
# 2002-06-06 fl   Added transparency support for save (0.8)
# 2004-02-24 fl   Disable interlacing for small images
#
# Copyright (c) 1997-2004 by Secret Labs AB
# Copyright (c) 1995-2004 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#


__version__ = "0.9"


import Image, ImageFile, ImagePalette


# --------------------------------------------------------------------
# Helpers

def i16(c):
    return ord(c[0]) + (ord(c[1])<<8)

def o16(i):
    return chr(i&255) + chr(i>>8&255)


# --------------------------------------------------------------------
# Identify/read GIF files

def _accept(prefix):
    return prefix[:6] in ["GIF87a", "GIF89a"]

##
# Image plugin for GIF images.  This plugin supports both GIF87 and
# GIF89 images.

class GifImageFile(ImageFile.ImageFile):

    format = "GIF"
    format_description = "Compuserve GIF"

    global_palette = None

    def data(self):
        s = self.fp.read(1)
        if s and ord(s):
            return self.fp.read(ord(s))
        return None

    def _open(self):

        # Screen
        s = self.fp.read(13)
        if s[:6] not in ["GIF87a", "GIF89a"]:
            raise SyntaxError, "not a GIF file"

        self.info["version"] = s[:6]

        self.size = i16(s[6:]), i16(s[8:])

        self.tile = []

        flags = ord(s[10])

        bits = (flags & 7) + 1

        if flags & 128:
            # get global palette
            self.info["background"] = ord(s[11])
            # check if palette contains colour indices
            p = self.fp.read(3<<bits)
            for i in range(0, len(p), 3):
                if not (chr(i/3) == p[i] == p[i+1] == p[i+2]):
                    p = ImagePalette.raw("RGB", p)
                    self.global_palette = self.palette = p
                    break

        self.__fp = self.fp # FIXME: hack
        self.__rewind = self.fp.tell()
        self.seek(0) # get ready to read first frame

    def seek(self, frame):

        if frame == 0:
            # rewind
            self.__offset = 0
            self.dispose = None
            self.__frame = -1
            self.__fp.seek(self.__rewind)

        if frame != self.__frame + 1:
            raise ValueError, "cannot seek to frame %d" % frame
        self.__frame = frame

        self.tile = []

        self.fp = self.__fp
        if self.__offset:
            # backup to last frame
            self.fp.seek(self.__offset)
            while self.data():
                pass
            self.__offset = 0

        if self.dispose:
            self.im = self.dispose
            self.dispose = None

        self.palette = self.global_palette

        while 1:

            s = self.fp.read(1)
            if not s or s == ";":
                break

            elif s == "!":
                #
                # extensions
                #
                s = self.fp.read(1)
                block = self.data()
                if ord(s) == 249:
                    #
                    # graphic control extension
                    #
                    flags = ord(block[0])
                    if flags & 1:
                        self.info["transparency"] = ord(block[3])
                    self.info["duration"] = i16(block[1:3]) * 10
                    try:
                        # disposal methods
                        if flags & 8:
                            # replace with background colour
                            self.dispose = Image.core.fill("P", self.size,
                                self.info["background"])
                        elif flags & 16:
                            # replace with previous contents
                            self.dispose = self.im.copy()
                    except (AttributeError, KeyError):
                        pass
                elif ord(s) == 255:
                    #
                    # application extension
                    #
                    self.info["extension"] = block, self.fp.tell()
                    if block[:11] == "NETSCAPE2.0":
                        block = self.data()
                        if len(block) >= 3 and ord(block[0]) == 1:
                            self.info["loop"] = i16(block[1:3])
                while self.data():
                    pass

            elif s == ",":
                #
                # local image
                #
                s = self.fp.read(9)

                # extent
                x0, y0 = i16(s[0:]), i16(s[2:])
                x1, y1 = x0 + i16(s[4:]), y0 + i16(s[6:])
                flags = ord(s[8])

                interlace = (flags & 64) != 0

                if flags & 128:
                    bits = (flags & 7) + 1
                    self.palette =\
                        ImagePalette.raw("RGB", self.fp.read(3<<bits))

                # image data
                bits = ord(self.fp.read(1))
                self.__offset = self.fp.tell()
                self.tile = [("gif",
                             (x0, y0, x1, y1),
                             self.__offset,
                             (bits, interlace))]
                break

            else:
                pass
                # raise IOError, "illegal GIF tag `%x`" % ord(s)

        if not self.tile:
            # self.__fp = None
            raise EOFError, "no more images in GIF file"

        self.mode = "L"
        if self.palette:
            self.mode = "P"

    def tell(self):
        return self.__frame


# --------------------------------------------------------------------
# Write GIF files

try:
    import _imaging_gif
except ImportError:
    _imaging_gif = None

RAWMODE = {
    "1": "L",
    "L": "L",
    "P": "P",
}

def _save(im, fp, filename):

    if _imaging_gif:
        # call external driver
        try:
            _imaging_gif.save(im, fp, filename)
            return
        except IOError:
            pass # write uncompressed file

    try:
        rawmode = RAWMODE[im.mode]
        imOut = im
    except KeyError:
        # convert on the fly (EXPERIMENTAL -- I'm not sure PIL
        # should automatically convert images on save...)
        if Image.getmodebase(im.mode) == "RGB":
            imOut = im.convert("P")
            rawmode = "P"
        else:
            imOut = im.convert("L")
            rawmode = "L"

    # header
    for s in getheader(imOut, im.encoderinfo):
        fp.write(s)

    flags = 0

    try:
        interlace = im.encoderinfo["interlace"]
    except KeyError:
        interlace = 1

    # workaround for @PIL153
    if min(im.size) < 16:
        interlace = 0

    if interlace:
        flags = flags | 64

    try:
        transparency = im.encoderinfo["transparency"]
    except KeyError:
        pass
    else:
        # transparency extension block
        fp.write("!" +
                 chr(249) +             # extension intro
                 chr(4) +               # length
                 chr(1) +               # transparency info present
                 o16(0) +               # duration
                 chr(int(transparency)) # transparency index
                 + chr(0))

    # local image header
    fp.write("," +
             o16(0) + o16(0) +          # bounding box
             o16(im.size[0]) +          # size
             o16(im.size[1]) +
             chr(flags) +               # flags
             chr(8))                    # bits

    imOut.encoderconfig = (8, interlace)

    ImageFile._save(imOut, fp, [("gif", (0,0)+im.size, 0, rawmode)])

    fp.write("\0") # end of image data

    fp.write(";") # end of file

    try:
        fp.flush()
    except: pass

def _save_netpbm(im, fp, filename):

    #
    # If you need real GIF compression and/or RGB quantization, you
    # can use the external NETPBM/PBMPLUS utilities.  See comments
    # below for information on how to enable this.

    import os
    file = im._dump()
    if im.mode != "RGB":
        os.system("ppmtogif %s >%s" % (file, filename))
    else:
        os.system("ppmquant 256 %s | ppmtogif >%s" % (file, filename))
    try: os.unlink(file)
    except: pass


# --------------------------------------------------------------------
# GIF utilities

def getheader(im, info=None):
    """Return a list of strings representing a GIF header"""

    optimize = info and info.get("optimize", 0)

    s = [
        "GIF87a" +              # magic
        o16(im.size[0]) +       # size
        o16(im.size[1]) +
        chr(7 + 128) +          # flags: bits + palette
        chr(0) +                # background
        chr(0)                  # reserved/aspect
    ]

    if optimize:
        # minimize color palette
        i = 0
        maxcolor = 0
        for count in im.histogram():
            if count:
                maxcolor = i
            i = i + 1
    else:
        maxcolor = 256

    # global palette
    if im.mode == "P":
        # colour palette
        s.append(im.im.getpalette("RGB")[:maxcolor*3])
    else:
        # greyscale
        for i in range(maxcolor):
            s.append(chr(i) * 3)

    return s

def getdata(im, offset = (0, 0), **params):
    """Return a list of strings representing this image.
       The first string is a local image header, the rest contains
       encoded image data."""

    class collector:
        data = []
        def write(self, data):
            self.data.append(data)

    im.load() # make sure raster data is available

    fp = collector()

    try:
        im.encoderinfo = params

        # local image header
        fp.write("," +
                 o16(offset[0]) +       # offset
                 o16(offset[1]) +
                 o16(im.size[0]) +      # size
                 o16(im.size[1]) +
                 chr(0) +               # flags
                 chr(8))                # bits

        ImageFile._save(im, fp, [("gif", (0,0)+im.size, 0, RAWMODE[im.mode])])

        fp.write("\0") # end of image data

    finally:
        del im.encoderinfo

    return fp.data


# --------------------------------------------------------------------
# Registry

Image.register_open(GifImageFile.format, GifImageFile, _accept)
Image.register_save(GifImageFile.format, _save)
Image.register_extension(GifImageFile.format, ".gif")
Image.register_mime(GifImageFile.format, "image/gif")

#
# Uncomment the following line if you wish to use NETPBM/PBMPLUS
# instead of the built-in "uncompressed" GIF encoder

# Image.register_save(GifImageFile.format, _save_netpbm)
