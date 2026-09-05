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


def im_with_comments() -> BytesIO:
    im = Image.new("L", (4, 4), 128)
    buf = BytesIO()
    im.save(buf, format="IM")
    raw = buf.getvalue()

    header = (
        b"Image type: Greyscale image\r\n"
        b"Image size (x*y): 4*4\r\n"
        b"File size (no of images): 1\r\n"
        b"Comment: first comment\r\n"
        b"Comment: second comment\r\n"
    )
    header += b"\x00" * (511 - len(header)) + b"\x1a"

    return BytesIO(header + raw[512:])


def test_copy_list_info_im() -> None:
    with Image.open(im_with_comments()) as loaded:
        out = loaded.copy()
        assert out.info["Comment"] is not loaded.info["Comment"]

        out.info["Comment"].append("added only to the copy")
        assert loaded.info["Comment"] == ["first comment", "second comment"]


def test_transform_list_info_im() -> None:
    with Image.open(im_with_comments()) as loaded:
        out = loaded.transform(loaded.size, Image.Transform.AFFINE, [1, 0, 0, 0, 1, 0])
        assert out.info["Comment"] is not loaded.info["Comment"]

        out.info["Comment"].append("added only to the rotated copy")
        assert loaded.info["Comment"] == ["first comment", "second comment"]


def test_copy_list_info_iptc() -> None:
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
        im2 = im.copy()
        assert im2.info[(2, 25)] is not im.info[(2, 25)]

        im2.info[(2, 25)].append(b"KeywordForCopy")
        assert im.info[(2, 25)] == [b"Keyword1", b"Keyword2"]
