from tester import *

from PIL import Image
from PIL import ImageOps
from PIL import ImageFilter

im = Image.open("Images/lena.ppm")

def test_ops_api():

    i = ImageOps.gaussian_blur(im, 2.0)
    assert_equal(i.mode, "RGB")
    assert_equal(i.size, (128, 128))
    # i.save("blur.bmp")

    i = ImageOps.usm(im, 2.0, 125, 8)
    assert_equal(i.mode, "RGB")
    assert_equal(i.size, (128, 128))
    # i.save("usm.bmp")

def test_filter_api():

    filter = ImageFilter.GaussianBlur(2.0)
    i = im.filter(filter)
    assert_equal(i.mode, "RGB")
    assert_equal(i.size, (128, 128))

    filter = ImageFilter.UnsharpMask(2.0, 125, 8)
    i = im.filter(filter)
    assert_equal(i.mode, "RGB")
    assert_equal(i.size, (128, 128))

def test_usm():

    usm = ImageOps.unsharp_mask
    assert_exception(ValueError, lambda: usm(im.convert("1")))
    assert_no_exception(lambda: usm(im.convert("L")))
    assert_exception(ValueError, lambda: usm(im.convert("I")))
    assert_exception(ValueError, lambda: usm(im.convert("F")))
    assert_no_exception(lambda: usm(im.convert("RGB")))
    assert_no_exception(lambda: usm(im.convert("RGBA")))
    assert_no_exception(lambda: usm(im.convert("CMYK")))
    assert_exception(ValueError, lambda: usm(im.convert("YCbCr")))

def test_blur():

    blur = ImageOps.gaussian_blur
    assert_exception(ValueError, lambda: blur(im.convert("1")))
    assert_no_exception(lambda: blur(im.convert("L")))
    assert_exception(ValueError, lambda: blur(im.convert("I")))
    assert_exception(ValueError, lambda: blur(im.convert("F")))
    assert_no_exception(lambda: blur(im.convert("RGB")))
    assert_no_exception(lambda: blur(im.convert("RGBA")))
    assert_no_exception(lambda: blur(im.convert("CMYK")))
    assert_exception(ValueError, lambda: blur(im.convert("YCbCr")))
