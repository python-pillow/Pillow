from tester import *

from PIL import Image

def test_sanity():

    file = "Images/lena.webp"
    im = Image.open(file)

    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "WEBP")


    file = tempfile("temp.webp")

    lena("RGB").save(file)

    im = Image.open(file)
    im.load()

    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "WEBP")



