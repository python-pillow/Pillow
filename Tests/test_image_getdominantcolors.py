from .helper import hopper


def test_getdominantcolors():
    def getdominantcolors(mode):
        im = hopper(mode)
        colors = im.getdominantcolors()
        return len(colors)

    assert getdominantcolors("F") == 3
    assert getdominantcolors("I") == 3
    assert getdominantcolors("L") == 3
    assert getdominantcolors("P") == 3
    assert getdominantcolors("RGB") == 3
    assert getdominantcolors("YCbCr") == 3
    assert getdominantcolors("CMYK") == 3
    assert getdominantcolors("RGBA") == 3
    assert getdominantcolors("HSV") == 3
