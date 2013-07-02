from tester import *

from PIL import Image

codecs = dir(Image.core)

if "group4_encoder" not in codecs or "group4_decoder" not in codecs:
    skip("tiff support not available")

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

    out = tempfile("temp.tif")
    rot = orig.transpose(Image.ROTATE_90)
    assert_equal(rot.size,(500,500))
    rot.save(out)

    reread = Image.open(out)
    assert_equal(reread.size,(500,500))
    _assert_noerr(reread)
    assert_image_equal(reread, rot)

    assert_false(orig.tobytes() == reread.tobytes())

def test_adobe_deflate_tiff():
    file = "Tests/images/tiff_adobe_deflate.tif"
    im = Image.open(file)

    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (278, 374))
    assert_equal(im.tile[0][:3], ('tiff_adobe_deflate', (0, 0, 278, 374), 0))
    assert_no_exception(lambda: im.load())
