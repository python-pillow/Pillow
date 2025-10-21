from __future__ import annotations

from pathlib import Path

import pytest

from PIL import Image, features

from .helper import assert_image_equal, hopper


def test_split() -> None:
    def split(mode: str) -> list[tuple[str, int, int]]:
        layers = hopper(mode).split()
        return [(i.mode, i.size[0], i.size[1]) for i in layers]

    assert split("1") == [("1", 128, 128)]
    assert split("L") == [("L", 128, 128)]
    assert split("I") == [("I", 128, 128)]
    assert split("F") == [("F", 128, 128)]
    assert split("P") == [("P", 128, 128)]
    assert split("RGB") == [("L", 128, 128), ("L", 128, 128), ("L", 128, 128)]
    assert split("RGBA") == [
        ("L", 128, 128),
        ("L", 128, 128),
        ("L", 128, 128),
        ("L", 128, 128),
    ]
    assert split("CMYK") == [
        ("L", 128, 128),
        ("L", 128, 128),
        ("L", 128, 128),
        ("L", 128, 128),
    ]
    assert split("YCbCr") == [("L", 128, 128), ("L", 128, 128), ("L", 128, 128)]


@pytest.mark.parametrize(
    "mode", ("1", "L", "I", "F", "P", "RGB", "RGBA", "CMYK", "YCbCr")
)
def test_split_merge(mode: str) -> None:
    expected = Image.merge(mode, hopper(mode).split())
    assert_image_equal(hopper(mode), expected)


def test_split_open(tmp_path: Path) -> None:
    if features.check("zlib"):
        test_file = tmp_path / "temp.png"
    else:
        test_file = tmp_path / "temp.pcx"

    def split_open(mode: str) -> int:
        hopper(mode).save(test_file)
        with Image.open(test_file) as im:
            return len(im.split())

    assert split_open("1") == 1
    assert split_open("L") == 1
    assert split_open("P") == 1
    assert split_open("RGB") == 3
    if features.check("zlib"):
        assert split_open("RGBA") == 4
