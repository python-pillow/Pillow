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

# see https://github.com/python-imaging/Pillow/issues/279
def test_g4_fillorder_eq_png():
    """ Checking that we're actually getting the data that we expect"""
    png = Image.open('Tests/images/g4-fillorder-test.png')
    g4 = Image.open('Tests/images/g4-fillorder-test.tif')

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

    assert_equal(reread.info['compression'], orig.info['compression'])
    
    assert_false(orig.tobytes() == reread.tobytes())

def test_adobe_deflate_tiff():
    file = "Tests/images/tiff_adobe_deflate.tif"
    im = Image.open(file)

    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (278, 374))
    assert_equal(im.tile[0][:3], ('tiff_adobe_deflate', (0, 0, 278, 374), 0))
    assert_no_exception(lambda: im.load())


def test_write_metadata():
    """ Test metadata writing through libtiff """
    img = Image.open('Tests/images/lena_g4.tif')
    f = tempfile('temp.tiff')
    img.save(f, tiffinfo = img.tag)

    loaded = Image.open(f)

    original = img.tag.named()
    reloaded = loaded.tag.named()

    ignored = ['StripByteCounts', 'RowsPerStrip', 'PageNumber']
    
    for tag, value in reloaded.items():
        if tag not in ignored:
            assert_equal(original[tag], value, "%s didn't roundtrip" % tag)

    for tag, value in original.items():
        if tag not in ignored: 
            assert_equal(value, reloaded[tag], "%s didn't roundtrip" % tag)


def test_little_endian():
    im = Image.open('Tests/images/12bit.deflate.tif')
    assert_equal(im.getpixel((0,0)), 480)
    assert_equal(im.mode, 'I;16')

    b = im.tobytes()
    # Bytes are in image native order (little endian)
    if py3:
        assert_equal(b[0], ord(b'\xe0'))
        assert_equal(b[1], ord(b'\x01'))
    else:
        assert_equal(b[0], b'\xe0')
        assert_equal(b[1], b'\x01')
        

    out = tempfile("temp.tif")
    out = "temp.le.tif"
    im.save(out)
    reread = Image.open(out)

    assert_equal(reread.info['compression'], im.info['compression'])
    assert_equal(reread.getpixel((0,0)), 480)
    # UNDONE - libtiff defaults to writing in native endian, so
    # on big endian, we'll get back mode = 'I;16B' here. 
    
def test_big_endian():
    im = Image.open('Tests/images/12bit.MM.deflate.tif')

    assert_equal(im.getpixel((0,0)), 480)
    assert_equal(im.mode, 'I;16B')

    b = im.tobytes()

    # Bytes are in image native order (big endian)
    if py3:
        assert_equal(b[0], ord(b'\x01'))
        assert_equal(b[1], ord(b'\xe0'))
    else:
        assert_equal(b[0], b'\x01')
        assert_equal(b[1], b'\xe0')
    
    out = tempfile("temp.tif")
    im.save(out)
    reread = Image.open(out)

    assert_equal(reread.info['compression'], im.info['compression'])
    assert_equal(reread.getpixel((0,0)), 480)

def test_g4_string_info():
    """Tests String data in info directory"""
    file = "Tests/images/lena_g4_500.tif"
    orig = Image.open(file)
    
    out = tempfile("temp.tif")

    orig.tag[269] = 'temp.tif'
    orig.save(out)
             
    reread = Image.open(out)
    assert_equal('temp.tif', reread.tag[269])


