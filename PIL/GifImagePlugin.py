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

from PIL import Image, ImageFile, ImagePalette, \
                ImageChops, ImageSequence, _binary

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
        self._n_frames = None
        self._is_animated = None
        self._seek(0)  # get ready to read first frame

    @property
    def n_frames(self):
        if self._n_frames is None:
            current = self.tell()
            try:
                while True:
                    self.seek(self.tell() + 1)
            except EOFError:
                self._n_frames = self.tell() + 1
            self.seek(current)
        return self._n_frames

    @property
    def is_animated(self):
        if self._is_animated is None:
            current = self.tell()

            try:
                self.seek(1)
                self._is_animated = True
            except EOFError:
                self._is_animated = False

            self.seek(current)
        return self._is_animated

    def seek(self, frame):
        if frame == self.__frame:
            return
        if frame < self.__frame:
            self._seek(0)

        last_frame = self.__frame
        for f in range(self.__frame + 1, frame + 1):
            try:
                self._seek(f)
            except EOFError:
                self.seek(last_frame)
                raise EOFError("no more images in GIF file")

    def _seek(self, frame):

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
                elif i8(s) == 254:
                    #
                    # comment extension
                    #
                    self.info["comment"] = block
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
            raise EOFError

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


def _convert_mode(im, initial_call=False):
    # convert on the fly (EXPERIMENTAL -- I'm not sure PIL
    # should automatically convert images on save...)
    if Image.getmodebase(im.mode) == "RGB":
        if initial_call:
            palette_size = 256
            if im.palette:
                palette_size = len(im.palette.getdata()[1]) // 3
            return im.convert("P", palette=1, colors=palette_size)
        else:
            return im.convert("P")
    return im.convert("L")


def _save_all(im, fp, filename):
    _save(im, fp, filename, save_all=True)


def _save(im, fp, filename, save_all=False):

    im.encoderinfo.update(im.info)
    if _imaging_gif:
        # call external driver
        try:
            _imaging_gif.save(im, fp, filename)
            return
        except IOError:
            pass  # write uncompressed file

    if im.mode in RAWMODE:
        im_out = im.copy()
    else:
        im_out = _convert_mode(im, True)

    # header
    try:
        palette = im.encoderinfo["palette"]
    except KeyError:
        palette = None
        im.encoderinfo["optimize"] = im.encoderinfo.get("optimize", True)

    if save_all:
        previous = None

        first_frame = None
        append_images = im.encoderinfo.get("append_images", [])
        if "duration" in im.encoderinfo:
            duration = im.encoderinfo["duration"]
        else:
            duration = None
        frame_count = 0
        for imSequence in [im]+append_images:
            for im_frame in ImageSequence.Iterator(imSequence):
                encoderinfo = im.encoderinfo.copy()
                im_frame = _convert_mode(im_frame)
                if isinstance(duration, (list, tuple)):
                    encoderinfo["duration"] = duration[frame_count]
                frame_count += 1

                # To specify duration, add the time in milliseconds to getdata(),
                # e.g. getdata(im_frame, duration=1000)
                if not previous:
                    # global header
                    first_frame = getheader(im_frame, palette, encoderinfo)[0]
                    first_frame += getdata(im_frame, (0, 0), **encoderinfo)
                else:
                    if first_frame:
                        for s in first_frame:
                            fp.write(s)
                        first_frame = None

                    # delta frame
                    delta = ImageChops.subtract_modulo(im_frame, previous.copy())
                    bbox = delta.getbbox()

                    if bbox:
                        # compress difference
                        encoderinfo['include_color_table'] = True
                        for s in getdata(im_frame.crop(bbox),
                                         bbox[:2], **encoderinfo):
                            fp.write(s)
                    else:
                        # FIXME: what should we do in this case?
                        pass
                previous = im_frame
        if first_frame:
            save_all = False
    if not save_all:
        header = getheader(im_out, palette, im.encoderinfo)[0]
        for s in header:
            fp.write(s)

        flags = 0

        if get_interlace(im):
            flags = flags | 64

        # local image header
        _get_local_header(fp, im, (0, 0), flags)

        im_out.encoderconfig = (8, get_interlace(im))
        ImageFile._save(im_out, fp, [("gif", (0, 0)+im.size, 0,
                                      RAWMODE[im_out.mode])])

        fp.write(b"\0")  # end of image data

    fp.write(b";")  # end of file

    if hasattr(fp, "flush"):
        fp.flush()


def get_interlace(im):
    try:
        interlace = im.encoderinfo["interlace"]
    except KeyError:
        interlace = 1

    # workaround for @PIL153
    if min(im.size) < 16:
        interlace = 0

    return interlace


