from __future__ import annotations

import pytest

from PIL import Image, features

from .helper import PillowLeakTestCase, assert_image_equal, hopper

TYPE_CHECKING = False
if TYPE_CHECKING:
    from pathlib import Path


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


def test_merge_single_band_mode_mismatch() -> None:
    with pytest.raises(ValueError, match="images do not match"):
        Image.merge("F", [Image.new("L", (1, 1))])


class TestMergeLeak(PillowLeakTestCase):
    mem_limit = 4 * 1024  # kb
    iterations = 100

    def test_merge_single_band_mode_mismatch(self) -> None:
        # A tall image, so that the leaked row pointers count towards RSS.
        # Each set of row pointers is 1 MB, so the allocator holding on to one
        # after it has been freed stays within mem_limit, but leaking them does not
        im = Image.new("L", (1, 128 * 1024))

        def core() -> None:
            with pytest.raises(ValueError):
                Image.merge("F", [im])

        self._test_leak(core)
