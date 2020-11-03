from PIL import Image

from .helper import hopper


def test_sanity():

    bbox = hopper().getbbox()
    assert isinstance(bbox, tuple)


def test_bbox():
    def check(im, fill_color):
        assert im.getbbox() is None

        im.paste(fill_color, (10, 25, 90, 75))
        assert im.getbbox() == (10, 25, 90, 75)

        im.paste(fill_color, (25, 10, 75, 90))
        assert im.getbbox() == (10, 10, 90, 90)

        im.paste(fill_color, (-10, -10, 110, 110))
        assert im.getbbox() == (0, 0, 100, 100)

    # 8-bit mode
    im = Image.new("L", (100, 100), 0)
    check(im, 255)

    # 32-bit mode
    im = Image.new("RGB", (100, 100), 0)
    check(im, 255)

    for mode in ("RGBA", "RGBa"):
        for color in ((0, 0, 0, 0), (127, 127, 127, 0), (255, 255, 255, 0)):
            im = Image.new(mode, (100, 100), color)
            check(im, (255, 255, 255, 255))

    for mode in ("La", "LA", "PA"):
        for color in ((0, 0), (127, 0), (255, 0)):
            im = Image.new(mode, (100, 100), color)
            check(im, (255, 255))