def _get_local_header(fp, im, offset, flags):
    transparent_color_exists = False
    try:
        transparency = im.encoderinfo["transparency"]
    except KeyError:
        pass
    else:
        transparency = int(transparency)
        # optimize the block away if transparent color is not used
        transparent_color_exists = True

        used_palette_colors = _get_optimize(im, im.encoderinfo)
        if used_palette_colors is not None:
            # adjust the transparency index after optimize
            for i, palette_color in enumerate(used_palette_colors):
                if palette_color == transparency:
                    transparency = i
                    transparent_color_exists = True
                    break
                else:
                    transparent_color_exists = False

    if "duration" in im.encoderinfo:
        duration = int(im.encoderinfo["duration"] / 10)
    else:
        duration = 0
    if transparent_color_exists or duration != 0:
        transparency_flag = 1 if transparent_color_exists else 0
        if not transparent_color_exists:
            transparency = 0

        fp.write(b"!" +
                 o8(249) +                # extension intro
                 o8(4) +                  # length
                 o8(transparency_flag) +  # packed fields
                 o16(duration) +          # duration
                 o8(transparency) +       # transparency index
                 o8(0))

    if "comment" in im.encoderinfo and 1 <= len(im.encoderinfo["comment"]) <= 255:
        fp.write(b"!" +
                 o8(254) +                # extension intro
                 o8(len(im.encoderinfo["comment"])) +
                 im.encoderinfo["comment"] +
                 o8(0))
    if "loop" in im.encoderinfo:
        number_of_loops = im.encoderinfo["loop"]
        fp.write(b"!" +
                 o8(255) +                # extension intro
                 o8(11) +
                 b"NETSCAPE2.0" +
                 o8(3) +
                 o8(1) +
                 o16(number_of_loops) +   # number of loops
                 o8(0))
    include_color_table = im.encoderinfo.get('include_color_table')
    if include_color_table:
        try:
            palette = im.encoderinfo["palette"]
        except KeyError:
            palette = None
        palette_bytes = _get_palette_bytes(im, palette, im.encoderinfo)[0]
        color_table_size = _get_color_table_size(palette_bytes)
        if color_table_size:
            flags = flags | 128               # local color table flag
            flags = flags | color_table_size

    fp.write(b"," +
             o16(offset[0]) +             # offset
             o16(offset[1]) +
             o16(im.size[0]) +            # size
             o16(im.size[1]) +
             o8(flags))                   # flags
    if include_color_table and color_table_size:
        fp.write(_get_header_palette(palette_bytes))
    fp.write(o8(8))                       # bits


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
    except OSError:
        pass


# --------------------------------------------------------------------
# GIF utilities

# Force optimization so that we can test performance against
# cases where it took lots of memory and time previously.
_FORCE_OPTIMIZE = False

def _get_optimize(im, info):
    if im.mode in ("P", "L") and info and info.get("optimize", 0):
        # Potentially expensive operation.

        # The palette saves 3 bytes per color not used, but palette
        # lengths are restricted to 3*(2**N) bytes. Max saving would
        # be 768 -> 6 bytes if we went all the way down to 2 colors.
        # * If we're over 128 colors, we can't save any space.
        # * If there aren't any holes, it's not worth collapsing.
        # * If we have a 'large' image, the palette is in the noise.

        # create the new palette if not every color is used
        used_palette_colors = _get_used_palette_colors(im)
        if _FORCE_OPTIMIZE or im.mode == 'L' or \
           (len(used_palette_colors) <= 128 and
            max(used_palette_colors) > len(used_palette_colors) and
            im.width * im.height < 512 * 512):
            return used_palette_colors

def _get_used_palette_colors(im):
    used_palette_colors = []

    # check which colors are used
    i = 0
    for count in im.histogram():
        if count:
            used_palette_colors.append(i)
        i += 1

    return used_palette_colors

