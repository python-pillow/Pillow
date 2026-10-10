from __future__ import annotations

from io import BytesIO

import pytest

from PIL import Image, UnidentifiedImageError, XbmImagePlugin

from .helper import assert_image_equal, hopper, timeout_unless_slower_valgrind

TYPE_CHECKING = False
if TYPE_CHECKING:
    from pathlib import Path

PIL151 = b"""
#define basic_width 32
#define basic_height 32
static char basic_bits[] = {
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00,
0x80, 0xff, 0xff, 0x01, 0x40, 0x00, 0x00, 0x02,
0x20, 0x00, 0x00, 0x04, 0x20, 0x00, 0x00, 0x04, 0x10, 0x00, 0x00, 0x08,
0x10, 0x00, 0x00, 0x08,
0x10, 0x00, 0x00, 0x08, 0x10, 0x00, 0x00, 0x08,
0x10, 0x00, 0x00, 0x08, 0x10, 0x00, 0x00, 0x08, 0x10, 0x00, 0x00, 0x08,
0x20, 0x00, 0x00, 0x04,
0x20, 0x00, 0x00, 0x04, 0x40, 0x00, 0x00, 0x02,
0x80, 0xff, 0xff, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00,
};
"""


def test_pil151() -> None:
    with Image.open(BytesIO(PIL151)) as im:
        im.load()
        assert im.mode == "1"
        assert im.size == (32, 32)


def test_open() -> None:
    # Arrange
    # Created with `convert hopper.png hopper.xbm`
    filename = "Tests/images/hopper.xbm"

    # Act
    with Image.open(filename) as im:
        # Assert
        assert im.mode == "1"
        assert im.size == (128, 128)


@pytest.mark.parametrize(
    "comment",
    (
        b"/* comment */\n",
        b"/*\nThis is an example file\n*/\n",
        b"// comment\n",
        b"// " + b"A" * 200 + b"\n",
        b"/* one */\n// two\n",
    ),
)
def test_leading_comment(comment: bytes) -> None:
    with Image.open(BytesIO(comment + PIL151)) as im:
        assert im.format == "XBM"
        assert im.size == (32, 32)

        with Image.open(BytesIO(PIL151)) as expected:
            assert_image_equal(im, expected)


def test_unterminated_comment() -> None:
    with pytest.raises(UnidentifiedImageError):
        Image.open(BytesIO(b"/* unterminated\n" + PIL151))


def test_open_filename_with_underscore() -> None:
    # Arrange
    # Created with `convert hopper.png hopper_underscore.xbm`
    filename = "Tests/images/hopper_underscore.xbm"

    # Act
    with Image.open(filename) as im:
        # Assert
        assert im.mode == "1"
        assert im.size == (128, 128)


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        XbmImagePlugin.XbmImageFile(invalid_file)


def test_save_wrong_mode(tmp_path: Path) -> None:
    im = hopper()
    out = tmp_path / "temp.xbm"

    with pytest.raises(OSError):
        im.save(out)


def test_hotspot(tmp_path: Path) -> None:
    im = hopper("1")
    out = tmp_path / "temp.xbm"

    hotspot = (0, 7)
    im.save(out, hotspot=hotspot)

    with Image.open(out) as reloaded:
        assert reloaded.info["hotspot"] == hotspot


@timeout_unless_slower_valgrind(1)
def test_redos() -> None:
    redos = b""
    for prop in (b"width", b"height", b"x_hot", b"y_hot"):
        redos += b"#define" + b" " * 60 + b"_" + prop + b" 1\r"
    redos += b"\r" * 60 + b"_bits" + b"A" * 512

    b = BytesIO(redos)
    with pytest.raises(SyntaxError):
        XbmImagePlugin.XbmImageFile(b)
