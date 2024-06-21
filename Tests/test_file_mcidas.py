from __future__ import annotations

import pytest

from PIL import Image, McIdasImagePlugin

from .helper import assert_image_equal_tofile

def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        McIdasImagePlugin.McIdasImageFile(invalid_file)


def test_valid_file() -> None:
    # Arrange
    # https://ghrc.nsstc.nasa.gov/hydro/details/cmx3g8
    # https://ghrc.nsstc.nasa.gov/pub/fieldCampaigns/camex3/cmx3g8/browse/
    test_file = "Tests/images/cmx3g8_wv_1998.260_0745_mcidas.ara"
    saved_file = "Tests/images/cmx3g8_wv_1998.260_0745_mcidas.tiff"

    # Act
    with Image.open(test_file) as im:
        im.load()

        # Assert
        assert im.format == "MCIDAS"
        assert im.mode == "I"
        assert im.size == (1800, 400)
        assert_image_equal_tofile(im, saved_file)


def test_open_invalid_file() -> None:
    invalid_file = "Tests/images/drawing_wmf_ref_144.png"

    with pytest.raises(SyntaxError):
        McIdasImagePlugin.McIdasImageFile(invalid_file)


def test_open_8bit_file() -> None:
    test_file = "Tests/images/l_trns.png"

    with Image.open(test_file) as im:
        im.load()

        assert im.format == "MCIDAS"
        assert im.mode == "L"
        assert im.size == (800, 600)


def test_open_16bit_file() -> None:
    test_file = "Tests/images/rgb_trns.png"

    with Image.open(test_file) as im:
        im.load()

        assert im.format == "MCIDAS"
        assert im.mode == "I"
        assert im.size == (1024, 768)


def test_open_32bit_file() -> None:
    test_file = "Tests/images/tga/common/200x32_la.png"

    with Image.open(test_file) as im:
        im.load()

        assert im.format == "MCIDAS"
        assert im.mode == "I"
        assert im.size == (1280, 1024)


def test_open_unsupported_format() -> None:
    test_file = "Tests/images/exif_text.png"

    with pytest.raises(SyntaxError):
        McIdasImagePlugin.McIdasImageFile(test_file)

