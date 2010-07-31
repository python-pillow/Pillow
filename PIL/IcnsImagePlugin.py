#
# The Python Imaging Library.
# $Id$
#
# Mac OS X icns file decoder, based on icns.py by Bob Ippolito.
#
# history:
# 2004-10-09 fl   Turned into a PIL plugin; removed 2.3 dependencies.
#
# Copyright (c) 2004 by Bob Ippolito.
# Copyright (c) 2004 by Secret Labs.
# Copyright (c) 2004 by Fredrik Lundh.
#
# See the README file for information on usage and redistribution.
#

import Image, ImageFile
import string, struct

HEADERSIZE = 8

def nextheader(fobj):
    return struct.unpack('>4sI', fobj.read(HEADERSIZE))

def read_32t(fobj, (start, length), (width, height)):
    # The 128x128 icon seems to have an extra header for some reason.
    fobj.seek(start)
    sig = fobj.read(4)
    if sig != '\x00\x00\x00\x00':
        raise SyntaxError, 'Unknown signature, expecting 0x00000000'
    return read_32(fobj, (start + 4, length - 4), (width, height))

def read_32(fobj, (start, length), size):
    """
    Read a 32bit RGB icon resource.  Seems to be either uncompressed or
    an RLE packbits-like scheme.
    """
    fobj.seek(start)
    sizesq = size[0] * size[1]
    if length == sizesq * 3:
        # uncompressed ("RGBRGBGB")
        indata = fobj.read(length)
        im = Image.frombuffer("RGB", size, indata, "raw", "RGB", 0, 1)
    else:
        # decode image
        im = Image.new("RGB", size, None)
        for band_ix in range(3):
            data = []
            bytesleft = sizesq
            while bytesleft > 0:
                byte = fobj.read(1)
                if not byte:
                    break
                byte = ord(byte)
                if byte & 0x80:
                    blocksize = byte - 125
                    byte = fobj.read(1)
                    for i in range(blocksize):
                        data.append(byte)
                else:
                    blocksize = byte + 1
                    data.append(fobj.read(blocksize))
                bytesleft = bytesleft - blocksize
                if bytesleft <= 0:
                    break
            if bytesleft != 0:
                raise SyntaxError(
                    "Error reading channel [%r left]" % bytesleft
                    )
            band = Image.frombuffer(
                "L", size, string.join(data, ""), "raw", "L", 0, 1
                )
            im.im.putband(band.im, band_ix)
    return {"RGB": im}

def read_mk(fobj, (start, length), size):
    # Alpha masks seem to be uncompressed
    fobj.seek(start)
    band = Image.frombuffer(
        "L", size, fobj.read(size[0]*size[1]), "raw", "L", 0, 1
        )
    return {"A": band}

class IcnsFile:

    SIZES = {
        (128, 128): [
            ('it32', read_32t),
            ('t8mk', read_mk),
        ],
        (48, 48): [
            ('ih32', read_32),
            ('h8mk', read_mk),
        ],
        (32, 32): [
            ('il32', read_32),
            ('l8mk', read_mk),
        ],
        (16, 16): [
            ('is32', read_32),
            ('s8mk', read_mk),
        ],
    }

    def __init__(self, fobj):
        """
        fobj is a file-like object as an icns resource
        """
        # signature : (start, length)
        self.dct = dct = {}
        self.fobj = fobj
        sig, filesize = nextheader(fobj)
        if sig != 'icns':
            raise SyntaxError, 'not an icns file'
        i = HEADERSIZE
        while i < filesize:
            sig, blocksize = nextheader(fobj)
            i = i + HEADERSIZE
            blocksize = blocksize - HEADERSIZE
            dct[sig] = (i, blocksize)
            fobj.seek(blocksize, 1)
            i = i + blocksize

    def itersizes(self):
        sizes = []
        for size, fmts in self.SIZES.items():
            for (fmt, reader) in fmts:
                if self.dct.has_key(fmt):
                    sizes.append(size)
                    break
        return sizes

    def bestsize(self):
        sizes = self.itersizes()
        if not sizes:
            raise SyntaxError, "No 32bit icon resources found"
        return max(sizes)

    def dataforsize(self, size):
        """
        Get an icon resource as {channel: array}.  Note that
        the arrays are bottom-up like windows bitmaps and will likely
        need to be flipped or transposed in some way.
        """
        dct = {}
        for code, reader in self.SIZES[size]:
            desc = self.dct.get(code)
            if desc is not None:
                dct.update(reader(self.fobj, desc, size))
        return dct

    def getimage(self, size=None):
        if size is None:
            size = self.bestsize()
        channels = self.dataforsize(size)
        im = channels.get("RGB").copy()
        try:
            im.putalpha(channels["A"])
        except KeyError:
            pass
        return im

##
# Image plugin for Mac OS icons.

class IcnsImageFile(ImageFile.ImageFile):
    """
    PIL read-only image support for Mac OS .icns files.
    Chooses the best resolution, but will possibly load
    a different size image if you mutate the size attribute
    before calling 'load'.

    The info dictionary has a key 'sizes' that is a list
    of sizes that the icns file has.
    """

    format = "ICNS"
    format_description = "Mac OS icns resource"

    def _open(self):
        self.icns = IcnsFile(self.fp)
        self.mode = 'RGBA'
        self.size = self.icns.bestsize()
        self.info['sizes'] = self.icns.itersizes()
        # Just use this to see if it's loaded or not yet.
        self.tile = ('',)

    def load(self):
        Image.Image.load(self)
        if not self.tile:
            return
        self.load_prepare()
        # This is likely NOT the best way to do it, but whatever.
        im = self.icns.getimage(self.size)
        self.im = im.im
        self.mode = im.mode
        self.size = im.size
        self.fp = None
        self.icns = None
        self.tile = ()
        self.load_end()


Image.register_open("ICNS", IcnsImageFile, lambda x: x[:4] == 'icns')
Image.register_extension("ICNS", '.icns')

if __name__ == '__main__':
    import os, sys
    im = Image.open(open(sys.argv[1], "rb"))
    im.save("out.png")
    os.startfile("out.png")
