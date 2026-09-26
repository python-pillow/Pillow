from __future__ import annotations

import itertools
from unittest.mock import Mock

import pytest

from PIL import Image


def _make_rows(width: int, height: int) -> list[bytes]:
    """Build test image data of width x height."""
    return [
        bytes((y * (width - 1) + x) % 256 for x in range(width)) for y in range(height)
    ]


def _frombuffer(
    mode: str, size: tuple[int, int], data: bytes, *, stride: int = 0, ystep: int = 1
) -> Image.Image:
    im = Image.frombuffer(mode, size, data, "raw", mode, stride, ystep)
    assert im.readonly  # Sanity check (that we took the map_buffer path)
    return im


@pytest.mark.parametrize("mode", Image.MODES)
def test_equal(mode: str) -> None:
    num_img_bytes = len(Image.new(mode, (2, 2)).tobytes())
    data = bytes(range(ord("A"), ord("A") + num_img_bytes))
    img_a = Image.frombytes(mode, (2, 2), data)
    img_b = Image.frombytes(mode, (2, 2), data)
    assert img_a.tobytes() == img_b.tobytes()
    assert img_a == img_b


def test_not_equal_mode_1() -> None:
    # With mode "1" different bytes can map to the same value,
    # so we have to be more specific with the values we use.
    for bytes_a, bytes_b in itertools.permutations(
        (bytes(x) for x in itertools.product(b"\x00\xff", repeat=4)), 2
    ):
        # Use rawmode "1;8" so that each full byte is interpreted as a value
        # instead of the bits in the bytes being interpreted as values.
        img_a = Image.frombytes("1", (2, 2), bytes_a, "raw", "1;8")
        img_b = Image.frombytes("1", (2, 2), bytes_b, "raw", "1;8")
        assert img_a.tobytes() != img_b.tobytes()
        assert img_a != img_b


@pytest.mark.parametrize("mode", [mode for mode in Image.MODES if mode != "1"])
def test_not_equal(mode: str) -> None:
    num_img_bytes = len(Image.new(mode, (2, 2)).tobytes())
    data_a = bytes(range(ord("A"), ord("A") + num_img_bytes))
    data_b = bytes(range(ord("Z"), ord("Z") - num_img_bytes, -1))
    img_a = Image.frombytes(mode, (2, 2), data_a)
    img_b = Image.frombytes(mode, (2, 2), data_b)
    assert img_a.tobytes() != img_b.tobytes()
    assert img_a != img_b


@pytest.mark.parametrize("mode", ("RGB", "YCbCr", "HSV", "LAB"))
def test_equal_three_channels_four_bytes(mode: str) -> None:
    # The "A" and "B" values in LAB images are signed values from -128 to 127,
    # but we store them as unsigned values from 0 to 255, so we need to use
    # slightly different input bytes for LAB to get the same output.
    img_a = Image.new(mode, (1, 1), 0x00B3B231 if mode == "LAB" else 0x00333231)
    img_b = Image.new(mode, (1, 1), 0xFFB3B231 if mode == "LAB" else 0xFF333231)
    assert img_a.tobytes() == img_b.tobytes() == b"123"
    assert img_a == img_b


@pytest.mark.parametrize("mode", ("LA", "La", "PA"))
def test_equal_two_channels_four_bytes(mode: str) -> None:
    # Test that for LA/La/PA modes, where the data is stored in the 1st and 4th
    # byte of each pixel, the middle bytes are masked off for comparison.
    img_a = Image.new(mode, (1, 1), 0x32000031)
    img_b = Image.new(mode, (1, 1), 0x32FFFF31)
    assert img_a.tobytes() == img_b.tobytes() == b"12"
    assert img_a == img_b


def test_not_equal_rgbx_padding() -> None:
    # Ensure RGBX's last byte is compared, even if it has no image meaning.
    img_a = Image.frombytes("RGBX", (1, 1), b"1234")
    img_b = Image.frombytes("RGBX", (1, 1), b"123\xff")
    assert img_a.tobytes() != img_b.tobytes()
    assert img_a != img_b


def test_compare_with_other_type() -> None:
    im = Image.new("L", (1, 1))
    assert im.im == im.im
    assert im.im != 42
    # Check that the other object's comparison method is called.
    x = Mock(__eq__=Mock(return_value=True))
    assert im.im == x
    assert x.__eq__.called  # type: ignore[attr-defined]


def test_equal_frombuffer_stride() -> None:
    # Test that a buffer-mapped image's padding bytes (stride)
    # are not part of the comparison.
    width, height, stride = 3, 4, 8
    rows = _make_rows(width, height)
    buffer_a = b"".join(row + b"\x00" * (stride - width) for row in rows)
    buffer_b = b"".join(row + b"\xff" * (stride - width) for row in rows)
    assert buffer_a != buffer_b
    img_a = _frombuffer("L", (width, height), buffer_a, stride=stride)
    img_b = _frombuffer("L", (width, height), buffer_b, stride=stride)
    assert img_a.tobytes() == img_b.tobytes()  # Padding bytes disappear
    assert img_a == img_b


def test_not_equal_frombuffer_stride() -> None:
    # Test that differences within strided rows are found,
    # even if padding matches.
    width, height, stride = 3, 4, 8
    rows = _make_rows(width, height)
    padding = b"\xab" * (stride - width)
    buffer_a = b"".join(row + padding for row in rows)
    rows[height - 1] = bytes(42) + rows[height - 1][1:]
    buffer_b = b"".join(row + padding for row in rows)

    img_a = _frombuffer("L", (width, height), buffer_a, stride=stride)
    img_b = _frombuffer("L", (width, height), buffer_b, stride=stride)
    assert img_a.tobytes() != img_b.tobytes()
    assert img_a != img_b


def test_equal_frombuffer_ystep() -> None:
    # Test that ystep=-1 (rows in reverse order) is handled correctly.
    width, height = 3, 4
    rows = _make_rows(width, height)
    img_a = _frombuffer("L", (width, height), b"".join(rows))
    img_b = _frombuffer("L", (width, height), b"".join(reversed(rows)), ystep=-1)
    assert img_a.tobytes() == img_b.tobytes()
    assert img_a == img_b
