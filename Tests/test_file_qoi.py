from __future__ import annotations

import pytest

from PIL import Image, QoiImagePlugin

from .helper import assert_image_equal_tofile


def test_sanity() -> None:
    with Image.open("Tests/images/hopper.qoi") as im:
        assert im.mode == "RGB"
        assert im.size == (128, 128)
        assert im.format == "QOI"

        assert_image_equal_tofile(im, "Tests/images/hopper.png")

    with Image.open("Tests/images/pil123rgba.qoi") as im:
        assert im.mode == "RGBA"
        assert im.size == (162, 150)
        assert im.format == "QOI"

        assert_image_equal_tofile(im, "Tests/images/pil123rgba.png")


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        QoiImagePlugin.QoiImageFile(invalid_file)
