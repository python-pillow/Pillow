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
    
def test_rgba_p():
    im = lena('RGBA')
    im.putalpha(lena('L'))

    converted = im.convert('P')
    comparable = converted.convert('RGBA')

    assert_image_similar(im, comparable, 20)
               
def test_trns_p():    
    im = lena('P')
    im.info['transparency']=0

    f = tempfile('temp.png')

    l = im.convert('L')
    assert_equal(l.info['transparency'], 0) # undone
    assert_no_exception(lambda: l.save(f))


    rgb = im.convert('RGB')
    assert_equal(rgb.info['transparency'], (0,0,0)) # undone
    assert_no_exception(lambda: rgb.save(f))
    
def test_trns_l():
    im = lena('L')
    im.info['transparency'] = 128

    f = tempfile('temp.png')
    
    rgb = im.convert('RGB')
    assert_equal(rgb.info['transparency'], (128,128,128)) # undone
    assert_no_exception(lambda: rgb.save(f))

    p = im.convert('P')
    assert_true('transparency' in p.info)
    assert_no_exception(lambda: p.save(f))

    p = assert_warning(UserWarning,
                       lambda: im.convert('P', palette = Image.ADAPTIVE))
    assert_false('transparency' in p.info)
    assert_no_exception(lambda: p.save(f))

    
def test_trns_RGB():
    im = lena('RGB')
    im.info['transparency'] = im.getpixel((0,0))

    f = tempfile('temp.png')
        
    l = im.convert('L')
    assert_equal(l.info['transparency'], l.getpixel((0,0))) # undone
    assert_no_exception(lambda: l.save(f))

    p = im.convert('P')
    assert_true('transparency' in p.info)
    assert_no_exception(lambda: p.save(f))
    
    p = assert_warning(UserWarning,
                       lambda: im.convert('P', palette = Image.ADAPTIVE))
    assert_false('transparency' in p.info)
    assert_no_exception(lambda: p.save(f))


