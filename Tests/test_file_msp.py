from tester import *

from PIL import Image

def test_sanity():

    file = tempfile("temp.msp")

    lena("1").save(file)

    im = Image.open(file)
    im.load()
    assert_equal(im.mode, "1")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "MSP")
