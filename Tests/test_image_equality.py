from __future__ import annotations

import pytest

from PIL import Image


def _make_rows(size: tuple[int, int]) -> list[bytes]:
    # Build test image data
    return [
        bytes((y * (size[0] - 1) + x) % 256 for x in range(size[0]))
        for y in range(size[1])
    ]


@pytest.mark.parametrize("mode", Image.MODES)
def test_equal(mode: str) -> None:
    num_img_bytes = len(Image.new(mode, (2, 2)).tobytes())
    data = bytes(range(num_img_bytes))
    img_a = Image.frombytes(mode, (2, 2), data)
    img_b = Image.frombytes(mode, (2, 2), data)
    assert img_a.tobytes() == img_b.tobytes()
    assert img_a == img_b


def test_equal_mode_1_nonzero_values() -> None:
    # 1 mode pixels are either empty (0) or not (1-255)
    img_a = Image.new("1", (1, 1), 1)
    img_b = Image.new("1", (1, 1), 255)
    assert img_a.tobytes() == img_b.tobytes()
    assert img_a == img_b


@pytest.mark.parametrize("mode", Image.MODES)
def test_not_equal(mode: str) -> None:
    num_img_bytes = len(Image.new(mode, (2, 2)).tobytes())
    if mode == "1":
        data_a = bytes((0, 255))
        data_b = bytes((255, 0))
    else:
        data_a = bytes(range(num_img_bytes))
        data_b = bytes(range(255, 255 - num_img_bytes, -1))
    img_a = Image.frombytes(mode, (2, 2), data_a)
    img_b = Image.frombytes(mode, (2, 2), data_b)
    assert img_a.tobytes() != img_b.tobytes()
    assert img_a != img_b


@pytest.mark.parametrize("mode", ("RGB", "YCbCr", "HSV", "LAB"))
def test_equal_three_channels_four_bytes(mode: str) -> None:
    color_a = 0x00B3B231 if mode == "LAB" else 0x00333231
    color_b = color_a | 0xFF000000

    img_a = Image.new(mode, (1, 1), color_a)
    img_b = Image.new(mode, (1, 1), color_b)
    assert img_a.tobytes() == img_b.tobytes() == b"123"
    assert img_a == img_b


@pytest.mark.parametrize("mode", ("LA", "La", "PA"))
def test_equal_two_channels_four_bytes(mode: str) -> None:
    # Test that for LA/La/PA modes, where the data is stored in the 1st and 4th
    # byte of each pixel, the middle bytes are ignored.
    img_a = Image.new(mode, (1, 1), 0x32000031)
    img_b = Image.new(mode, (1, 1), 0x32FFFF31)
    assert img_a.tobytes() == img_b.tobytes() == b"12"
    assert img_a == img_b


def test_types() -> None:
    im = Image.new("L", (1, 1))
    assert im.im == im.im
    assert im.im != 42

    class EqMock:
        eq_called = False

        def __eq__(self, other: object) -> bool:
            self.eq_called = True
            return True

    x = EqMock()
    assert im.im == x
    assert x.eq_called


def _make_palette_image(mode: str, data: bytes, rawmode: str) -> Image.Image:
    im = Image.new(mode, (2, 2))
    im.putpalette(data, rawmode)
    return im


@pytest.mark.parametrize("mode", ("P", "PA"))
def test_equal_palette(mode: str) -> None:
    img_a = _make_palette_image(mode, b"\x01\x02\x03" * 256, "RGB")
    img_b = _make_palette_image(mode, b"\x01\x02\x03" * 256, "RGB")
    assert img_a == img_b

    img_a = _make_palette_image(mode, b"\x01\x02\x03\x80" * 256, "RGBA")
    img_b = _make_palette_image(mode, b"\x01\x02\x03\x80" * 256, "RGBA")
    assert img_a == img_b


@pytest.mark.parametrize("mode", ("P", "PA"))
def test_not_equal_palette_alpha(mode: str) -> None:
    # Palettes that differ only in alpha are not equal.
    img_a = _make_palette_image(mode, b"\x01\x02\x03\xff" * 256, "RGBA")
    img_b = _make_palette_image(mode, b"\x01\x02\x03\x00" * 256, "RGBA")
    assert img_a.getpalette() == img_b.getpalette()  # implicit RGB rawmode
    assert img_a.getpalette(None) != img_b.getpalette(None)
    assert img_a != img_b

    # An RGB palette is not the same as an otherwise identical opaque RGBA palette
    img_a = _make_palette_image(mode, b"\x01\x02\x03" * 256, "RGB")
    img_b = _make_palette_image(mode, b"\x01\x02\x03\xff" * 256, "RGBA")
    assert img_a.getpalette() == img_b.getpalette()  # implicit RGB rawmode
    assert img_a.getpalette(None) != img_b.getpalette(None)
    assert img_a != img_b
