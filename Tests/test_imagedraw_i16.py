from __future__ import annotations

import pytest

from PIL import Image, ImageDraw
from Tests.helper import assert_image_equal_tofile
from Tests.test_imagedraw import BBOX, POINTS, X0, Y0, H, W

TYPE_CHECKING = False

if TYPE_CHECKING:
    from PIL._typing import Coords


def test_point_I16() -> None:
    # Arrange
    im = Image.new("I;16", (1, 1))
    draw = ImageDraw.Draw(im)

    # Act
    draw.point((0, 0), fill=0x1234)

    # Assert
    assert im.getpixel((0, 0)) == 0x1234


@pytest.mark.parametrize("points", POINTS)
def test_polygon_width_I16(points: Coords) -> None:
    # Arrange
    im = Image.new("I;16", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.polygon(points, outline=0xFFFF, width=2)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_polygon_width_I.tiff")


@pytest.mark.parametrize("bbox", BBOX)
def test_rectangle_I16(bbox: Coords) -> None:
    # Arrange
    im = Image.new("I;16", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.rectangle(bbox, outline=0xCDEF)

    # Assert
    assert im.getpixel((X0, Y0)) == 0xCDEF
    assert_image_equal_tofile(im, "Tests/images/imagedraw_rectangle_I.tiff")
