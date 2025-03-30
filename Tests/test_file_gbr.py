from __future__ import annotations

import pytest

from PIL import GbrImagePlugin, Image

from .helper import assert_image_equal_tofile


def test_gbr_file() -> None:
    with Image.open("Tests/images/gbr.gbr") as im:
        assert_image_equal_tofile(im, "Tests/images/gbr.png")


def test_load() -> None:
    with Image.open("Tests/images/gbr.gbr") as im:
        px = im.load()
        assert px is not None
        assert px[0, 0] == (0, 0, 0, 0)

        # Test again now that it has already been loaded once
        px = im.load()
        assert px is not None
        assert px[0, 0] == (0, 0, 0, 0)


def test_multiple_load_operations() -> None:
    with Image.open("Tests/images/gbr.gbr") as im:
        im.load()
        im.load()
        assert_image_equal_tofile(im, "Tests/images/gbr.png")


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        GbrImagePlugin.GbrImageFile(invalid_file)
