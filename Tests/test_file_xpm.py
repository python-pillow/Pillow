from __future__ import annotations

from io import BytesIO

import pytest

from PIL import Image, XpmImagePlugin

from .helper import assert_image_similar, hopper

TEST_FILE = "Tests/images/hopper.xpm"


def test_sanity() -> None:
    with Image.open(TEST_FILE) as im:
        im.load()
        assert im.mode == "P"
        assert im.size == (128, 128)
        assert im.format == "XPM"

        # large error due to quantization->44 colors.
        assert_image_similar(im.convert("RGB"), hopper(), 23)


def test_bpp2() -> None:
    with Image.open("Tests/images/hopper_bpp2.xpm") as im:
        assert_image_similar(im.convert("RGB"), hopper(), 11)


def test_rgb() -> None:
    with Image.open("Tests/images/hopper_rgb.xpm") as im:
        assert im.mode == "RGB"
        assert_image_similar(im, hopper(), 16)


def test_truncated_header() -> None:
    data = b"/* XPM */"
    with pytest.raises(SyntaxError, match="broken XPM file"):
        with XpmImagePlugin.XpmImageFile(BytesIO(data)):
            pass


def test_cannot_read_color() -> None:
    with open(TEST_FILE, "rb") as fp:
        data = fp.read().split(b"#")[0]
    with pytest.raises(ValueError, match="cannot read this XPM file"):
        with Image.open(BytesIO(data)):
            pass

    with pytest.raises(ValueError, match="cannot read this XPM file"):
        with Image.open(BytesIO(data + b"invalid")):
            pass


def test_not_enough_image_data() -> None:
    with open(TEST_FILE, "rb") as fp:
        data = fp.read().split(b"/* pixels */")[0]
    with Image.open(BytesIO(data)) as im:
        with pytest.raises(ValueError, match="not enough image data"):
            im.load()


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        XpmImagePlugin.XpmImageFile(invalid_file)


def test_load_read() -> None:
    # Arrange
    with Image.open(TEST_FILE) as im:
        assert isinstance(im, XpmImagePlugin.XpmImageFile)
        dummy_bytes = 1

        # Act
        data = im.load_read(dummy_bytes)

    # Assert
    assert len(data) == 16384
