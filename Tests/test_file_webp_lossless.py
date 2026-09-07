from __future__ import annotations

import pytest

from PIL import Image

from .helper import assert_image_equal, hopper

TYPE_CHECKING = False
if TYPE_CHECKING:
    from pathlib import Path

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

        assert_image_equal(image, hopper(RGB_MODE))


def test_lossless(tmp_path: Path) -> None:
    lossless_file = tmp_path / "lossless.webp"
    for lossless in (True, False):
        hopper(RGB_MODE).save(lossless_file, lossless=lossless)
        with Image.open(lossless_file) as image:
            assert image.info["lossless"] is lossless

    with Image.open("Tests/images/hopper.webp") as image:
        assert image.info["lossless"] is False
