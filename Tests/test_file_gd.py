from __future__ import annotations

import pytest

from PIL import GdImageFile, UnidentifiedImageError

TEST_GD_FILE = "Tests/images/hopper.gd"


def test_sanity() -> None:
    with GdImageFile.open(TEST_GD_FILE) as im:
        assert im.size == (128, 128)
        assert im.format == "GD"


def test_bad_mode() -> None:
    with pytest.raises(ValueError):
        GdImageFile.open(TEST_GD_FILE, "bad mode")


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(UnidentifiedImageError):
        GdImageFile.open(invalid_file)
