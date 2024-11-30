from __future__ import annotations

import pytest

from PIL import FtexImagePlugin, Image

from .helper import assert_image_equal_tofile, assert_image_similar


def test_load_raw() -> None:
    with Image.open("Tests/images/ftex_uncompressed.ftu") as im:
        assert_image_equal_tofile(im, "Tests/images/ftex_uncompressed.png")


def test_load_dxt1() -> None:
    with Image.open("Tests/images/ftex_dxt1.ftc") as im:
        with Image.open("Tests/images/ftex_dxt1.png") as target:
            assert_image_similar(im, target.convert("RGBA"), 15)


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        FtexImagePlugin.FtexImageFile(invalid_file)
