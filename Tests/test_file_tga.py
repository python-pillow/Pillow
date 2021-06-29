import os
from glob import glob
from itertools import product

import pytest

from PIL import Image

from .helper import assert_image_equal, assert_image_equal_tofile, hopper

_TGA_DIR = os.path.join("Tests", "images", "tga")
_TGA_DIR_COMMON = os.path.join(_TGA_DIR, "common")


_MODES = ("L", "LA", "P", "RGB", "RGBA")
_ORIGINS = ("tl", "bl")

_ORIGIN_TO_ORIENTATION = {"tl": 1, "bl": -1}


def test_sanity(tmp_path):
    for mode in _MODES:

        def roundtrip(original_im):
            out = str(tmp_path / "temp.tga")

            original_im.save(out, rle=rle)
            with Image.open(out) as saved_im:
                if rle:
                    assert (
                        saved_im.info["compression"] == original_im.info["compression"]
                    )
                assert saved_im.info["orientation"] == original_im.info["orientation"]
                if mode == "P":
                    assert saved_im.getpalette() == original_im.getpalette()

                assert_image_equal(saved_im, original_im)

        png_paths = glob(os.path.join(_TGA_DIR_COMMON, f"*x*_{mode.lower()}.png"))

        for png_path in png_paths:
            with Image.open(png_path) as reference_im:
                assert reference_im.mode == mode

                path_no_ext = os.path.splitext(png_path)[0]
                for origin, rle in product(_ORIGINS, (True, False)):
                    tga_path = "{}_{}_{}.tga".format(
                        path_no_ext, origin, "rle" if rle else "raw"
                    )

                    with Image.open(tga_path) as original_im:
                        assert original_im.format == "TGA"
                        assert original_im.get_format_mimetype() == "image/x-tga"
                        if rle:
                            assert original_im.info["compression"] == "tga_rle"
                        assert (
                            original_im.info["orientation"]
                            == _ORIGIN_TO_ORIENTATION[origin]
                        )
                        if mode == "P":
                            assert original_im.getpalette() == reference_im.getpalette()

                        assert_image_equal(original_im, reference_im)

                        roundtrip(original_im)


def test_palette_depth_16(tmp_path):
    with Image.open("Tests/images/p_16.tga") as im:
        assert_image_equal_tofile(im.convert("RGB"), "Tests/images/p_16.png")

        out = str(tmp_path / "temp.png")
        im.save(out)
        with Image.open(out) as reloaded:
            assert_image_equal_tofile(reloaded.convert("RGB"), "Tests/images/p_16.png")


def test_id_field():
    # tga file with id field
    test_file = "Tests/images/tga_id_field.tga"

    # Act
    with Image.open(test_file) as im:

        # Assert
        assert im.size == (100, 100)


def test_id_field_rle():
    # tga file with id field
    test_file = "Tests/images/rgb32rle.tga"

    # Act
    with Image.open(test_file) as im:

        # Assert
        assert im.size == (199, 199)


def test_save(tmp_path):
    test_file = "Tests/images/tga_id_field.tga"
    with Image.open(test_file) as im:
        out = str(tmp_path / "temp.tga")

        # Save
        im.save(out)
        with Image.open(out) as test_im:
            assert test_im.size == (100, 100)
            assert test_im.info["id_section"] == im.info["id_section"]

        # RGBA save
        im.convert("RGBA").save(out)
    with Image.open(out) as test_im:
        assert test_im.size == (100, 100)


def test_save_wrong_mode(tmp_path):
    im = hopper("PA")
    out = str(tmp_path / "temp.tga")

    with pytest.raises(OSError):
        im.save(out)


def test_save_mapdepth():
    # This image has been manually hexedited from 200x32_p_bl_raw.tga
    # to include an origin
    test_file = "Tests/images/200x32_p_bl_raw_origin.tga"
    with Image.open(test_file) as im:
        assert_image_equal_tofile(im, "Tests/images/tga/common/200x32_p.png")


def test_save_id_section(tmp_path):
    test_file = "Tests/images/rgb32rle.tga"
    with Image.open(test_file) as im:
        out = str(tmp_path / "temp.tga")

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
    pytest.warns(UserWarning, lambda: im.save(out, id_section=id_section))
    with Image.open(out) as test_im:
        assert test_im.info["id_section"] == id_section[:255]

    test_file = "Tests/images/tga_id_field.tga"
    with Image.open(test_file) as im:

        # Save with no id section
        im.save(out, id_section="")
    with Image.open(out) as test_im:
        assert "id_section" not in test_im.info


def test_save_orientation(tmp_path):
    test_file = "Tests/images/rgb32rle.tga"
    out = str(tmp_path / "temp.tga")
    with Image.open(test_file) as im:
        assert im.info["orientation"] == -1

        im.save(out, orientation=1)
    with Image.open(out) as test_im:
        assert test_im.info["orientation"] == 1


def test_save_rle(tmp_path):
    test_file = "Tests/images/rgb32rle.tga"
    with Image.open(test_file) as im:
        assert im.info["compression"] == "tga_rle"

        out = str(tmp_path / "temp.tga")

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


def test_save_l_transparency(tmp_path):
    # There are 559 transparent pixels in la.tga.
    num_transparent = 559

    in_file = "Tests/images/la.tga"
    with Image.open(in_file) as im:
        assert im.mode == "LA"
        assert im.getchannel("A").getcolors()[0][0] == num_transparent

        out = str(tmp_path / "temp.tga")
        im.save(out)

    with Image.open(out) as test_im:
        assert test_im.mode == "LA"
        assert test_im.getchannel("A").getcolors()[0][0] == num_transparent

        assert_image_equal(im, test_im)
