from tester import *

from PIL import Image
from PIL import ImageFile

codecs = dir(Image.core)

# save original block sizes
MAXBLOCK = ImageFile.MAXBLOCK
SAFEBLOCK = ImageFile.SAFEBLOCK

def test_parser():

    def roundtrip(format):

        im = lena("L").resize((1000, 1000))
        if format in ("MSP", "XBM"):
            im = im.convert("1")

        file = BytesIO()

        im.save(file, format)

        data = file.getvalue()

        parser = ImageFile.Parser()
        parser.feed(data)
        imOut = parser.close()

        return im, imOut

    assert_image_equal(*roundtrip("BMP"))
    assert_image_equal(*roundtrip("GIF"))
    assert_image_equal(*roundtrip("IM"))
    assert_image_equal(*roundtrip("MSP"))
    if "zip_encoder" in codecs:
        try:
            # force multiple blocks in PNG driver
            ImageFile.MAXBLOCK = 8192
            assert_image_equal(*roundtrip("PNG"))
        finally:
            ImageFile.MAXBLOCK = MAXBLOCK
    assert_image_equal(*roundtrip("PPM"))
    assert_image_equal(*roundtrip("TIFF"))
    assert_image_equal(*roundtrip("XBM"))
    assert_image_equal(*roundtrip("TGA"))
    assert_image_equal(*roundtrip("PCX"))

    im1, im2 = roundtrip("EPS")
    assert_image_similar(im1, im2.convert('L'),20) # EPS comes back in RGB      
    
    if "jpeg_encoder" in codecs:
        im1, im2 = roundtrip("JPEG") # lossy compression
        assert_image(im1, im2.mode, im2.size)

    # XXX Why assert exception and why does it fail?
    # https://github.com/python-imaging/Pillow/issues/78
    #assert_exception(IOError, lambda: roundtrip("PDF"))

def test_ico():
    with open('Tests/images/python.ico', 'rb') as f:
        data = f.read()
    p = ImageFile.Parser()
    p.feed(data)
    assert_equal((48,48), p.image.size)

def test_safeblock():

    im1 = lena()

    if "zip_encoder" not in codecs:
        skip("PNG (zlib) encoder not available")

    try:
        ImageFile.SAFEBLOCK = 1
        im2 = fromstring(tostring(im1, "PNG"))
    finally:
        ImageFile.SAFEBLOCK = SAFEBLOCK

    assert_image_equal(im1, im2)
