from __future__ import annotations

import os
from pathlib import Path

import pytest

from PIL import Image, UnidentifiedImageError

from .helper import assert_image_equal, assert_image_equal_tofile, hopper

_TGA_DIR = os.path.join("Tests", "images", "tga")
_TGA_DIR_COMMON = os.path.join(_TGA_DIR, "common")


_ORIGINS = ("tl", "bl")

_ORIGIN_TO_ORIENTATION = {"tl": 1, "bl": -1}


@pytest.mark.parametrize(
    "size_mode",
    (
        ("1x1", "L"),
        ("200x32", "L"),
        ("200x32", "LA"),
        ("200x32", "P"),
        ("200x32", "RGB"),
        ("200x32", "RGBA"),
    ),
)
@pytest.mark.parametrize("origin", _ORIGINS)
@pytest.mark.parametrize("rle", (True, False))
def test_sanity(
    size_mode: tuple[str, str], origin: str, rle: str, tmp_path: Path
) -> None:
    def roundtrip(original_im: Image.Image) -> None:
        out = tmp_path / "temp.tga"

        original_im.save(out, rle=rle)
        with Image.open(out) as saved_im:
            if rle:
                assert saved_im.info["compression"] == original_im.info["compression"]
            assert saved_im.info["orientation"] == original_im.info["orientation"]
            if mode == "P":
                assert saved_im.getpalette() == original_im.getpalette()

            assert_image_equal(saved_im, original_im)

    size, mode = size_mode
    png_path = os.path.join(_TGA_DIR_COMMON, size + "_" + mode.lower() + ".png")
    with Image.open(png_path) as reference_im:
        assert reference_im.mode == mode

        path_no_ext = os.path.splitext(png_path)[0]
        tga_path = "{}_{}_{}.tga".format(path_no_ext, origin, "rle" if rle else "raw")

        with Image.open(tga_path) as original_im:
            assert original_im.format == "TGA"
            assert original_im.get_format_mimetype() == "image/x-tga"
            if rle:
                assert original_im.info["compression"] == "tga_rle"
            assert original_im.info["orientation"] == _ORIGIN_TO_ORIENTATION[origin]
            if mode == "P":
                assert original_im.getpalette() == reference_im.getpalette()

            assert_image_equal(original_im, reference_im)

            roundtrip(original_im)


def test_palette_depth_8() -> None:
    with pytest.raises(UnidentifiedImageError):
        Image.open("Tests/images/p_8.tga")


def test_palette_depth_16(tmp_path: Path) -> None:
    with Image.open("Tests/images/p_16.tga") as im:
        assert im.palette is not None
        assert im.palette.mode == "RGBA"
        assert_image_equal_tofile(im.convert("RGBA"), "Tests/images/p_16.png")

        out = tmp_path / "temp.png"
        im.save(out)
        with Image.open(out) as reloaded:
            assert_image_equal_tofile(reloaded.convert("RGBA"), "Tests/images/p_16.png")


def test_rgba_16() -> None:
    with Image.open("Tests/images/rgba16.tga") as im:
        assert im.mode == "RGBA"

        assert im.getpixel((0, 0)) == (172, 0, 255, 255)
        assert im.getpixel((1, 0)) == (0, 255, 82, 0)


def test_id_field() -> None:
    # tga file with id field
    test_file = "Tests/images/tga_id_field.tga"

    # Act
    with Image.open(test_file) as im:
        # Assert
        assert im.size == (100, 100)


def test_id_field_rle() -> None:
    # tga file with id field
    test_file = "Tests/images/rgb32rle.tga"

    # Act
    with Image.open(test_file) as im:
        # Assert
        assert im.size == (199, 199)


def test_cross_scan_line() -> None:
    with Image.open("Tests/images/cross_scan_line.tga") as im:
        assert_image_equal_tofile(im, "Tests/images/cross_scan_line.png")

    with Image.open("Tests/images/cross_scan_line_truncated.tga") as im:
        with pytest.raises(OSError):
            im.load()


def test_save(tmp_path: Path) -> None:
    test_file = "Tests/images/tga_id_field.tga"
    with Image.open(test_file) as im:
        out = tmp_path / "temp.tga"

        # Save
        im.save(out)
        with Image.open(out) as test_im:
            assert test_im.size == (100, 100)
            assert test_im.info["id_section"] == im.info["id_section"]

        # RGBA save
        im.convert("RGBA").save(out)
    with Image.open(out) as test_im:
        assert test_im.size == (100, 100)


