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

__version__ = "0.4"

from . import Image, ImageFile
import io


#
# --------------------------------------------------------------------

# object ids:
#  1. catalogue
#  2. pages
#  3. image
#  4. page
#  5. page contents

def _obj(fp, obj, **dict):
    fp.write(b"%d 0 obj\n" % obj)
    if dict:
        fp.write(b"<<\n")
        for k, v in dict.items():
            if v is not None:
                fp.write(b"/%s %s\n" % (k, v))
        fp.write(b">>\n")

def _endobj(fp):
    fp.write(b"endobj\n")

##
# (Internal) Image save plugin for the PDF format.

def _save(im, fp, filename):
    resolution = im.encoderinfo.get("resolution", 72.0)

    #
    # make sure image data is available
    im.load()

    xref = [0]*(5+1) # placeholders

    fp.write(b"%PDF-1.2\n")
    fp.write(b"% created by PIL PDF driver " + __version__ + "\n")

    #
    # Get image characteristics

    width, height = im.size

    # FIXME: Should replace ASCIIHexDecode with RunLengthDecode (packbits)
    # or LZWDecode (tiff/lzw compression).  Note that PDF 1.2 also supports
    # Flatedecode (zip compression).

    bits = 8
    params = None

    if im.mode == "1":
        filter = b"/ASCIIHexDecode"
        colorspace = b"/DeviceGray"
        procset = b"/ImageB" # grayscale
        bits = 1
    elif im.mode == "L":
        filter = b"/DCTDecode"
        # params = "<< /Predictor 15 /Columns %d >>" % (width-2)
        colorspace = b"/DeviceGray"
        procset = b"/ImageB" # grayscale
    elif im.mode == "P":
        filter = b"/ASCIIHexDecode"
        colorspace = b"[ /Indexed /DeviceRGB 255 <"
        palette = im.im.getpalette("RGB")
        for i in range(256):
            r = ord(palette[i*3])
            g = ord(palette[i*3+1])
            b = ord(palette[i*3+2])
            colorspace = colorspace + b"%02x%02x%02x " % (r, g, b)
        colorspace = colorspace + b"> ]"
        procset = b"/ImageI" # indexed color
    elif im.mode == "RGB":
        filter = b"/DCTDecode"
        colorspace = b"/DeviceRGB"
        procset = b"/ImageC" # color images
    elif im.mode == "CMYK":
        filter = b"/DCTDecode"
        colorspace = b"/DeviceCMYK"
        procset = b"/ImageC" # color images
    else:
        raise ValueError("cannot save mode %s" % im.mode)

    #
    # catalogue

    xref[1] = fp.tell()
    _obj(fp, 1, Type = b"/Catalog",
                Pages = b"2 0 R")
    _endobj(fp)

    #
    # pages

    xref[2] = fp.tell()
    _obj(fp, 2, Type = b"/Pages",
                Count = 1,
                Kids = b"[4 0 R]")
    _endobj(fp)

    #
    # image

    op = io.BytesIO()

    if filter == b"/ASCIIHexDecode":
        if bits == 1:
            # FIXME: the hex encoder doesn't support packed 1-bit
            # images; do things the hard way...
            data = im.tostring("raw", "1")
            im = Image.new("L", (len(data), 1), None)
            im.putdata(data)
        ImageFile._save(im, op, [("hex", (0,0)+im.size, 0, im.mode)])
    elif filter == b"/DCTDecode":
        ImageFile._save(im, op, [("jpeg", (0,0)+im.size, 0, im.mode)])
    elif filter == b"/FlateDecode":
        ImageFile._save(im, op, [("zip", (0,0)+im.size, 0, im.mode)])
    elif filter == b"/RunLengthDecode":
        ImageFile._save(im, op, [("packbits", (0,0)+im.size, 0, im.mode)])
    else:
        raise ValueError("unsupported PDF filter (%s)" % filter)

    xref[3] = fp.tell()
    _obj(fp, 3, Type = b"/XObject",
                Subtype = b"/Image",
                Width = width, # * 72.0 / resolution,
                Height = height, # * 72.0 / resolution,
                Length = len(op.getvalue()),
                Filter = filter,
                BitsPerComponent = bits,
                DecodeParams = params,
                ColorSpace = colorspace)

    fp.write(b"stream\n")
    fp.write(op.getvalue())
    fp.write(b"\nendstream\n")

    _endobj(fp)

    #
    # page

    xref[4] = fp.tell()
    _obj(fp, 4)
    fp.write(b"<<\n/Type /Page\n/Parent 2 0 R\n"\
             b"/Resources <<\n/ProcSet [ /PDF %s ]\n"\
             b"/XObject << /image 3 0 R >>\n>>\n"\
             b"/MediaBox [ 0 0 %d %d ]\n/Contents 5 0 R\n>>\n" %\
             (procset, int(width * 72.0 /resolution) , int(height * 72.0 / resolution)))
    _endobj(fp)

    #
    # page contents

    op = io.BytesIO()

    op.write(b"q %d 0 0 %d 0 0 cm /image Do Q\n" % (int(width * 72.0 / resolution), int(height * 72.0 / resolution)))

    xref[5] = fp.tell()
    _obj(fp, 5, Length = len(op.getvalue()))

    fp.write(b"stream\n")
    fp.write(op.getvalue())
    fp.write(b"\nendstream\n")

    _endobj(fp)

    #
    # trailer
    startxref = fp.tell()
    fp.write(b"xref\n0 %d\n0000000000 65535 f \n" % len(xref))
    for x in xref[1:]:
        fp.write(b"%010d 00000 n \n" % x)
    fp.write(b"trailer\n<<\n/Size %d\n/Root 1 0 R\n>>\n" % len(xref))
    fp.write(b"startxref\n%d\n%%%%EOF\n" % startxref)
    fp.flush()

#
# --------------------------------------------------------------------

Image.register_save("PDF", _save)

Image.register_extension("PDF", ".pdf")

Image.register_mime("PDF", "application/pdf")
