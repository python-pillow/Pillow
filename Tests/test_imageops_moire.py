from __future__ import annotations

from PIL import Image, ImageOps


def test_moire_output_size() -> None:
    img = Image.new("RGB", (100, 100), (128, 128, 128))
    result = ImageOps.moire(img)
    assert result.size == img.size


def test_moire_output_mode() -> None:
    img = Image.new("RGB", (100, 100), (128, 128, 128))
    result = ImageOps.moire(img)
    assert result.mode == "RGB"
