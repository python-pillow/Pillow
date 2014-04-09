from tester import *

from PIL import Image


def _roundtrip(im):
    f = tempfile("temp.pcx")
    im.save(f)
    im2 = Image.open(f)

    assert_equal(im2.mode, im.mode)
    assert_equal(im2.size, im.size)
    assert_equal(im2.format, "PCX")
    assert_image_equal(im2, im)
    
def test_sanity():
    for mode in ('1', 'L', 'P', 'RGB'):
        _roundtrip(lena(mode))

def test_odd():
    # see issue #523, odd sized images should have a stride that's even.
    # not that imagemagick or gimp write pcx that way. 
    # we were not handling properly. 
    for mode in ('1', 'L', 'P', 'RGB'):
        # larger, odd sized images are better here to ensure that
        # we handle interrupted scan lines properly.
        _roundtrip(lena(mode).resize((511,511)))
        

def test_pil184():
    # Check reading of files where xmin/xmax is not zero.

    file = "Tests/images/pil184.pcx"
    im = Image.open(file)

    assert_equal(im.size, (447, 144))
    assert_equal(im.tile[0][1], (0, 0, 447, 144))

    # Make sure all pixels are either 0 or 255.
    assert_equal(im.histogram()[0] + im.histogram()[255], 447*144)
