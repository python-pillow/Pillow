import pytest

from PIL import Image, ImagePalette

from .helper import assert_image_equal, assert_image_equal_tofile, hopper


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
    assert_image_equal_tofile(im.convert("RGB"), "Tests/images/palette_negative.png")

    im.putpalette(ImagePalette.random())

    im.putpalette(ImagePalette.sepia())
    assert_image_equal_tofile(im.convert("RGB"), "Tests/images/palette_sepia.png")

    im.putpalette(ImagePalette.wedge())
    assert_image_equal_tofile(im.convert("RGB"), "Tests/images/palette_wedge.png")


def test_putpalette_with_alpha_values():
    with Image.open("Tests/images/transparent.gif") as im:
        expected = im.convert("RGBA")

        palette = im.getpalette()
        transparency = im.info.pop("transparency")

        palette_with_alpha_values = []
        for i in range(256):
            color = palette[i * 3 : i * 3 + 3]
            alpha = 0 if i == transparency else 255
            palette_with_alpha_values += color + [alpha]
        im.putpalette(palette_with_alpha_values, "RGBA")

        assert_image_equal(im.convert("RGBA"), expected)
