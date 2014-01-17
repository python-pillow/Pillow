from tester import *

from PIL import Image

def test_sanity():

    data = lena().getdata()

    assert_no_exception(lambda: len(data))
    assert_no_exception(lambda: list(data))

    assert_equal(data[0], (223, 162, 133))

def test_roundtrip():

    def getdata(mode):
        im = lena(mode).resize((32, 30))
        data = im.getdata()
        return data[0], len(data), len(list(data))

    assert_equal(getdata("1"), (255, 960, 960))
    assert_equal(getdata("L"), (176, 960, 960))
    assert_equal(getdata("I"), (176, 960, 960))
    assert_equal(getdata("F"), (176.0, 960, 960))
    assert_equal(getdata("RGB"), ((223, 162, 133), 960, 960))
    assert_equal(getdata("RGBA"), ((223, 162, 133, 255), 960, 960))
    assert_equal(getdata("CMYK"), ((32, 93, 122, 0), 960, 960))
    assert_equal(getdata("YCbCr"), ((176, 103, 160), 960, 960))
