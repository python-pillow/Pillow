from PIL import Image

from .helper import hopper


def test_palette():
    def palette(mode):
        p = hopper(mode).getpalette()
        if p:
            return p[:10]
        return None

    assert palette("1") is None
    assert palette("L") is None
    assert palette("I") is None
    assert palette("F") is None
    assert palette("P") == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert palette("RGB") is None
    assert palette("RGBA") is None
    assert palette("CMYK") is None
    assert palette("YCbCr") is None


def test_palette_rawmode():
    im = Image.new("P", (1, 1))
    im.putpalette((1, 2, 3))

    rgb = im.getpalette("RGB")
    assert len(rgb) == 256 * 3
    assert rgb[:3] == [1, 2, 3]

    # Convert the RGB palette to RGBA
    rgba = im.getpalette("RGBA")
    assert len(rgba) == 256 * 4
    assert rgba[:4] == [1, 2, 3, 255]

    im.putpalette((1, 2, 3, 4), "RGBA")

    # Convert the RGBA palette to RGB
    rgb = im.getpalette("RGB")
    assert len(rgb) == 256 * 3
    assert rgb[:3] == [1, 2, 3]

    rgba = im.getpalette("RGBA")
    assert len(rgba) == 256 * 4
    assert rgba[:4] == [1, 2, 3, 4]
