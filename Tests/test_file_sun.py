from __future__ import annotations

import io
import os

import pytest

from PIL import Image, SunImagePlugin, _binary

from .helper import assert_image_equal_tofile, assert_image_similar, hopper

EXTRA_DIR = "Tests/images/sunraster"


def test_sanity() -> None:
    # Arrange
    # Created with ImageMagick: convert hopper.jpg hopper.ras
    test_file = "Tests/images/hopper.ras"

    # Act
    with Image.open(test_file) as im:
        # Assert
        assert im.size == (128, 128)

        assert_image_similar(im, hopper(), 5)  # visually verified

    invalid_file = "Tests/images/flower.jpg"
    with pytest.raises(SyntaxError):
        SunImagePlugin.SunImageFile(invalid_file)


def test_im1() -> None:
    with Image.open("Tests/images/sunraster.im1") as im:
        assert_image_equal_tofile(im, "Tests/images/sunraster.im1.png")


def _sun_header(
    depth: int = 0, file_type: int = 0, palette_length: int = 0
) -> io.BytesIO:
    return io.BytesIO(
        _binary.o32be(0x59A66A95)
        + b"\x00" * 8
        + _binary.o32be(depth)
        + b"\x00" * 4
        + _binary.o32be(file_type)
        + b"\x00" * 4
        + _binary.o32be(palette_length)
    )


def test_unsupported_mode_bit_depth() -> None:
    with pytest.raises(SyntaxError, match="Unsupported Mode/Bit Depth"):
        with SunImagePlugin.SunImageFile(_sun_header()):
            pass


def test_unsupported_color_palette_length() -> None:
    with pytest.raises(SyntaxError, match="Unsupported Color Palette Length"):
        with SunImagePlugin.SunImageFile(_sun_header(depth=1, palette_length=1025)):
            pass


def test_unsupported_palette_type() -> None:
    with pytest.raises(SyntaxError, match="Unsupported Palette Type"):
        with SunImagePlugin.SunImageFile(_sun_header(depth=1, palette_length=1)):
            pass


def test_unsupported_file_type() -> None:
    with pytest.raises(SyntaxError, match="Unsupported Sun Raster file type"):
        with SunImagePlugin.SunImageFile(_sun_header(depth=1, file_type=6)):
            pass


@pytest.mark.skipif(
    not os.path.exists(EXTRA_DIR), reason="Extra image files not installed"
)
def test_rgbx() -> None:
    with open(os.path.join(EXTRA_DIR, "32bpp.ras"), "rb") as fp:
        data = fp.read()

    # Set file type to 3
    data = data[:20] + _binary.o32be(3) + data[24:]

    with Image.open(io.BytesIO(data)) as im:
        r, g, b = im.split()
        im = Image.merge("RGB", (b, g, r))
        assert_image_equal_tofile(im, os.path.join(EXTRA_DIR, "32bpp.png"))


@pytest.mark.skipif(
    not os.path.exists(EXTRA_DIR), reason="Extra image files not installed"
)
def test_others() -> None:
    files = (
        os.path.join(EXTRA_DIR, f)
        for f in os.listdir(EXTRA_DIR)
        if os.path.splitext(f)[1] in (".sun", ".SUN", ".ras")
    )
    for path in files:
        with Image.open(path) as im:
            im.load()
            assert isinstance(im, SunImagePlugin.SunImageFile)
            assert_image_equal_tofile(im, f"{os.path.splitext(path)[0]}.png")
