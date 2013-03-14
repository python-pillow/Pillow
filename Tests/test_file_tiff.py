from tester import *

from PIL import Image

import random

def test_sanity():

    file = tempfile("temp.tif")

    lena("RGB").save(file)

    im = Image.open(file)
    im.load()
    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "TIFF")

    lena("1").save(file)
    im = Image.open(file)

    lena("L").save(file)
    im = Image.open(file)

    lena("P").save(file)
    im = Image.open(file)

    lena("RGB").save(file)
    im = Image.open(file)

    lena("I").save(file)
    im = Image.open(file)

def test_mac_tiff():
    # Read RGBa images from Mac OS X [@PIL136]

    file = "Tests/images/pil136.tiff"
    im = Image.open(file)

    assert_equal(im.mode, "RGBA")
    assert_equal(im.size, (55, 43))
    assert_equal(im.tile, [('raw', (0, 0, 55, 43), 8, ('RGBa', 0, 1))])
    assert_no_exception(lambda: im.load())

def test_gimp_tiff():
    # Read TIFF JPEG images from GIMP [@PIL168]

    file = "Tests/images/pil168.tif"
    im = Image.open(file)

    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (256, 256))
    assert_equal(im.tile, [
            ('jpeg', (0, 0, 256, 64), 8, ('RGB', '')),
            ('jpeg', (0, 64, 256, 128), 1215, ('RGB', '')),
            ('jpeg', (0, 128, 256, 192), 2550, ('RGB', '')),
            ('jpeg', (0, 192, 256, 256), 3890, ('RGB', '')),
            ])
    assert_no_exception(lambda: im.load())

def _assert_noerr(im):
    """Helper tests that assert basic sanity about the g4 tiff reading"""
    #1 bit
    assert_equal(im.mode, "1")

    # Does the data actually load
    assert_no_exception(lambda: im.load())
    assert_no_exception(lambda: im.getdata())

    try:
        assert_equal(im._compression, 'group4')
    except:
        print("No _compression")
        print (dir(im))

    # can we write it back out, in a different form. 
    out = tempfile("temp.png")
    assert_no_exception(lambda: im.save(out))

def test_g4_tiff():
    """Test the ordinary file path load path"""

    file = "Tests/images/lena_g4_500.tif"
    im = Image.open(file)

    assert_equal(im.size, (500,500))
    _assert_noerr(im)

def test_g4_large():
    file = "Tests/images/pport_g4.tif"
    im = Image.open(file)
    _assert_noerr(im)

def test_g4_tiff_file():
    """Testing the string load path"""

    file = "Tests/images/lena_g4_500.tif"
    with open(file,'rb') as f:
        im = Image.open(f)

        assert_equal(im.size, (500,500))
        _assert_noerr(im)

def test_g4_tiff_bytesio():
    """Testing the stringio loading code path"""
    from io import BytesIO
    file = "Tests/images/lena_g4_500.tif"
    s = BytesIO()
    with open(file,'rb') as f:
        s.write(f.read())
        s.seek(0)
    im = Image.open(s)

    assert_equal(im.size, (500,500))
    _assert_noerr(im)
    	
def test_g4_eq_png():
    """ Checking that we're actually getting the data that we expect"""
    png = Image.open('Tests/images/lena_bw_500.png')
    g4 = Image.open('Tests/images/lena_g4_500.tif')

    assert_image_equal(g4, png)

def test_g4_write():
    """Checking to see that the saved image is the same as what we wrote"""
    file = "Tests/images/lena_g4_500.tif"
    orig = Image.open(file)

    out = "temp.tif"
    rot = orig.transpose(Image.ROTATE_90)
    assert_equal(rot.size,(500,500))
    rot.save(out)

    reread = Image.open(out)
    assert_equal(reread.size,(500,500))
    _assert_noerr(reread)
    assert_image_equal(reread, rot)

    assert_false(orig.tobytes() == reread.tobytes())

