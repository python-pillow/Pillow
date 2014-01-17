from tester import *

from PIL import Image

def test_sanity():

    def convert(im, mode):
        out = im.convert(mode)
        assert_equal(out.mode, mode)
        assert_equal(out.size, im.size)

    modes = "1", "L", "I", "F", "RGB", "RGBA", "RGBX", "CMYK", "YCbCr"

    for mode in modes:
        im = lena(mode)
        for mode in modes:
            yield_test(convert, im, mode)

def test_default():

    im = lena("P")
    assert_image(im, "P", im.size)
    im = im.convert()
    assert_image(im, "RGB", im.size)
    im = im.convert()
    assert_image(im, "RGB", im.size)



# ref https://github.com/python-imaging/Pillow/issues/274

def _test_float_conversion(im):
    orig = im.getpixel((5,5))
    converted = im.convert('F').getpixel((5,5))
    assert_equal(orig, converted)

def test_8bit():
    im = Image.open('Images/lena.jpg')
    _test_float_conversion(im.convert('L'))

def test_16bit():
    im = Image.open('Tests/images/16bit.cropped.tif')
    _test_float_conversion(im)

def test_16bit_workaround():
    im = Image.open('Tests/images/16bit.cropped.tif')
    _test_float_conversion(im.convert('I'))
    

    
