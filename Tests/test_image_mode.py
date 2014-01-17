from tester import *

from PIL import Image

def test_sanity():

    im = lena()
    assert_no_exception(lambda: im.mode)

def test_properties():
    def check(mode, *result):
        signature = (
            Image.getmodebase(mode), Image.getmodetype(mode),
            Image.getmodebands(mode), Image.getmodebandnames(mode),
            )
        assert_equal(signature, result)
    check("1", "L", "L", 1, ("1",))
    check("L", "L", "L", 1, ("L",))
    check("P", "RGB", "L", 1, ("P",))
    check("I", "L", "I", 1, ("I",))
    check("F", "L", "F", 1, ("F",))
    check("RGB", "RGB", "L", 3, ("R", "G", "B"))
    check("RGBA", "RGB", "L", 4, ("R", "G", "B", "A"))
    check("RGBX", "RGB", "L", 4, ("R", "G", "B", "X"))
    check("RGBX", "RGB", "L", 4, ("R", "G", "B", "X"))
    check("CMYK", "RGB", "L", 4, ("C", "M", "Y", "K"))
    check("YCbCr", "RGB", "L", 3, ("Y", "Cb", "Cr"))
