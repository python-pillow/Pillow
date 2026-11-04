from __future__ import annotations

import copy
from io import BytesIO

import pytest

from PIL import Image

from .helper import hopper, skip_unless_feature


@pytest.mark.parametrize("mode", ("1", "P", "L", "RGB", "I", "F"))
def test_copy(mode: str) -> None:
    cropped_coordinates = (10, 10, 20, 20)
    cropped_size = (10, 10)

    # Internal copy method
    im = hopper(mode)
    out = im.copy()
    assert out.mode == im.mode
    assert out.size == im.size

    # Python's copy method
    im = hopper(mode)
    out = copy.copy(im)
    assert out.mode == im.mode
    assert out.size == im.size

    # Internal copy method on a cropped image
    im = hopper(mode)
    out = im.crop(cropped_coordinates).copy()
    assert out.mode == im.mode
    assert out.size == cropped_size

    # Python's copy method on a cropped image
    im = hopper(mode)
    out = copy.copy(im.crop(cropped_coordinates))
    assert out.mode == im.mode
    assert out.size == cropped_size


def test_copy_zero() -> None:
    im = Image.new("RGB", (0, 0))
    out = im.copy()
    assert out.mode == im.mode
    assert out.size == im.size


@skip_unless_feature("libtiff")
def test_deepcopy() -> None:
    with Image.open("Tests/images/g4_orientation_5.tif") as im:
        assert im.size == (590, 88)

        out = copy.deepcopy(im)
    assert out.size == (590, 88)


def test_copy_info_list() -> None:
    # Construct IPTC image
    def field(tag: tuple[int, int], value: bytes) -> bytes:
        return bytes((0x1C,) + tag + (0, len(value))) + value

    data = field((2, 25), b"Keyword1")
    data += field((2, 25), b"Keyword2")
    data += field((3, 60), bytes((1, 0)))  # layers, component
    data += field((3, 120), bytes((1,)))  # compression
    data += field((3, 20), b"\x01")  # width
    data += field((3, 30), b"\x01")  # height
    data += field((8, 10), bytes((0,)))
    f = BytesIO(data)

    with Image.open(f) as im:
        # Copy
        im_copy = im.copy()
        assert im_copy.info[(2, 25)] is not im.info[(2, 25)]

        im_copy.info[(2, 25)].append(b"KeywordForCopy")
        assert im.info[(2, 25)] == [b"Keyword1", b"Keyword2"]

        # Transform
        im_transform = im.transform(im.size, Image.Transform.AFFINE, [1, 0, 0, 0, 1, 0])
        assert im_transform.info[(2, 25)] is not im.info[(2, 25)]

        im_transform.info[(2, 25)].append(b"KeywordForTransform")
        assert im.info[(2, 25)] == [b"Keyword1", b"Keyword2"]
