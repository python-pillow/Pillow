#
# The Python Imaging Library.
# $Id$
#
# PDF (Acrobat) file handling
#
# History:
# 1996-07-16 fl   Created
# 1997-01-18 fl   Fixed header
# 2004-02-21 fl   Fixes for 1/L/CMYK images, etc.
# 2004-02-24 fl   Fixes for 1 and P images.
#
# Copyright (c) 1997-2004 by Secret Labs AB.  All rights reserved.
# Copyright (c) 1996-1997 by Fredrik Lundh.
#
# See the README file for information on usage and redistribution.
#

##
# Image plugin for PDF images (output only).
##

from . import Image, ImageFile
from ._binary import i8
import io

__version__ = "0.4"


#
# --------------------------------------------------------------------

# object ids:
#  1. catalogue
#  2. pages
#  3. image
#  4. page
#  5. page contents

def _obj(fp, obj, **dict):
    fp.write("%d 0 obj\n" % obj)
    if dict:
        fp.write("<<\n")
        for k, v in dict.items():
            if v is not None:
                fp.write("/%s %s\n" % (k, v))
        fp.write(">>\n")


def _endobj(fp):
    fp.write("endobj\n")


def _save_all(im, fp, filename):
    _save(im, fp, filename, save_all=True)


##
# (Internal) Image save plugin for the PDF format.

def _save(im, fp, filename, save_all=False):
    resolution = im.encoderinfo.get("resolution", 72.0)

    #
    # make sure image data is available
    im.load()

    xref = [0]

    class TextWriter(object):
        def __init__(self, fp):
            self.fp = fp

        def __getattr__(self, name):
            return getattr(self.fp, name)

        def write(self, value):
            self.fp.write(value.encode('latin-1'))

    fp = TextWriter(fp)

    fp.write("%PDF-1.2\n")
    fp.write("% created by PIL PDF driver " + __version__ + "\n")

    # FIXME: Should replace ASCIIHexDecode with RunLengthDecode (packbits)
    # or LZWDecode (tiff/lzw compression).  Note that PDF 1.2 also supports
    # Flatedecode (zip compression).

    bits = 8
    params = None

    if im.mode == "1":
        filter = "/ASCIIHexDecode"
        colorspace = "/DeviceGray"
        procset = "/ImageB"  # grayscale
        bits = 1
    elif im.mode == "L":
        filter = "/DCTDecode"
        # params = "<< /Predictor 15 /Columns %d >>" % (width-2)
        colorspace = "/DeviceGray"
        procset = "/ImageB"  # grayscale
    elif im.mode == "P":
        filter = "/ASCIIHexDecode"
        colorspace = "[ /Indexed /DeviceRGB 255 <"
        palette = im.im.getpalette("RGB")
        for i in range(256):
            r = i8(palette[i*3])
            g = i8(palette[i*3+1])
            b = i8(palette[i*3+2])
            colorspace += "%02x%02x%02x " % (r, g, b)
        colorspace += "> ]"
        procset = "/ImageI"  # indexed color
    elif im.mode == "RGB":
        filter = "/DCTDecode"
        colorspace = "/DeviceRGB"
        procset = "/ImageC"  # color images
    elif im.mode == "CMYK":
        filter = "/DCTDecode"
        colorspace = "/DeviceCMYK"
        procset = "/ImageC"  # color images
    else:
        raise ValueError("cannot save mode %s" % im.mode)

    #
    # catalogue

    xref.append(fp.tell())
    _obj(
        fp, 1,
        Type="/Catalog",
        Pages="2 0 R")
    _endobj(fp)

    #
    # pages
    numberOfPages = 1
    if save_all:
        try:
            numberOfPages = im.n_frames
        except AttributeError:
            # Image format does not have n_frames. It is a single frame image
            pass
    pages = [str(pageNumber*3+4)+" 0 R"
             for pageNumber in range(0, numberOfPages)]

    xref.append(fp.tell())
    _obj(
        fp, 2,
        Type="/Pages",
        Count=len(pages),
        Kids="["+"\n".join(pages)+"]")
    _endobj(fp)

    for pageNumber in range(0, numberOfPages):
        im.seek(pageNumber)

        #
        # image

        op = io.BytesIO()

        if filter == "/ASCIIHexDecode":
            if bits == 1:
                # FIXME: the hex encoder doesn't support packed 1-bit
                # images; do things the hard way...
                data = im.tobytes("raw", "1")
                im = Image.new("L", (len(data), 1), None)
                im.putdata(data)
            ImageFile._save(im, op, [("hex", (0, 0)+im.size, 0, im.mode)])
        elif filter == "/DCTDecode":
            Image.SAVE["JPEG"](im, op, filename)
        elif filter == "/FlateDecode":
            ImageFile._save(im, op, [("zip", (0, 0)+im.size, 0, im.mode)])
        elif filter == "/RunLengthDecode":
            ImageFile._save(im, op, [("packbits", (0, 0)+im.size, 0, im.mode)])
        else:
            raise ValueError("unsupported PDF filter (%s)" % filter)

        #
        # Get image characteristics

        width, height = im.size

        xref.append(fp.tell())
        _obj(
            fp, pageNumber*3+3,
            Type="/XObject",
            Subtype="/Image",
            Width=width,  # * 72.0 / resolution,
            Height=height,  # * 72.0 / resolution,
            Length=len(op.getvalue()),
            Filter=filter,
            BitsPerComponent=bits,
            DecodeParams=params,
            ColorSpace=colorspace)

        fp.write("stream\n")
        fp.fp.write(op.getvalue())
        fp.write("\nendstream\n")

        _endobj(fp)

        #
        # page

        xref.append(fp.tell())
        _obj(fp, pageNumber*3+4)
        fp.write(
            "<<\n/Type /Page\n/Parent 2 0 R\n"
            "/Resources <<\n/ProcSet [ /PDF %s ]\n"
            "/XObject << /image %d 0 R >>\n>>\n"
            "/MediaBox [ 0 0 %d %d ]\n/Contents %d 0 R\n>>\n" % (
                procset,
                pageNumber*3+3,
                int(width * 72.0 / resolution),
                int(height * 72.0 / resolution),
                pageNumber*3+5))
        _endobj(fp)

        #
        # page contents

        op = TextWriter(io.BytesIO())

        op.write(
            "q %d 0 0 %d 0 0 cm /image Do Q\n" % (
                int(width * 72.0 / resolution),
                int(height * 72.0 / resolution)))

        xref.append(fp.tell())
        _obj(fp, pageNumber*3+5, Length=len(op.fp.getvalue()))

        fp.write("stream\n")
        fp.fp.write(op.fp.getvalue())
        fp.write("\nendstream\n")

        _endobj(fp)

    #
    # trailer
    startxref = fp.tell()
    fp.write("xref\n0 %d\n0000000000 65535 f \n" % len(xref))
    for x in xref[1:]:
        fp.write("%010d 00000 n \n" % x)
    fp.write("trailer\n<<\n/Size %d\n/Root 1 0 R\n>>\n" % len(xref))
    fp.write("startxref\n%d\n%%%%EOF\n" % startxref)
    if hasattr(fp, "flush"):
        fp.flush()

#
# --------------------------------------------------------------------

Image.register_save("PDF", _save)
Image.register_save_all("PDF", _save_all)

Image.register_extension("PDF", ".pdf")

Image.register_mime("PDF", "application/pdf")
