from __future__ import annotations

import pytest

from PIL import Image

from .helper import hopper

expected_data = {
    "1": (256, 0, 10994, -6588993366496339844),
    "CMYK": (1024, 0, 16384, 6499941520588169132),
    "F": (256, 0, 662, -6473002676204311189),
    "HSV": (768, 0, 1696, -6543359421857819796),
    "I": (256, 0, 662, -6473002676204311189),
    "I;16": (256, 0, 8192, 5889973619001565923),
    "I;16B": (256, 0, 8192, 5889973619001565923),
    "I;16L": (256, 0, 8192, 5889973619001565923),
    "I;16N": (256, 0, 8192, 5889973619001565923),
    "L": (256, 0, 662, -2745750633816556827),
    "LA": (512, 0, 662, -7010327511106502095),
    "La": (512, 0, 662, -7010327511106502095),
    "LAB": (768, 0, 1946, -5543905267928649909),
    "P": (256, 0, 1551, -8229466336626460515),
    "PA": (512, 0, 1551, 5750919599917307801),
    "RGB": (768, 4, 675, -7521681876442962674),
    "RGBA": (1024, 0, 16384, -4362402434932696434),
    "RGBa": (1024, 0, 16384, -4362402434932696434),
    "RGBX": (1024, 0, 16384, -4362402434932696434),
    "YCbCr": (768, 0, 1908, -1513926274659056238),
}


@pytest.mark.parametrize("mode", Image.MODES)
def test_histogram(mode: str) -> None:
    h = hopper(mode).histogram()
    # If all values are checked in the same assert and they don't match,
    # the error message gets truncated. So use multiple asserts to see
    # the full message.
    assert (len(h), min(h), max(h)) == expected_data[mode][:3]
    assert hash(tuple(h)) == expected_data[mode][3]
