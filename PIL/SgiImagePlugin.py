#
# The Python Imaging Library.
# $Id$
#
# SGI image file handling
#
# See "The SGI Image File Format (Draft version 0.97)", Paul Haeberli.
# <ftp://ftp.sgi.com/graphics/SGIIMAGESPEC>
#
#
# History:
# 2016-16-10 mb   Add save method without compression
# 1995-09-10 fl   Created
#
# Copyright (c) 2016 by Mickael Bonfill.
# Copyright (c) 2008 by Karsten Hiddemann.
# Copyright (c) 1997 by Secret Labs AB.
# Copyright (c) 1995 by Fredrik Lundh.
#
# See the README file for information on usage and redistribution.
#


from PIL import Image, ImageFile, _binary
import struct
import os

__version__ = "0.3"

i8 = _binary.i8
o8 = _binary.o8
i16 = _binary.i16be


def _accept(prefix):
    return len(prefix) >= 2 and i16(prefix) == 474


##
# Image plugin for SGI images.

class SgiImageFile(ImageFile.ImageFile):

    format = "SGI"
    format_description = "SGI Image File Format"

    def _open(self):

        # HEAD
        s = self.fp.read(512)
        if i16(s) != 474:
            raise ValueError("Not an SGI image file")

        # relevant header entries
        compression = i8(s[2])

        # bytes, dimension, zsize
        layout = i8(s[3]), i16(s[4:]), i16(s[10:])

        # determine mode from bytes/zsize
        if layout == (1, 2, 1) or layout == (1, 1, 1):
            self.mode = "L"
        elif layout == (1, 3, 3):
            self.mode = "RGB"
        elif layout == (1, 3, 4):
            self.mode = "RGBA"
        else:
            raise ValueError("Unsupported SGI image mode")

        # size
        self.size = i16(s[6:]), i16(s[8:])

        # decoder info
        if compression == 0:
            offset = 512
            pagesize = self.size[0]*self.size[1]*layout[0]
            self.tile = []
            for layer in self.mode:
                self.tile.append(
                    ("raw", (0, 0)+self.size, offset, (layer, 0, -1)))
                offset = offset + pagesize
        elif compression == 1:
            raise ValueError("SGI RLE encoding not supported")


def _save(im, fp, filename):
    if im.mode != "RGB" and im.mode != "RGBA" and im.mode != "L":
        raise ValueError("Unsupported SGI image mode")

    # Flip the image, since the origin of SGI file is the bottom-left corner
    im = im.transpose(Image.FLIP_TOP_BOTTOM)
    # Define the file as SGI File Format
    magicNumber = 474
    # Run-Length Encoding Compression - Unsupported at this time
    rle = 0
    # Byte-per-pixel precision, 1 = 8bits per pixel
    bpc = 1
    # Number of dimensions (x,y,z)
    dim = 3
    # X Dimension = width / Y Dimension = height
    x, y = im.size
    if im.mode == "L" and y == 1:
        dim = 1
    elif im.mode == "L":
        dim = 2
    # Z Dimension: Number of channels
    z = len(im.mode)
    if dim == 1 or dim == 2:
        z = 1
    # Minimum Byte value
    pinmin = 0
    # Maximum Byte value (255 = 8bits per pixel)
    pinmax = 255
    # Image name (79 characters max, truncated below in write)
    imgName = os.path.splitext(os.path.basename(filename))[0]
    if str is not bytes:
        imgName = imgName.encode('ascii', 'ignore')
    # Standard representation of pixel in the file
    colormap = 0
    fp.write(struct.pack('>h', magicNumber))
    fp.write(o8(rle))
    fp.write(o8(bpc))
    fp.write(struct.pack('>H', dim))
    fp.write(struct.pack('>H', x))
    fp.write(struct.pack('>H', y))
    fp.write(struct.pack('>H', z))
    fp.write(struct.pack('>l', pinmin))
    fp.write(struct.pack('>l', pinmax))

    fp.write(struct.pack('4s', b'')) # dummy
    fp.write(struct.pack('79s', imgName)) # truncates to 79 chars
    fp.write(struct.pack('s', b'')) # force null byte after imgname
    fp.write(struct.pack('>l', colormap))

    fp.write(struct.pack('404s', b'')) # dummy

    #assert we've got the right number of bands. 
    if len(im.getbands()) != z:
        raise ValueError("incorrect number of bands in SGI write: %s vs %s" %
                         (z, len(im.getbands())))

    for channel in im.split():
        fp.write(channel.tobytes())

    fp.close()


#
# registry

Image.register_open(SgiImageFile.format, SgiImageFile, _accept)
Image.register_save(SgiImageFile.format, _save)
Image.register_mime(SgiImageFile.format, "image/sgi")
Image.register_mime(SgiImageFile.format, "image/rgb")
Image.register_extension(SgiImageFile.format, ".bw")
Image.register_extension(SgiImageFile.format, ".rgb")
Image.register_extension(SgiImageFile.format, ".rgba")
Image.register_extension(SgiImageFile.format, ".sgi")

# End of file
