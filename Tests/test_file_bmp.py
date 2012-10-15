from tester import *

from PIL import Image

def test_sanity():

    file = tempfile("temp.bmp")

    lena().save(file)

    im = Image.open(file)
    im.load()
    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "BMP")

    lena("1").save(file)
    im = Image.open(file)

    lena("L").save(file)
    im = Image.open(file)

    lena("P").save(file)
    im = Image.open(file)

    lena("RGB").save(file)
    im = Image.open(file)
