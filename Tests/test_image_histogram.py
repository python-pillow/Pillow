from __future__ import annotations

import pytest

from PIL import Image

from .helper import hopper

expected_data = {
    "1": (256, 0, 10994),
    "CMYK": (1024, 0, 16384),
    "F": (256, 0, 662),
    "HSV": (768, 0, 1696),
    "I": (256, 0, 662),
    "I;16": (256, 0, 8192),
    "I;16B": (256, 0, 8192),
    "I;16L": (256, 0, 8192),
    "I;16N": (256, 0, 8192),
    "L": (256, 0, 662),
    "LA": (512, 0, 662),
    "La": (512, 0, 662),
    "LAB": (768, 0, 1946),
    "P": (256, 0, 1551),
    "PA": (512, 0, 1551),
    "RGB": (768, 4, 675),
    "RGBA": (1024, 0, 16384),
    "RGBa": (1024, 0, 16384),
    "RGBX": (1024, 0, 16384),
    "YCbCr": (768, 0, 1908),
}


@pytest.mark.parametrize("mode", Image.MODES)
def test_histogram(mode: str) -> None:
    h = hopper(mode).histogram()
    assert (len(h), min(h), max(h)) == expected_data[mode]
