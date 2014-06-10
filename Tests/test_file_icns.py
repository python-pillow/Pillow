from tester import *

from PIL import Image

# sample icon file
file = "Images/pillow.icns"
data = open(file, "rb").read()

enable_jpeg2k = hasattr(Image.core, 'jp2klib_version')

def test_sanity():
    # Loading this icon by default should result in the largest size
    # (512x512@2x) being loaded
    im = Image.open(file)
    im.load()
    assert_equal(im.mode, "RGBA")
    assert_equal(im.size, (1024, 1024))
    assert_equal(im.format, "ICNS")

def test_sizes():
    # Check that we can load all of the sizes, and that the final pixel
    # dimensions are as expected
    im = Image.open(file)
    for w,h,r in im.info['sizes']:
        wr = w * r
        hr = h * r
        im2 = Image.open(file)
        im2.size = (w, h, r)
        im2.load()
        assert_equal(im2.mode, 'RGBA')
        assert_equal(im2.size, (wr, hr))

def test_older_icon():
    # This icon was made with Icon Composer rather than iconutil; it still
    # uses PNG rather than JP2, however (since it was made on 10.9).
    im = Image.open('Tests/images/pillow2.icns')
    for w,h,r in im.info['sizes']:
        wr = w * r
        hr = h * r
        im2 = Image.open('Tests/images/pillow2.icns')
        im2.size = (w, h, r)
        im2.load()
        assert_equal(im2.mode, 'RGBA')
        assert_equal(im2.size, (wr, hr))

def test_jp2_icon():
    # This icon was made by using Uli Kusterer's oldiconutil to replace
    # the PNG images with JPEG 2000 ones.  The advantage of doing this is
    # that OS X 10.5 supports JPEG 2000 but not PNG; some commercial
    # software therefore does just this.
    
    # (oldiconutil is here: https://github.com/uliwitness/oldiconutil)

    if not enable_jpeg2k:
        return
    
    im = Image.open('Tests/images/pillow3.icns')
    for w,h,r in im.info['sizes']:
        wr = w * r
        hr = h * r
        im2 = Image.open('Tests/images/pillow3.icns')
        im2.size = (w, h, r)
        im2.load()
        assert_equal(im2.mode, 'RGBA')
        assert_equal(im2.size, (wr, hr))
    
