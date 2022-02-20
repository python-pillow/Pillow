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

    for rawmode in ("RGB", None):
        rgb = im.getpalette(rawmode)
        assert rgb == [1, 2, 3]

    # Convert the RGB palette to RGBA
    rgba = im.getpalette("RGBA")
    assert rgba == [1, 2, 3, 255]

    im.putpalette((1, 2, 3, 4), "RGBA")

    # Convert the RGBA palette to RGB
    rgb = im.getpalette("RGB")
    assert rgb == [1, 2, 3]

    for rawmode in ("RGBA", None):
        rgba = im.getpalette(rawmode)
        assert rgba == [1, 2, 3, 4]
