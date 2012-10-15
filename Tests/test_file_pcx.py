from tester import *

from PIL import Image

def test_sanity():

    file = tempfile("temp.pcx")

    lena("1").save(file)

    im = Image.open(file)
    im.load()
    assert_equal(im.mode, "1")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "PCX")

    lena("1").save(file)
    im = Image.open(file)

    lena("L").save(file)
    im = Image.open(file)

    lena("P").save(file)
    im = Image.open(file)

    lena("RGB").save(file)
    im = Image.open(file)

def test_pil184():
    # Check reading of files where xmin/xmax is not zero.

    file = "Tests/images/pil184.pcx"
    im = Image.open(file)

    assert_equal(im.size, (447, 144))
    assert_equal(im.tile[0][1], (0, 0, 447, 144))

    # Make sure all pixels are either 0 or 255.
    assert_equal(im.histogram()[0] + im.histogram()[255], 447*144)
