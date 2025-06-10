from __future__ import annotations

import io
from pathlib import Path

import pytest

from PIL import BmpImagePlugin, Image, _binary

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar_tofile,
    hopper,
)


@pytest.mark.parametrize("mode", ("1", "L", "P", "RGB"))
def test_sanity(mode: str, tmp_path: Path) -> None:
    outfile = tmp_path / "temp.bmp"

    im = hopper(mode)
    im.save(outfile, "BMP")

    with Image.open(outfile) as reloaded:
        reloaded.load()
        assert im.mode == reloaded.mode
        assert im.size == reloaded.size
        assert reloaded.format == "BMP"
        assert reloaded.get_format_mimetype() == "image/bmp"


def test_invalid_file() -> None:
    with open("Tests/images/flower.jpg", "rb") as fp:
        with pytest.raises(SyntaxError):
            BmpImagePlugin.BmpImageFile(fp)


def test_fallback_if_mmap_errors() -> None:
    # This image has been truncated,
    # so that the buffer is not large enough when using mmap
    with Image.open("Tests/images/mmap_error.bmp") as im:
        assert_image_equal_tofile(im, "Tests/images/pal8_offset.bmp")


def test_save_to_bytes() -> None:
    output = io.BytesIO()
    im = hopper()
    im.save(output, "BMP")

    output.seek(0)
    with Image.open(output) as reloaded:
        assert im.mode == reloaded.mode
        assert im.size == reloaded.size
        assert reloaded.format == "BMP"


def test_small_palette(tmp_path: Path) -> None:
    im = Image.new("P", (1, 1))
    colors = [0, 0, 0, 125, 125, 125, 255, 255, 255]
    im.putpalette(colors)

    out = tmp_path / "temp.bmp"
    im.save(out)

    with Image.open(out) as reloaded:
        assert reloaded.getpalette() == colors


def test_save_too_large(tmp_path: Path) -> None:
    outfile = tmp_path / "temp.bmp"
    with Image.new("RGB", (1, 1)) as im:
        im._size = (37838, 37838)
        with pytest.raises(ValueError):
            im.save(outfile)


def test_dpi() -> None:
    dpi = (72, 72)

    output = io.BytesIO()
    with hopper() as im:
        im.save(output, "BMP", dpi=dpi)

    output.seek(0)
    with Image.open(output) as reloaded:
        assert reloaded.info["dpi"] == (72.008961115161, 72.008961115161)


def test_save_bmp_with_dpi(tmp_path: Path) -> None:
    # Test for #1301
    # Arrange
    outfile = tmp_path / "temp.jpg"
    with Image.open("Tests/images/hopper.bmp") as im:
        assert im.info["dpi"] == (95.98654816726399, 95.98654816726399)

        # Act
        im.save(outfile, "JPEG", dpi=im.info["dpi"])

        # Assert
        with Image.open(outfile) as reloaded:
            reloaded.load()
            assert reloaded.info["dpi"] == (96, 96)
            assert reloaded.size == im.size
            assert reloaded.format == "JPEG"


def test_save_float_dpi(tmp_path: Path) -> None:
    outfile = tmp_path / "temp.bmp"
    with Image.open("Tests/images/hopper.bmp") as im:
        im.save(outfile, dpi=(72.21216100543306, 72.21216100543306))
        with Image.open(outfile) as reloaded:
            assert reloaded.info["dpi"] == (72.21216100543306, 72.21216100543306)


def test_load_dib() -> None:
    # test for #1293, Imagegrab returning Unsupported Bitfields Format
    with Image.open("Tests/images/clipboard.dib") as im:
        assert im.format == "DIB"
        assert im.get_format_mimetype() == "image/bmp"

        assert_image_equal_tofile(im, "Tests/images/clipboard_target.png")


