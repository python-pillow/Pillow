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

from PIL import Image, ImageFile, ImagePalette, _binary

__version__ = "0.9"


# --------------------------------------------------------------------
# Helpers

i8 = _binary.i8
i16 = _binary.i16le
o8 = _binary.o8
o16 = _binary.o16le


# --------------------------------------------------------------------
# Identify/read GIF files

def _accept(prefix):
    return prefix[:6] in [b"GIF87a", b"GIF89a"]


##
# Image plugin for GIF images.  This plugin supports both GIF87 and
# GIF89 images.

class GifImageFile(ImageFile.ImageFile):

    format = "GIF"
    format_description = "Compuserve GIF"
    global_palette = None

    def data(self):
        s = self.fp.read(1)
        if s and i8(s):
            return self.fp.read(i8(s))
        return None

    def _open(self):

        # Screen
        s = self.fp.read(13)
        if s[:6] not in [b"GIF87a", b"GIF89a"]:
            raise SyntaxError("not a GIF file")

        self.info["version"] = s[:6]
        self.size = i16(s[6:]), i16(s[8:])
        self.tile = []
        flags = i8(s[10])
        bits = (flags & 7) + 1

        if flags & 128:
            # get global palette
            self.info["background"] = i8(s[11])
            # check if palette contains colour indices
            p = self.fp.read(3 << bits)
            for i in range(0, len(p), 3):
                if not (i//3 == i8(p[i]) == i8(p[i+1]) == i8(p[i+2])):
                    p = ImagePalette.raw("RGB", p)
                    self.global_palette = self.palette = p
                    break

        self.__fp = self.fp  # FIXME: hack
        self.__rewind = self.fp.tell()
        self.seek(0)  # get ready to read first frame

    def seek(self, frame):

        if frame == 0:
            # rewind
            self.__offset = 0
            self.dispose = None
            self.dispose_extent = [0, 0, 0, 0]  # x0, y0, x1, y1
            self.__frame = -1
            self.__fp.seek(self.__rewind)
            self._prev_im = None
            self.disposal_method = 0
        else:
            # ensure that the previous frame was loaded
            if not self.im:
                self.load()

        if frame != self.__frame + 1:
            raise ValueError("cannot seek to frame %d" % frame)
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
            self.im.paste(self.dispose, self.dispose_extent)

        from copy import copy
        self.palette = copy(self.global_palette)

        while True:

            s = self.fp.read(1)
            if not s or s == b";":
                break

            elif s == b"!":
                #
                # extensions
                #
                s = self.fp.read(1)
                block = self.data()
                if i8(s) == 249:
                    #
                    # graphic control extension
                    #
                    flags = i8(block[0])
                    if flags & 1:
                        self.info["transparency"] = i8(block[3])
                    self.info["duration"] = i16(block[1:3]) * 10

                    # disposal method - find the value of bits 4 - 6
                    dispose_bits = 0b00011100 & flags
                    dispose_bits = dispose_bits >> 2
                    if dispose_bits:
                        # only set the dispose if it is not
                        # unspecified. I'm not sure if this is
                        # correct, but it seems to prevent the last
                        # frame from looking odd for some animations
                        self.disposal_method = dispose_bits
                elif i8(s) == 255:
                    #
                    # application extension
                    #
                    self.info["extension"] = block, self.fp.tell()
                    if block[:11] == b"NETSCAPE2.0":
                        block = self.data()
                        if len(block) >= 3 and i8(block[0]) == 1:
                            self.info["loop"] = i16(block[1:3])
                while self.data():
                    pass

            elif s == b",":
                #
                # local image
                #
                s = self.fp.read(9)

                # extent
                x0, y0 = i16(s[0:]), i16(s[2:])
                x1, y1 = x0 + i16(s[4:]), y0 + i16(s[6:])
                self.dispose_extent = x0, y0, x1, y1
                flags = i8(s[8])

                interlace = (flags & 64) != 0

                if flags & 128:
                    bits = (flags & 7) + 1
                    self.palette =\
                        ImagePalette.raw("RGB", self.fp.read(3 << bits))

                # image data
                bits = i8(self.fp.read(1))
                self.__offset = self.fp.tell()
                self.tile = [("gif",
                             (x0, y0, x1, y1),
                             self.__offset,
                             (bits, interlace))]
                break

            else:
                pass
                # raise IOError, "illegal GIF tag `%x`" % i8(s)

        try:
            if self.disposal_method < 2:
                # do not dispose or none specified
                self.dispose = None
            elif self.disposal_method == 2:
                # replace with background colour
                self.dispose = Image.core.fill("P", self.size,
                                               self.info["background"])
            else:
                # replace with previous contents
                if self.im:
                    self.dispose = self.im.copy()

            # only dispose the extent in this frame
            if self.dispose:
                self.dispose = self.dispose.crop(self.dispose_extent)
        except (AttributeError, KeyError):
            pass

        if not self.tile:
            # self.__fp = None
            raise EOFError("no more images in GIF file")

        self.mode = "L"
        if self.palette:
            self.mode = "P"

    def tell(self):
        return self.__frame

    def load_end(self):
        ImageFile.ImageFile.load_end(self)

        # if the disposal method is 'do not dispose', transparent
        # pixels should show the content of the previous frame
        if self._prev_im and self.disposal_method == 1:
            # we do this by pasting the updated area onto the previous
            # frame which we then use as the current image content
            updated = self.im.crop(self.dispose_extent)
            self._prev_im.paste(updated, self.dispose_extent,
                                updated.convert('RGBA'))
            self.im = self._prev_im
        self._prev_im = self.im.copy()

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
            pass  # write uncompressed file

    if im.mode in RAWMODE:
        im_out = im
    else:
        # convert on the fly (EXPERIMENTAL -- I'm not sure PIL
        # should automatically convert images on save...)
        if Image.getmodebase(im.mode) == "RGB":
            palette_size = 256
            if im.palette:
                palette_size = len(im.palette.getdata()[1]) // 3
            im_out = im.convert("P", palette=1, colors=palette_size)
        else:
            im_out = im.convert("L")

    # header
    try:
        palette = im.encoderinfo["palette"]
    except KeyError:
        palette = None
        im.encoderinfo["optimize"] = im.encoderinfo.get("optimize", True)

    header, used_palette_colors = getheader(im_out, palette, im.encoderinfo)
    for s in header:
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
        transparency = int(transparency)
        # optimize the block away if transparent color is not used
        transparent_color_exists = True
        # adjust the transparency index after optimize
        if used_palette_colors is not None and len(used_palette_colors) < 256:
            for i in range(len(used_palette_colors)):
                if used_palette_colors[i] == transparency:
                    transparency = i
                    transparent_color_exists = True
                    break
                else:
                    transparent_color_exists = False

        # transparency extension block
        if transparent_color_exists:
            fp.write(b"!" +
                     o8(249) +              # extension intro
                     o8(4) +                # length
                     o8(1) +                # transparency info present
                     o16(0) +               # duration
                     o8(transparency) +     # transparency index
                     o8(0))

    # local image header
    fp.write(b"," +
             o16(0) + o16(0) +          # bounding box
             o16(im.size[0]) +          # size
             o16(im.size[1]) +
             o8(flags) +                # flags
             o8(8))                     # bits

    im_out.encoderconfig = (8, interlace)
    ImageFile._save(im_out, fp, [("gif", (0, 0)+im.size, 0,
                                  RAWMODE[im_out.mode])])

    fp.write(b"\0")  # end of image data

    fp.write(b";")  # end of file

    try:
        fp.flush()
    except:
        pass


def _save_netpbm(im, fp, filename):

    #
    # If you need real GIF compression and/or RGB quantization, you
    # can use the external NETPBM/PBMPLUS utilities.  See comments
    # below for information on how to enable this.

    import os
    from subprocess import Popen, check_call, PIPE, CalledProcessError
    import tempfile
    file = im._dump()

    if im.mode != "RGB":
        with open(filename, 'wb') as f:
            stderr = tempfile.TemporaryFile()
            check_call(["ppmtogif", file], stdout=f, stderr=stderr)
    else:
        with open(filename, 'wb') as f:

            # Pipe ppmquant output into ppmtogif
            # "ppmquant 256 %s | ppmtogif > %s" % (file, filename)
            quant_cmd = ["ppmquant", "256", file]
            togif_cmd = ["ppmtogif"]
            stderr = tempfile.TemporaryFile()
            quant_proc = Popen(quant_cmd, stdout=PIPE, stderr=stderr)
            stderr = tempfile.TemporaryFile()
            togif_proc = Popen(togif_cmd, stdin=quant_proc.stdout, stdout=f,
                               stderr=stderr)

            # Allow ppmquant to receive SIGPIPE if ppmtogif exits
            quant_proc.stdout.close()

            retcode = quant_proc.wait()
            if retcode:
                raise CalledProcessError(retcode, quant_cmd)

            retcode = togif_proc.wait()
            if retcode:
                raise CalledProcessError(retcode, togif_cmd)

    try:
        os.unlink(file)
    except:
        pass


# --------------------------------------------------------------------
# GIF utilities

def getheader(im, palette=None, info=None):
    """Return a list of strings representing a GIF header"""

    optimize = info and info.get("optimize", 0)

    # Header Block
    # http://www.matthewflickinger.com/lab/whatsinagif/bits_and_bytes.asp
    header = [
        b"GIF87a" +             # signature + version
        o16(im.size[0]) +       # canvas width
        o16(im.size[1])         # canvas height
    ]

    if im.mode == "P":
        if palette and isinstance(palette, bytes):
            source_palette = palette[:768]
        else:
            source_palette = im.im.getpalette("RGB")[:768]
    else:  # L-mode
        if palette and isinstance(palette, bytes):
            source_palette = palette[:768]
        else:
            source_palette = bytearray([i//3 for i in range(768)])

    used_palette_colors = palette_bytes = None

    if im.mode in ("P", "L") and optimize:
        used_palette_colors = []

        # check which colors are used
        i = 0
        for count in im.histogram():
            if count:
                used_palette_colors.append(i)
            i += 1

        # create the new palette if not every color is used
        if len(used_palette_colors) < 256:
            palette_bytes = b""
            new_positions = {}

            i = 0
            # pick only the used colors from the palette
            for oldPosition in used_palette_colors:
                palette_bytes += source_palette[oldPosition*3:oldPosition*3+3]
                new_positions[oldPosition] = i
                i += 1

            # replace the palette color id of all pixel with the new id
            image_bytes = bytearray(im.tobytes())
            for i in range(len(image_bytes)):
                image_bytes[i] = new_positions[image_bytes[i]]
            im.frombytes(bytes(image_bytes))
            new_palette_bytes = (palette_bytes +
                                 (768 - len(palette_bytes)) * b'\x00')
            im.putpalette(new_palette_bytes)
            im.palette = ImagePalette.ImagePalette("RGB",
                                                   palette=palette_bytes,
                                                   size=len(palette_bytes))

    if not palette_bytes:
        palette_bytes = source_palette

    # Logical Screen Descriptor
    # calculate the palette size for the header
    import math
    color_table_size = int(math.ceil(math.log(len(palette_bytes)//3, 2)))-1
    if color_table_size < 0:
        color_table_size = 0
    # size of global color table + global color table flag
    header.append(o8(color_table_size + 128))
    # background + reserved/aspect
    header.append(o8(0) + o8(0))
    # end of Logical Screen Descriptor

    # add the missing amount of bytes
    # the palette has to be 2<<n in size
    actual_target_size_diff = (2 << color_table_size) - len(palette_bytes)//3
    if actual_target_size_diff > 0:
        palette_bytes += o8(0) * 3 * actual_target_size_diff

    # Header + Logical Screen Descriptor + Global Color Table
    header.append(palette_bytes)
    return header, used_palette_colors


def getdata(im, offset=(0, 0), **params):
    """Return a list of strings representing this image.
       The first string is a local image header, the rest contains
       encoded image data."""

    class Collector:
        data = []

        def write(self, data):
            self.data.append(data)

    im.load()  # make sure raster data is available

    fp = Collector()

    try:
        im.encoderinfo = params

        # local image header
        fp.write(b"," +
                 o16(offset[0]) +       # offset
                 o16(offset[1]) +
                 o16(im.size[0]) +      # size
                 o16(im.size[1]) +
                 o8(0) +                # flags
                 o8(8))                 # bits

        ImageFile._save(im, fp, [("gif", (0, 0)+im.size, 0, RAWMODE[im.mode])])

        fp.write(b"\0")  # end of image data

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
