from PIL import Image

from .helper import hopper


def test_sanity():
    data = hopper().getdata()

    len(data)
    list(data)

    assert data[0] == (20, 20, 70)


def test_roundtrip():
    def getdata(mode):
        im = hopper(mode).resize((32, 30), Image.NEAREST)
        data = im.getdata()
        return data[0], len(data), len(list(data))

    assert getdata("1") == (0, 960, 960)
    assert getdata("L") == (17, 960, 960)
    assert getdata("I") == (17, 960, 960)
    assert getdata("F") == (17.0, 960, 960)
    assert getdata("RGB") == ((11, 13, 52), 960, 960)
    assert getdata("RGBA") == ((11, 13, 52, 255), 960, 960)
    assert getdata("CMYK") == ((244, 242, 203, 0), 960, 960)
    assert getdata("YCbCr") == ((16, 147, 123), 960, 960)
