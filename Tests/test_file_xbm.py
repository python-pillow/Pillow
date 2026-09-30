from __future__ import annotations

from io import BytesIO

import pytest

from PIL import Image, XbmImagePlugin

from .helper import hopper

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


@pytest.mark.parametrize("name", [b"basic_bits", b"basic_xbm", b"bitmap", b"_bitmap2"])
@pytest.mark.parametrize("hotspot", [False, True])
def test_array_name(name: bytes, hotspot: bool) -> None:
    data = PIL151.replace(b"basic_bits", name)
    if hotspot:
        data = data.replace(
            b"static char", b"#define basic_x_hot 3\n#define basic_y_hot 7\nstatic char"
        )

    with Image.open(BytesIO(PIL151)) as expected, Image.open(BytesIO(data)) as im:
        im.load()
        assert im.mode == "1"
        assert im.size == expected.size
        assert im.tobytes() == expected.tobytes()
        if hotspot:
            assert im.info["hotspot"] == (3, 7)
        else:
            assert "hotspot" not in im.info


@pytest.mark.parametrize("name", [b"basic_bits", b"bitmap"])
@pytest.mark.parametrize(
    "suffix", [b"/* sample[] */", b"static char sample[] = {0xff};"]
)
def test_array_name_with_trailing_array(name: bytes, suffix: bytes) -> None:
    data = (
        b"#define basic_width 8\n#define basic_height 1\nstatic char "
        + name
        + b"[] = {0x55};\n"
        + suffix
    )
    with Image.open(BytesIO(data)) as im:
        assert im.tobytes() == b"\xaa"


@pytest.mark.parametrize("name", [b"basic_bits", b"bitmap"])
@pytest.mark.parametrize(
    "comment",
    [b"/* sample[] = {0xff}; */", b"/* sample[] example */", b"// sample[] = {0xff};"],
)
def test_array_name_with_header_comment(name: bytes, comment: bytes) -> None:
    data = (
        b"#define basic_width 8\n#define basic_height 1\n"
        + comment
        + b"\nstatic char "
        + name
        + b"[] = {0x55};\n"
    )
    with Image.open(BytesIO(data)) as im:
        assert im.tobytes() == b"\xaa"


@pytest.mark.parametrize(
    "prefix",
    [
        b"static char metadata[] = {0xff};",
        b"extern char external[]; /* example 0xff */",
        b'static const char label[] = "example";',
        b'char *label = "/*";',
    ],
)
def test_conventional_array_with_preceding_declaration(prefix: bytes) -> None:
    data = (
        b"#define basic_width 8\n#define basic_height 1\n"
        + prefix
        + b"\nstatic char basic_bits[] = {0x55};\n"
    )
    with Image.open(BytesIO(data)) as im:
        assert im.tobytes() == b"\xaa"


@pytest.mark.parametrize(
    "prefix",
    [
        b"extern char external[];",
        b'static char label[] = "example";',
        b'static char label[] = "/*";',
        b'static char label[] = "sample[] = {0xff}";',
        b'static char label[] = "\\"sample[] = {0xff}";',
        b"static char label = '\\'';",
    ],
)
def test_nonconventional_array_with_preceding_declaration(prefix: bytes) -> None:
    data = (
        b"#define basic_width 8\n#define basic_height 1\n"
        + prefix
        + b"\nstatic unsigned char bitmap[] = {0x55};\n"
    )
    with Image.open(BytesIO(data)) as im:
        assert im.tobytes() == b"\xaa"


@pytest.mark.timeout(3)
@pytest.mark.parametrize("declaration", [b"", b"static char bitmap[] = {0x55};"])
@pytest.mark.parametrize("comment", [b"/**/", b"//"])
def test_repeated_header_comments(declaration: bytes, comment: bytes) -> None:
    data = b"#define basic_width 8\n#define basic_height 1\n" + comment * 60 + b"\n"
    if declaration:
        with Image.open(BytesIO(data + declaration)) as im:
            assert im.tobytes() == b"\xaa"
    else:
        with pytest.raises(SyntaxError):
            XbmImagePlugin.XbmImageFile(BytesIO(data))


def test_open() -> None:
    # Arrange
    # Created with `convert hopper.png hopper.xbm`
    filename = "Tests/images/hopper.xbm"

    # Act
    with Image.open(filename) as im:
        # Assert
        assert im.mode == "1"
        assert im.size == (128, 128)


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


@pytest.mark.parametrize("declaration", [b"static char bitmap", b"static char []"])
def test_missing_array_name_or_brackets(declaration: bytes) -> None:
    data = b"#define basic_width 8\n#define basic_height 1\n" + declaration
    with pytest.raises(SyntaxError):
        XbmImagePlugin.XbmImageFile(BytesIO(data))


def test_save_wrong_mode(tmp_path: Path) -> None:
    im = hopper()
    out = tmp_path / "temp.xbm"

    with pytest.raises(OSError):
        im.save(out)


@pytest.mark.parametrize("hotspot", [None, (0, 7)])
def test_hotspot(tmp_path: Path, hotspot: tuple[int, int] | None) -> None:
    im = hopper("1")
    out = tmp_path / "temp.xbm"

    im.save(out, hotspot=hotspot)

    with Image.open(out) as reloaded:
        assert reloaded.info.get("hotspot") == hotspot
