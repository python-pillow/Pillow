from tester import *

from PIL import Image

im = lena().resize((128, 100))

def test_toarray():
    def test(mode):
        ai = im.convert(mode).__array_interface__
        return ai["shape"], ai["typestr"], len(ai["data"])
    # assert_equal(test("1"), ((100, 128), '|b1', 1600))
    assert_equal(test("L"), ((100, 128), '|u1', 12800))
    assert_equal(test("I"), ((100, 128), Image._ENDIAN + 'i4', 51200)) # FIXME: wrong?
    assert_equal(test("F"), ((100, 128), Image._ENDIAN + 'f4', 51200)) # FIXME: wrong?
    assert_equal(test("RGB"), ((100, 128, 3), '|u1', 38400))
    assert_equal(test("RGBA"), ((100, 128, 4), '|u1', 51200))
    assert_equal(test("RGBX"), ((100, 128, 4), '|u1', 51200))

def test_fromarray():
    def test(mode):
        i = im.convert(mode)
        a = i.__array_interface__
        a["strides"] = 1 # pretend it's non-contigous
        i.__array_interface__ = a # patch in new version of attribute
        out = Image.fromarray(i)
        return out.mode, out.size, list(i.getdata()) == list(out.getdata())
    # assert_equal(test("1"), ("1", (128, 100), True))
    assert_equal(test("L"), ("L", (128, 100), True))
    assert_equal(test("I"), ("I", (128, 100), True))
    assert_equal(test("F"), ("F", (128, 100), True))
    assert_equal(test("RGB"), ("RGB", (128, 100), True))
    assert_equal(test("RGBA"), ("RGBA", (128, 100), True))
    assert_equal(test("RGBX"), ("RGBA", (128, 100), True))
