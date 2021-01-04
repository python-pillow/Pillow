import pytest

from PIL import CurImagePlugin, Image

TEST_FILE = "Tests/images/deerstalker.cur"


def test_sanity():
    with Image.open(TEST_FILE) as im:
        assert im.size == (32, 32)
        assert isinstance(im, CurImagePlugin.CurImageFile)
        # Check some pixel colors to ensure image is loaded properly
        assert im.getpixel((10, 1)) == (0, 0, 0, 0)
        assert im.getpixel((11, 1)) == (253, 254, 254, 1)
        assert im.getpixel((16, 16)) == (84, 87, 86, 255)


def test_invalid_file():
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        CurImagePlugin.CurImageFile(invalid_file)

    no_cursors_file = "Tests/images/no_cursors.cur"

    cur = CurImagePlugin.CurImageFile(TEST_FILE)
    cur.fp.close()
    with open(no_cursors_file, "rb") as cur.fp:
        with pytest.raises(TypeError):
            cur._open()
