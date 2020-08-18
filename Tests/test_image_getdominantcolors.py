from .helper import hopper


def test_getdominantcolors():
    def getdominantcolors(mode, numcolors=None):
        im = hopper(mode)

        if numcolors:
            colors = im.getdominantcolors(numcolors)
        else:
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
