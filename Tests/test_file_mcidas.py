import pytest

from PIL import Image, McIdasImagePlugin

from .helper import assert_image_equal_tofile


def test_invalid_file():
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        McIdasImagePlugin.McIdasImageFile(invalid_file)


def test_valid_file():
    # Arrange
    # https://ghrc.nsstc.nasa.gov/hydro/details/cmx3g8
    # https://ghrc.nsstc.nasa.gov/pub/fieldCampaigns/camex3/cmx3g8/browse/
    test_file = "Tests/images/cmx3g8_wv_1998.260_0745_mcidas.ara"
    saved_file = "Tests/images/cmx3g8_wv_1998.260_0745_mcidas.png"

    # Act
    with Image.open(test_file) as im:
        im.load()

        # Assert
        assert im.format == "MCIDAS"
        assert im.mode == "I"
        assert im.size == (1800, 400)
        assert_image_equal_tofile(im, saved_file)
