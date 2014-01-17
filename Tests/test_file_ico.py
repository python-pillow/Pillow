from tester import *

from PIL import Image

# sample ppm stream
file = "Images/lena.ico"
data = open(file, "rb").read()

def test_sanity():
    im = Image.open(file)
    im.load()
    assert_equal(im.mode, "RGBA")
    assert_equal(im.size, (16, 16))
    assert_equal(im.format, "ICO")
