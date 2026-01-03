from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest

from PIL import Image, SgiImagePlugin

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar,
    hopper,
)


def test_rgb() -> None:
    # Created with ImageMagick then renamed:
    # convert hopper.ppm -compress None sgi:hopper.rgb
    test_file = "Tests/images/hopper.rgb"

    with Image.open(test_file) as im:
        assert_image_equal(im, hopper())
        assert im.get_format_mimetype() == "image/rgb"


def test_rgb16() -> None:
    assert_image_equal_tofile(hopper(), "Tests/images/hopper16.rgb")


def test_l() -> None:
    # Created with ImageMagick
    # convert hopper.ppm -monochrome -compress None sgi:hopper.bw
    test_file = "Tests/images/hopper.bw"

    with Image.open(test_file) as im:
        assert_image_similar(im, hopper("L"), 2)
        assert im.get_format_mimetype() == "image/sgi"


def test_rgba() -> None:
    # Created with ImageMagick:
    # convert transparent.png -compress None transparent.sgi
    test_file = "Tests/images/transparent.sgi"

    with Image.open(test_file) as im:
        assert_image_equal_tofile(im, "Tests/images/transparent.png")
        assert im.get_format_mimetype() == "image/sgi"


def test_rle() -> None:
    # Created with ImageMagick:
    # convert hopper.ppm  hopper.sgi
    test_file = "Tests/images/hopper.sgi"

    with Image.open(test_file) as im:
        assert_image_equal_tofile(im, "Tests/images/hopper.rgb")


def test_rle16() -> None:
    test_file = "Tests/images/tv16.sgi"

    with Image.open(test_file) as im:
        assert_image_equal_tofile(im, "Tests/images/tv.rgb")


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(ValueError):
        SgiImagePlugin.SgiImageFile(invalid_file)


def test_unsupported_image_mode() -> None:
    with open("Tests/images/hopper.rgb", "rb") as fp:
        data = fp.read()
    data = data[:3] + b"\x03" + data[4:]
    with pytest.raises(ValueError, match="Unsupported SGI image mode"):
        with Image.open(BytesIO(data)):
            pass


def roundtrip(img: Image.Image, tmp_path: Path) -> None:
    out = tmp_path / "temp.sgi"
    img.save(out, format="sgi")
    assert_image_equal_tofile(img, out)

    out = tmp_path / "fp.sgi"
    with open(out, "wb") as fp:
        img.save(fp)
        assert_image_equal_tofile(img, out)

        assert not fp.closed


@pytest.mark.parametrize("mode", ("L", "RGB", "RGBA"))
def test_write(mode: str, tmp_path: Path) -> None:
    roundtrip(hopper(mode), tmp_path)


def test_write_L_mode_1_dimension(tmp_path: Path) -> None:
    roundtrip(Image.new("L", (10, 1)), tmp_path)


def test_write16(tmp_path: Path) -> None:
    test_file = "Tests/images/hopper16.rgb"

    with Image.open(test_file) as im:
        out = tmp_path / "temp.sgi"
        im.save(out, format="sgi", bpc=2)

        assert_image_equal_tofile(im, out)


def test_unsupported_mode(tmp_path: Path) -> None:
    im = hopper("LA")
    out = tmp_path / "temp.sgi"

    with pytest.raises(ValueError):
        im.save(out, format="sgi")


def test_unsupported_number_of_bytes_per_pixel(tmp_path: Path) -> None:
    im = hopper()
    out = tmp_path / "temp.sgi"

    with pytest.raises(ValueError, match="Unsupported number of bytes per pixel"):
        im.save(out, bpc=3)
