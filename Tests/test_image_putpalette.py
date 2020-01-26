import pytest
from PIL import ImagePalette

from .helper import hopper


def test_putpalette():
    def palette(mode):
        im = hopper(mode).copy()
        im.putpalette(list(range(256)) * 3)
        p = im.getpalette()
        if p:
            return im.mode, p[:10]
        return im.mode

    with pytest.raises(ValueError):
        palette("1")
    for mode in ["L", "LA", "P", "PA"]:
        assert palette(mode) == (
            "PA" if "A" in mode else "P",
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        )
    with pytest.raises(ValueError):
        palette("I")
    with pytest.raises(ValueError):
        palette("F")
    with pytest.raises(ValueError):
        palette("RGB")
    with pytest.raises(ValueError):
        palette("RGBA")
    with pytest.raises(ValueError):
        palette("YCbCr")


def test_imagepalette():
    im = hopper("P")
    im.putpalette(ImagePalette.negative())
    im.putpalette(ImagePalette.random())
    im.putpalette(ImagePalette.sepia())
    im.putpalette(ImagePalette.wedge())
