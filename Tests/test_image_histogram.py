from __future__ import annotations

import pytest

from PIL import Image

from .helper import hopper


def test_histogram() -> None:
    def histogram(mode: str) -> tuple[int, int, int]:
        h = hopper(mode).histogram()
        return len(h), min(h), max(h)

    assert histogram("1") == (256, 0, 10994)
    assert histogram("L") == (256, 0, 662)
    assert histogram("LA") == (512, 0, 16384)
    assert histogram("La") == (512, 0, 16384)
    assert histogram("I") == (256, 0, 662)
    assert histogram("F") == (256, 0, 662)
    assert histogram("P") == (256, 0, 1551)
    assert histogram("PA") == (512, 0, 16384)
    assert histogram("RGB") == (768, 4, 675)
    assert histogram("RGBA") == (1024, 0, 16384)
    assert histogram("CMYK") == (1024, 0, 16384)
    assert histogram("YCbCr") == (768, 0, 1908)


def test_histogram_masked() -> None:
    mask = Image.new("1", (128, 128), 0)
    crop_box = (0, 0, 128, 64)
    mask.paste(1, crop_box)

    def histogram(mode: str) -> tuple[int, int, int]:
        im = hopper(mode)
        h = im.histogram(mask)
        assert h == im.crop(crop_box).histogram()
        return len(h), min(h), max(h)

    assert histogram("1") == (256, 0, 5024)
    assert histogram("L") == (256, 0, 178)
    assert histogram("LA") == (512, 0, 8192)
    assert histogram("La") == (512, 0, 8192)
    assert histogram("P") == (256, 0, 797)
    assert histogram("PA") == (512, 0, 8192)
    assert histogram("RGB") == (768, 1, 174)
    assert histogram("RGBA") == (1024, 0, 8192)
    assert histogram("CMYK") == (1024, 0, 8192)
    assert histogram("YCbCr") == (768, 0, 1009)


@pytest.mark.parametrize("mode", ("I", "F"))
def test_histogram_masked_unsupported_mode(mode: str) -> None:
    mask = Image.new("1", (128, 128))
    with pytest.raises(ValueError, match="image has wrong mode"):
        hopper(mode).histogram(mask)


def test_histogram_mask_size_mismatch() -> None:
    mask = Image.new("1", (1, 1))
    with pytest.raises(ValueError, match="images do not match"):
        hopper("L").histogram(mask)


@pytest.mark.parametrize(
    "mode", ("LA", "La", "I", "F", "P", "PA", "RGB", "RGBA", "CMYK", "YCbCr")
)
def test_histogram_bad_mask_mode(mode: str) -> None:
    mask = Image.new(mode, (128, 128))
    with pytest.raises(ValueError, match="bad transparency mask"):
        hopper("L").histogram(mask)
