from __future__ import annotations

import pytest

from PIL import Image, ImageDraw
from Tests.helper import assert_image_equal_tofile
from Tests.test_imagedraw import BBOX, POINTS, X0, Y0, H, W

TYPE_CHECKING = False

if TYPE_CHECKING:
    from PIL._typing import Coords

I16_MODES = ("I;16", "I;16L", "I;16B", "I;16N")
I16_INK = 0x1234


def create_I16_image_draw(mode: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new(mode, (8, 8))
    return img, ImageDraw.Draw(img)


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


@pytest.mark.parametrize("mode", I16_MODES)
def test_point_I16(mode: str) -> None:
    img, draw = create_I16_image_draw(mode)
    draw.point((4, 4), fill=I16_INK)
    assert img.getpixel((4, 4)) == I16_INK


@pytest.mark.parametrize("mode", I16_MODES)
def test_horizontal_line_I16(mode: str) -> None:
    img, draw = create_I16_image_draw(mode)
    draw.line((0, 4, 7, 4), fill=I16_INK)
    assert img.getpixel((4, 4)) == I16_INK


@pytest.mark.parametrize("mode", I16_MODES)
def test_vertical_line_I16(mode: str) -> None:
    img, draw = create_I16_image_draw(mode)
    draw.line((4, 0, 4, 7), fill=I16_INK)
    assert img.getpixel((4, 4)) == I16_INK


@pytest.mark.parametrize("mode", I16_MODES)
def test_diagonal_line_I16(mode: str) -> None:
    img, draw = create_I16_image_draw(mode)
    draw.line((0, 0, 7, 7), fill=I16_INK)
    assert img.getpixel((4, 4)) == I16_INK


@pytest.mark.parametrize("mode", I16_MODES)
def test_rectangle_fill_I16(mode: str) -> None:
    img, draw = create_I16_image_draw(mode)
    draw.rectangle((0, 0, 7, 7), fill=I16_INK)
    assert img.getpixel((4, 4)) == I16_INK


@pytest.mark.parametrize("mode", I16_MODES)
def test_polygon_I16(mode: str) -> None:
    img, draw = create_I16_image_draw(mode)
    draw.polygon([(0, 0), (7, 0), (7, 7), (0, 7)], fill=I16_INK)
    assert img.getpixel((4, 4)) == I16_INK


@pytest.mark.parametrize("mode", I16_MODES)
def test_masked_polygon_I16(mode: str) -> None:
    # A polygon outline wider than one pixel is drawn through a mask.
    img, draw = create_I16_image_draw(mode)
    draw.polygon([(0, 0), (7, 0), (7, 7), (0, 7)], outline=I16_INK, width=8)
    assert img.getpixel((4, 4)) == I16_INK


@pytest.mark.parametrize("mode", I16_MODES)
def test_ellipse_I16(mode: str) -> None:
    img, draw = create_I16_image_draw(mode)
    draw.ellipse((0, 0, 7, 7), fill=I16_INK)
    assert img.getpixel((4, 4)) == I16_INK
