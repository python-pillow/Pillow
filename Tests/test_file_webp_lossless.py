from __future__ import annotations

from pathlib import Path

import pytest

from PIL import Image

from .helper import assert_image_equal, hopper

pytest.importorskip("PIL._webp", reason="WebP support not installed")
RGB_MODE = "RGB"


def test_write_lossless_rgb(tmp_path: Path) -> None:
    temp_file = tmp_path / "temp.webp"

    hopper(RGB_MODE).save(temp_file, lossless=True)

    with Image.open(temp_file) as image:
        image.load()

        assert image.mode == RGB_MODE
        assert image.size == (128, 128)
        assert image.format == "WEBP"
        image.load()
        image.getdata()

        assert_image_equal(image, hopper(RGB_MODE))
