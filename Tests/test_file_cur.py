import pytest

from PIL import CurImagePlugin, Image


def test_deerstalker():
    with Image.open("Tests/images/cur/deerstalker.cur") as im:
        assert im.size == (32, 32)
        assert isinstance(im, CurImagePlugin.CurImageFile)
        # Check some pixel colors to ensure image is loaded properly
        assert im.getpixel((10, 1)) == (0, 0, 0, 0)
        assert im.getpixel((11, 1)) == (253, 254, 254, 1)
        assert im.getpixel((16, 16)) == (84, 87, 86, 255)


def test_posy_link():
    with Image.open("Tests/images/cur/posy_link.cur") as im:
        assert im.size == (128, 128)
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((20, 20)) == (0, 0, 0, 255)
        assert im.getpixel((40, 40)) == (255, 255, 255, 255)


def test_invalid_file():
    invalid_file = "Tests/images/cur/posy_link.png"

    with pytest.raises(SyntaxError):
        CurImagePlugin.CurImageFile(invalid_file)

    no_cursors_file = "Tests/images/cur/no_cursors.cur"

    cur = CurImagePlugin.CurImageFile(TEST_FILE)
    cur.fp.close()
    with open(no_cursors_file, "rb") as cur.fp:
        with pytest.raises(TypeError):
            cur._open()