@pytest.mark.parametrize(
    "header_size, path",
    (
        (12, "g/pal8os2.bmp"),
        (40, "g/pal1.bmp"),
        (52, "q/rgb32h52.bmp"),
        (56, "q/rgba32h56.bmp"),
        (64, "q/pal8os2v2.bmp"),
        (108, "g/pal8v4.bmp"),
        (124, "g/pal8v5.bmp"),
    ),
)
def test_dib_header_size(header_size: int, path: str) -> None:
    image_path = "Tests/images/bmp/" + path
    with open(image_path, "rb") as fp:
        data = fp.read()[14:]
    assert _binary.i32le(data) == header_size

    dib = io.BytesIO(data)
    with Image.open(dib) as im:
        im.load()


def test_save_dib(tmp_path: Path) -> None:
    outfile = tmp_path / "temp.dib"

    with Image.open("Tests/images/clipboard.dib") as im:
        im.save(outfile)

        with Image.open(outfile) as reloaded:
            assert reloaded.format == "DIB"
            assert reloaded.get_format_mimetype() == "image/bmp"
            assert_image_equal(im, reloaded)


def test_rgba_bitfields() -> None:
    # This test image has been manually hexedited
    # to change the bitfield compression in the header from XBGR to RGBA
    with Image.open("Tests/images/rgb32bf-rgba.bmp") as im:
        # So before the comparing the image, swap the channels
        b, g, r = im.split()[1:]
        im = Image.merge("RGB", (r, g, b))

    assert_image_equal_tofile(im, "Tests/images/bmp/q/rgb32bf-xbgr.bmp")

    # This test image has been manually hexedited
    # to change the bitfield compression in the header from XBGR to ABGR
    with Image.open("Tests/images/rgb32bf-abgr.bmp") as im:
        assert_image_equal_tofile(
            im.convert("RGB"), "Tests/images/bmp/q/rgb32bf-xbgr.bmp"
        )


def test_rle8() -> None:
    with Image.open("Tests/images/hopper_rle8.bmp") as im:
        assert_image_similar_tofile(im.convert("RGB"), "Tests/images/hopper.bmp", 12)

    with Image.open("Tests/images/hopper_rle8_grayscale.bmp") as im:
        assert_image_equal_tofile(im, "Tests/images/bw_gradient.png")

    # This test image has been manually hexedited
    # to have rows with too much data
    with Image.open("Tests/images/hopper_rle8_row_overflow.bmp") as im:
        assert_image_similar_tofile(im.convert("RGB"), "Tests/images/hopper.bmp", 12)

    # Signal end of bitmap before the image is finished
    with open("Tests/images/bmp/g/pal8rle.bmp", "rb") as fp:
        data = fp.read(1063) + b"\x01"
    with Image.open(io.BytesIO(data)) as im:
        with pytest.raises(ValueError):
            im.load()


def test_rle4() -> None:
    with Image.open("Tests/images/bmp/g/pal4rle.bmp") as im:
        assert_image_similar_tofile(im, "Tests/images/bmp/g/pal4.bmp", 12)


@pytest.mark.parametrize(
    "file_name,length",
    (
        # EOF immediately after the header
        ("Tests/images/hopper_rle8.bmp", 1078),
        # EOF during delta
        ("Tests/images/bmp/q/pal8rletrns.bmp", 3670),
        # EOF when reading data in absolute mode
        ("Tests/images/bmp/g/pal8rle.bmp", 1064),
    ),
)
def test_rle8_eof(file_name: str, length: int) -> None:
    with open(file_name, "rb") as fp:
        data = fp.read(length)
    with Image.open(io.BytesIO(data)) as im:
        with pytest.raises(ValueError):
            im.load()


def test_offset() -> None:
    # This image has been hexedited
    # to exclude the palette size from the pixel data offset
    with Image.open("Tests/images/pal8_offset.bmp") as im:
        assert_image_equal_tofile(im, "Tests/images/bmp/g/pal8.bmp")


def test_use_raw_alpha(monkeypatch: pytest.MonkeyPatch) -> None:
    with Image.open("Tests/images/bmp/g/rgb32.bmp") as im:
        assert im.info["compression"] == BmpImagePlugin.BmpImageFile.COMPRESSIONS["RAW"]
        assert im.mode == "RGB"

    monkeypatch.setattr(BmpImagePlugin, "USE_RAW_ALPHA", True)
    with Image.open("Tests/images/bmp/g/rgb32.bmp") as im:
        assert im.mode == "RGBA"