def _get_color_table_size(palette_bytes):
    # calculate the palette size for the header
    import math
    color_table_size = int(math.ceil(math.log(len(palette_bytes)//3, 2)))-1
    if color_table_size < 0:
        color_table_size = 0
    return color_table_size

def _get_header_palette(palette_bytes):
    color_table_size = _get_color_table_size(palette_bytes)

    # add the missing amount of bytes
    # the palette has to be 2<<n in size
    actual_target_size_diff = (2 << color_table_size) - len(palette_bytes)//3
    if actual_target_size_diff > 0:
        palette_bytes += o8(0) * 3 * actual_target_size_diff
    return palette_bytes

def _get_palette_bytes(im, palette, info):
    if im.mode == "P":
        if palette and isinstance(palette, bytes):
            source_palette = palette[:768]
        else:
            source_palette = im.im.getpalette("RGB")[:768]
    else:  # L-mode
        if palette and isinstance(palette, bytes):
            source_palette = palette[:768]
        else:
            source_palette = bytearray(i//3 for i in range(768))

    palette_bytes = None

    used_palette_colors = _get_optimize(im, info)
    if used_palette_colors is not None:
        palette_bytes = b""
        new_positions = [0]*256

        # pick only the used colors from the palette
        for i, oldPosition in enumerate(used_palette_colors):
            palette_bytes += source_palette[oldPosition*3:oldPosition*3+3]
            new_positions[oldPosition] = i

        # replace the palette color id of all pixel with the new id

        # Palette images are [0..255], mapped through a 1 or 3
        # byte/color map.  We need to remap the whole image
        # from palette 1 to palette 2. New_positions is
        # an array of indexes into palette 1.  Palette 2 is
        # palette 1 with any holes removed.

        # We're going to leverage the convert mechanism to use the
        # C code to remap the image from palette 1 to palette 2,
        # by forcing the source image into 'L' mode and adding a
        # mapping 'L' mode palette, then converting back to 'L'
        # sans palette thus converting the image bytes, then
        # assigning the optimized RGB palette.

        # perf reference, 9500x4000 gif, w/~135 colors
        # 14 sec prepatch, 1 sec postpatch with optimization forced.

        mapping_palette = bytearray(new_positions)

        m_im = im.copy()
        m_im.mode = 'P'

        m_im.palette = ImagePalette.ImagePalette("RGB",
                                               palette=mapping_palette*3,
                                               size=768)
        #possibly set palette dirty, then
        #m_im.putpalette(mapping_palette, 'L')  # converts to 'P'
        # or just force it.
        # UNDONE -- this is part of the general issue with palettes
        m_im.im.putpalette(*m_im.palette.getdata())

        m_im = m_im.convert('L')

        # Internally, we require 768 bytes for a palette.
        new_palette_bytes = (palette_bytes +
                             (768 - len(palette_bytes)) * b'\x00')
        m_im.putpalette(new_palette_bytes)
        m_im.palette = ImagePalette.ImagePalette("RGB",
                                               palette=palette_bytes,
                                               size=len(palette_bytes))

        # oh gawd, this is modifying the image in place so I can pass by ref.
        # REFACTOR SOONEST
        im.frombytes(m_im.tobytes())

    if not palette_bytes:
        palette_bytes = source_palette

    # returning palette, _not_ padded to 768 bytes like our internal ones.
    return palette_bytes, used_palette_colors

def getheader(im, palette=None, info=None):
    """Return a list of strings representing a GIF header"""

    # Header Block
    # http://www.matthewflickinger.com/lab/whatsinagif/bits_and_bytes.asp

    version = b"87a"
    for extensionKey in ["transparency", "duration", "loop", "comment"]:
        if info and extensionKey in info:
            if ((extensionKey == "duration" and info[extensionKey] == 0) or
                (extensionKey == "comment" and not (1 <= len(info[extensionKey]) <= 255))):
                continue
            version = b"89a"
            break
    else:
        if im.info.get("version") == b"89a":
            version = b"89a"

    header = [
        b"GIF"+version +        # signature + version
        o16(im.size[0]) +       # canvas width
        o16(im.size[1])         # canvas height
    ]

    palette_bytes, used_palette_colors = _get_palette_bytes(im, palette, info)

    # Logical Screen Descriptor
    color_table_size = _get_color_table_size(palette_bytes)
    # size of global color table + global color table flag
    header.append(o8(color_table_size + 128))  # packed fields
    # background + reserved/aspect
    if info and "background" in info:
        background = info["background"]
    elif "background" in im.info:
        # This elif is redundant within GifImagePlugin
        # since im.info parameters are bundled into the info dictionary
        # However, external scripts may call getheader directly
        # So this maintains earlier behaviour
        background = im.info["background"]
    else:
        background = 0
    header.append(o8(background) + o8(0))
    # end of Logical Screen Descriptor

    # Header + Logical Screen Descriptor + Global Color Table
    header.append(_get_header_palette(palette_bytes))
    return header, used_palette_colors


def getdata(im, offset=(0, 0), **params):
    """Return a list of strings representing this image.
       The first string is a local image header, the rest contains
       encoded image data."""

    class Collector(object):
        data = []

        def write(self, data):
            self.data.append(data)

    im.load()  # make sure raster data is available

    fp = Collector()

    try:
        im.encoderinfo = params

        # local image header
        _get_local_header(fp, im, offset, 0)

        ImageFile._save(im, fp, [("gif", (0, 0)+im.size, 0, RAWMODE[im.mode])])

        fp.write(b"\0")  # end of image data

    finally:
        del im.encoderinfo

    return fp.data


# --------------------------------------------------------------------
# Registry

Image.register_open(GifImageFile.format, GifImageFile, _accept)
Image.register_save(GifImageFile.format, _save)
Image.register_save_all(GifImageFile.format, _save_all)
Image.register_extension(GifImageFile.format, ".gif")
Image.register_mime(GifImageFile.format, "image/gif")

#
# Uncomment the following line if you wish to use NETPBM/PBMPLUS
# instead of the built-in "uncompressed" GIF encoder

# Image.register_save(GifImageFile.format, _save_netpbm)
