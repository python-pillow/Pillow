import pytest
from PIL import Image

from .helper import hopper, is_big_endian, on_ci


@pytest.mark.xfail(is_big_endian() and on_ci(), reason="Fails on big-endian")
def test_extrema():
    def extrema(mode):
        return hopper(mode).getextrema()

    assert extrema("1") == (0, 255)
    assert extrema("L") == (1, 255)
    assert extrema("I") == (1, 255)
    assert extrema("F") == (1, 255)
    assert extrema("P") == (0, 225)  # fixed palette
    assert extrema("RGB") == ((0, 255), (0, 255), (0, 255))
    assert extrema("RGBA") == ((0, 255), (0, 255), (0, 255), (255, 255))
    assert extrema("CMYK") == ((0, 255), (0, 255), (0, 255), (0, 0))
    assert extrema("I;16") == (1, 255)


@pytest.mark.xfail(is_big_endian() and on_ci(), reason="Fails on big-endian")
def test_true_16():
    with Image.open("Tests/images/16_bit_noise.tif") as im:
        assert im.mode == "I;16"
        extrema = im.getextrema()
    assert extrema == (106, 285)
