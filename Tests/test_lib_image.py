import pytest

from PIL import Image


def test_setmode():

    im = Image.new("L", (1, 1), 255)
    im.im.setmode("1")
    assert im.im.getpixel((0, 0)) == 255
    im.im.setmode("L")
    assert im.im.getpixel((0, 0)) == 255

    im = Image.new("1", (1, 1), 1)
    im.im.setmode("L")
    assert im.im.getpixel((0, 0)) == 255
    im.im.setmode("1")
    assert im.im.getpixel((0, 0)) == 255

    im = Image.new("RGB", (1, 1), (1, 2, 3))
    im.im.setmode("RGB")
    assert im.im.getpixel((0, 0)) == (1, 2, 3)
    im.im.setmode("RGBA")
    assert im.im.getpixel((0, 0)) == (1, 2, 3, 255)
    im.im.setmode("RGBX")
    assert im.im.getpixel((0, 0)) == (1, 2, 3, 255)
    im.im.setmode("RGB")
    assert im.im.getpixel((0, 0)) == (1, 2, 3)

    with pytest.raises(ValueError):
        im.im.setmode("L")
    with pytest.raises(ValueError):
        im.im.setmode("RGBABCDE")
