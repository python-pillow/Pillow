from .helper import hopper


def test_getcolors():
    def getcolors(mode, limit=None):
        im = hopper(mode)
        if limit:
            colors = im.getcolors(limit)
        else:
            colors = im.getcolors()
        if colors:
            return len(colors)
        return None

    assert getcolors("1") == 2
    assert getcolors("L") == 255
    assert getcolors("I") == 255
    assert getcolors("F") == 255
    assert getcolors("P") == 90  # fixed palette
    assert getcolors("RGB") is None
    assert getcolors("RGBA") is None
    assert getcolors("CMYK") is None
    assert getcolors("YCbCr") is None

    assert getcolors("L", 128) is None
    assert getcolors("L", 1024) == 255

    assert getcolors("RGB", 8192) is None
    assert getcolors("RGB", 16384) == 10100
    assert getcolors("RGB", 100000) == 10100

    assert getcolors("RGBA", 16384) == 10100
    assert getcolors("CMYK", 16384) == 10100
    assert getcolors("YCbCr", 16384) == 9329


# --------------------------------------------------------------------


def test_pack():
    # Pack problems for small tables (@PIL209)

    im = hopper().quantize(3).convert("RGB")

    expected = [
        (4039, (172, 166, 181)),
        (4385, (124, 113, 134)),
        (7960, (31, 20, 33)),
    ]

    A = im.getcolors(maxcolors=2)
    assert A is None

    A = im.getcolors(maxcolors=3)
    A.sort()
    assert A == expected

    A = im.getcolors(maxcolors=4)
    A.sort()
    assert A == expected

    A = im.getcolors(maxcolors=8)
    A.sort()
    assert A == expected

    A = im.getcolors(maxcolors=16)
    A.sort()
    assert A == expected
