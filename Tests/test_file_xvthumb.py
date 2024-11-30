from __future__ import annotations

import pytest

from PIL import Image, XVThumbImagePlugin

from .helper import assert_image_similar, hopper

TEST_FILE = "Tests/images/hopper.p7"


def test_open() -> None:
    # Act
    with Image.open(TEST_FILE) as im:
        # Assert
        assert im.format == "XVThumb"

        # Create a Hopper image with a similar XV palette
        im_hopper = hopper().quantize(palette=im)
        assert_image_similar(im, im_hopper, 9)


def test_unexpected_eof() -> None:
    # Test unexpected EOF reading XV thumbnail file
    # Arrange
    bad_file = "Tests/images/hopper_bad.p7"

    # Act / Assert
    with pytest.raises(SyntaxError):
        XVThumbImagePlugin.XVThumbImageFile(bad_file)


def test_invalid_file() -> None:
    # Arrange
    invalid_file = "Tests/images/flower.jpg"

    # Act / Assert
    with pytest.raises(SyntaxError):
        XVThumbImagePlugin.XVThumbImageFile(invalid_file)