def test_small_palette(tmp_path: Path) -> None:
    im = Image.new("P", (1, 1))
    colors = [0, 0, 0]
    im.putpalette(colors)

    out = tmp_path / "temp.tga"
    im.save(out)

    with Image.open(out) as reloaded:
        assert reloaded.getpalette() == colors


def test_missing_palette() -> None:
    with Image.open("Tests/images/dilation4.lut") as im:
        assert im.mode == "L"


def test_save_wrong_mode(tmp_path: Path) -> None:
    im = hopper("PA")
    out = tmp_path / "temp.tga"

    with pytest.raises(OSError):
        im.save(out)


def test_save_mapdepth() -> None:
    # This image has been manually hexedited from 200x32_p_bl_raw.tga
    # to include an origin
    test_file = "Tests/images/200x32_p_bl_raw_origin.tga"
    with Image.open(test_file) as im:
        assert_image_equal_tofile(im, "Tests/images/tga/common/200x32_p.png")


def test_save_id_section(tmp_path: Path) -> None:
    test_file = "Tests/images/rgb32rle.tga"
    with Image.open(test_file) as im:
        out = tmp_path / "temp.tga"

        # Check there is no id section
        im.save(out)
    with Image.open(out) as test_im:
        assert "id_section" not in test_im.info

    # Save with custom id section
    im.save(out, id_section=b"Test content")
    with Image.open(out) as test_im:
        assert test_im.info["id_section"] == b"Test content"

    # Save with custom id section greater than 255 characters
    id_section = b"Test content" * 25
    with pytest.warns(
        UserWarning, match="id_section has been trimmed to 255 characters"
    ):
        im.save(out, id_section=id_section)

    with Image.open(out) as test_im:
        assert test_im.info["id_section"] == id_section[:255]

    test_file = "Tests/images/tga_id_field.tga"
    with Image.open(test_file) as im:
        # Save with no id section
        im.save(out, id_section="")
    with Image.open(out) as test_im:
        assert "id_section" not in test_im.info


def test_save_orientation(tmp_path: Path) -> None:
    test_file = "Tests/images/rgb32rle.tga"
    out = tmp_path / "temp.tga"
    with Image.open(test_file) as im:
        assert im.info["orientation"] == -1

        im.save(out, orientation=1)
    with Image.open(out) as test_im:
        assert test_im.info["orientation"] == 1


def test_horizontal_orientations() -> None:
    # These images have been manually hexedited to have the relevant orientations
    with Image.open("Tests/images/rgb32rle_top_right.tga") as im:
        px = im.load()
        assert px is not None
        value = px[90, 90]
        assert isinstance(value, tuple)
        assert value[:3] == (0, 0, 0)

    with Image.open("Tests/images/rgb32rle_bottom_right.tga") as im:
        px = im.load()
        assert px is not None
        value = px[90, 90]
        assert isinstance(value, tuple)
        assert value[:3] == (0, 255, 0)


def test_save_rle(tmp_path: Path) -> None:
    test_file = "Tests/images/rgb32rle.tga"
    with Image.open(test_file) as im:
        assert im.info["compression"] == "tga_rle"

        out = tmp_path / "temp.tga"

        # Save
        im.save(out)
    with Image.open(out) as test_im:
        assert test_im.size == (199, 199)
        assert test_im.info["compression"] == "tga_rle"

    # Save without compression
    im.save(out, compression=None)
    with Image.open(out) as test_im:
        assert "compression" not in test_im.info

    # RGBA save
    im.convert("RGBA").save(out)
    with Image.open(out) as test_im:
        assert test_im.size == (199, 199)

    test_file = "Tests/images/tga_id_field.tga"
    with Image.open(test_file) as im:
        assert "compression" not in im.info

        # Save with compression
        im.save(out, compression="tga_rle")
    with Image.open(out) as test_im:
        assert test_im.info["compression"] == "tga_rle"


def test_save_l_transparency(tmp_path: Path) -> None:
    # There are 559 transparent pixels in la.tga.
    num_transparent = 559

    in_file = "Tests/images/la.tga"
    with Image.open(in_file) as im:
        assert im.mode == "LA"
        assert im.getchannel("A").getcolors()[0][0] == num_transparent

        out = tmp_path / "temp.tga"
        im.save(out)

    with Image.open(out) as test_im:
        assert test_im.mode == "LA"
        assert test_im.getchannel("A").getcolors()[0][0] == num_transparent

        assert_image_equal(im, test_im)
