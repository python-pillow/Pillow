from __future__ import annotations

from pathlib import Path

import pytest

from PIL import Image, QoiImagePlugin

from .helper import assert_image_equal_tofile, hopper


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


def test_op_index() -> None:
    # QOI_OP_INDEX as the first chunk
    with Image.open("Tests/images/op_index.qoi") as im:
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)


def test_save(tmp_path: Path) -> None:
    f = tmp_path / "temp.qoi"

    im = hopper()
    im.save(f, colorspace="sRGB")

    assert_image_equal_tofile(im, f)

    for path in ("Tests/images/default_font.png", "Tests/images/pil123rgba.png"):
        with Image.open(path) as im:
            im.save(f)

            assert_image_equal_tofile(im, f)

    im = hopper("P")
    with pytest.raises(ValueError, match="Unsupported QOI image mode"):
        im.save(f)
