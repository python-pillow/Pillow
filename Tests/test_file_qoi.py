from __future__ import annotations

import struct
from io import BytesIO

import pytest

from PIL import Image, QoiImagePlugin

from .helper import assert_image_equal_tofile, hopper

TYPE_CHECKING = False
if TYPE_CHECKING:
    from pathlib import Path


def test_sanity() -> None:
    with Image.open("Tests/images/hopper.qoi") as im:
        assert im.mode == "RGB"
        assert im.size == (128, 128)
        assert im.format == "QOI"

        assert_image_equal_tofile(im, "Tests/images/hopper.png")

    with Image.open("Tests/images/pil123rgba.qoi") as im:
        assert im.mode == "RGBA"
        assert im.size == (162, 150)
        assert im.format == "QOI"

        assert_image_equal_tofile(im, "Tests/images/pil123rgba.png")


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        QoiImagePlugin.QoiImageFile(invalid_file)


@pytest.mark.parametrize("length", (14, 44, 48, 55))
def test_truncated(length: int) -> None:
    with open("Tests/images/pil123rgba.qoi", "rb") as fp:
        data = fp.read()[:length]
    with Image.open(BytesIO(data)) as im:
        with pytest.raises(ValueError, match="not enough image data"):
            im.load()


def test_op_index() -> None:
    # QOI_OP_INDEX as the first chunk
    with Image.open("Tests/images/op_index.qoi") as im:
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)


@pytest.mark.parametrize("channels", (3, 4))
@pytest.mark.parametrize("run_length", (1, 2, 62))
def test_op_run_updates_index(channels: int, run_length: int) -> None:
    data = (
        struct.pack(">4sIIBB", b"qoif", run_length + 2, 1, channels, 0)
        + bytes((0xC0 | (run_length - 1),))  # RUN of the initial opaque black pixel
        + b"\xff\x01\x02\x03\x04"  # RGBA with a different index
        + b"\x35"  # INDEX: opaque black hashes to 255 * 11 % 64 == 53
        + b"\x00" * 7
        + b"\x01"
    )
    black = (0, 0, 0, 255)[:channels]
    expected = [black] * run_length + [(1, 2, 3, 4)[:channels], black]
    with Image.open(BytesIO(data)) as im:
        assert im.mode == ("RGB" if channels == 3 else "RGBA")
        assert im.size == (run_length + 2, 1)
        assert [im.getpixel((x, 0)) for x in range(im.width)] == expected


def test_save(tmp_path: Path) -> None:
    f = tmp_path / "temp.qoi"

    im = hopper()
    im.save(f, colorspace="sRGB")

    assert_image_equal_tofile(im, f)

    for path in ("Tests/images/default_font.png", "Tests/images/pil123rgba.png"):
        with Image.open(path) as im:
            im.save(f)

            assert_image_equal_tofile(im, f)

    im = hopper("P")
    with pytest.raises(ValueError, match="Unsupported QOI image mode"):
        im.save(f)
