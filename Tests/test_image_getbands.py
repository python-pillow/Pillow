from tester import *

from PIL import Image

def test_getbands():

    assert_equal(Image.new("1", (1, 1)).getbands(), ("1",))
    assert_equal(Image.new("L", (1, 1)).getbands(), ("L",))
    assert_equal(Image.new("I", (1, 1)).getbands(), ("I",))
    assert_equal(Image.new("F", (1, 1)).getbands(), ("F",))
    assert_equal(Image.new("P", (1, 1)).getbands(), ("P",))
    assert_equal(Image.new("RGB", (1, 1)).getbands(), ("R", "G", "B"))
    assert_equal(Image.new("RGBA", (1, 1)).getbands(), ("R", "G", "B", "A"))
    assert_equal(Image.new("CMYK", (1, 1)).getbands(), ("C", "M", "Y", "K"))
    assert_equal(Image.new("YCbCr", (1, 1)).getbands(), ("Y", "Cb", "Cr"))
