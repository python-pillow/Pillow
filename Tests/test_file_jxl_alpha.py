from __future__ import annotations

import pytest

from PIL import Image

from .helper import assert_image_similar_tofile

_jpegxl = pytest.importorskip("PIL._jpegxl", reason="JPEG XL support not installed")


def test_read_rgba() -> None:
    """
    Can we read an RGBA mode file without error?
    Does it have the bits we expect?
    """

    # Generated with `cjxl transparent.png transparent.jxl -q 100 -e 8`
    file_path = "Tests/images/transparent.jxl"
    with Image.open(file_path) as image:
        assert image.mode == "RGBA"
        assert image.size == (200, 150)
        assert image.format == "JPEG XL"
        image.load()
        image.getdata()

        image.tobytes()

        assert_image_similar_tofile(image, "Tests/images/transparent.png", 1.0)
