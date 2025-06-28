from __future__ import annotations

import os.path
from collections.abc import Sequence
from typing import Callable

import pytest

from PIL import Image, ImageColor, ImageDraw, ImageFont, features
from PIL._typing import Coords

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar_tofile,
    hopper,
    skip_unless_feature,
)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (190, 190, 190)
DEFAULT_MODE = "RGB"
IMAGES_PATH = os.path.join("Tests", "images", "imagedraw")

# Image size
W, H = 100, 100

# Bounding box points
X0 = int(W / 4)
X1 = int(X0 * 3)
Y0 = int(H / 4)
Y1 = int(X0 * 3)

# Bounding boxes
BBOX = (((X0, Y0), (X1, Y1)), [(X0, Y0), (X1, Y1)], (X0, Y0, X1, Y1), [X0, Y0, X1, Y1])

# Coordinate sequences
POINTS = (
    ((10, 10), (20, 40), (30, 30)),
    [(10, 10), (20, 40), (30, 30)],
    ([10, 10], [20, 40], [30, 30]),
    [[10, 10], [20, 40], [30, 30]],
    (10, 10, 20, 40, 30, 30),
    [10, 10, 20, 40, 30, 30],
)

KITE_POINTS = (
    ((10, 50), (70, 10), (90, 50), (70, 90), (10, 50)),
    [(10, 50), (70, 10), (90, 50), (70, 90), (10, 50)],
    ([10, 50], [70, 10], [90, 50], [70, 90], [10, 50]),
    [[10, 50], [70, 10], [90, 50], [70, 90], [10, 50]],
)


def test_sanity() -> None:
    im = hopper("RGB").copy()

    draw = ImageDraw.ImageDraw(im)
    draw = ImageDraw.Draw(im)

    draw.ellipse(list(range(4)))
    draw.line(list(range(10)))
    draw.polygon(list(range(100)))
    draw.rectangle(list(range(4)))


def test_valueerror() -> None:
    with Image.open("Tests/images/chi.gif") as im:
        draw = ImageDraw.Draw(im)
        draw.line((0, 0), fill=(0, 0, 0))


def test_mode_mismatch() -> None:
    im = hopper("RGB").copy()

    with pytest.raises(ValueError):
        ImageDraw.ImageDraw(im, mode="L")


@pytest.mark.parametrize("bbox", BBOX)
@pytest.mark.parametrize("start, end", ((0, 180), (0.5, 180.4)))
def test_arc(bbox: Coords, start: float, end: float) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.arc(bbox, start, end)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_arc.png", 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_arc_end_le_start(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    start = 270.5
    end = 0

    # Act
    draw.arc(bbox, start=start, end=end)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_arc_end_le_start.png")


@pytest.mark.parametrize("bbox", BBOX)
def test_arc_no_loops(bbox: Coords) -> None:
    # No need to go in loops
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    start = 5
    end = 370

    # Act
    draw.arc(bbox, start=start, end=end)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_arc_no_loops.png", 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_arc_width(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.arc(bbox, 10, 260, width=5)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_arc_width.png", 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_arc_width_pieslice_large(bbox: Coords) -> None:
    # Tests an arc with a large enough width that it is a pieslice
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.arc(bbox, 10, 260, fill="yellow", width=100)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_arc_width_pieslice.png", 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_arc_width_fill(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.arc(bbox, 10, 260, fill="yellow", width=5)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_arc_width_fill.png", 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_arc_width_non_whole_angle(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    expected = "Tests/images/imagedraw_arc_width_non_whole_angle.png"

    # Act
    draw.arc(bbox, 10, 259.5, width=5)

    # Assert
    assert_image_similar_tofile(im, expected, 1)


def test_arc_high() -> None:
    # Arrange
    im = Image.new("RGB", (200, 200))
    draw = ImageDraw.Draw(im)

    # Act
    draw.arc([10, 10, 89, 189], 20, 330, width=20, fill="white")
    draw.arc([110, 10, 189, 189], 20, 150, width=20, fill="white")

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_arc_high.png")


def test_bitmap() -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    with Image.open("Tests/images/pil123rgba.png") as small:
        small = small.resize((50, 50), Image.Resampling.NEAREST)

        # Act
        draw.bitmap((10, 10), small)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_bitmap.png")


@pytest.mark.parametrize("mode", ("RGB", "L"))
@pytest.mark.parametrize("bbox", BBOX)
def test_chord(mode: str, bbox: Coords) -> None:
    # Arrange
    im = Image.new(mode, (W, H))
    draw = ImageDraw.Draw(im)
    expected = f"Tests/images/imagedraw_chord_{mode}.png"

    # Act
    draw.chord(bbox, 0, 180, fill="red", outline="yellow")

    # Assert
    assert_image_similar_tofile(im, expected, 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_chord_width(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.chord(bbox, 10, 260, outline="yellow", width=5)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_chord_width.png", 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_chord_width_fill(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.chord(bbox, 10, 260, fill="red", outline="yellow", width=5)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_chord_width_fill.png", 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_chord_zero_width(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.chord(bbox, 10, 260, fill="red", outline="yellow", width=0)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_chord_zero_width.png")


def test_chord_too_fat() -> None:
    # Arrange
    im = Image.new("RGB", (100, 100))
    draw = ImageDraw.Draw(im)

    # Act
    draw.chord([-150, -150, 99, 99], 15, 60, width=10, fill="white", outline="red")

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_chord_too_fat.png")


@pytest.mark.parametrize("mode", ("RGB", "L"))
@pytest.mark.parametrize("xy", ((W / 2, H / 2), [W / 2, H / 2]))
def test_circle(mode: str, xy: Sequence[float]) -> None:
    # Arrange
    im = Image.new(mode, (W, H))
    draw = ImageDraw.Draw(im)
    expected = f"Tests/images/imagedraw_ellipse_{mode}.png"

    # Act
    draw.circle(xy, 25, fill="green", outline="blue")

    # Assert
    assert_image_similar_tofile(im, expected, 1)


@pytest.mark.parametrize("mode", ("RGB", "L"))
@pytest.mark.parametrize("bbox", BBOX)
def test_ellipse(mode: str, bbox: Coords) -> None:
    # Arrange
    im = Image.new(mode, (W, H))
    draw = ImageDraw.Draw(im)
    expected = f"Tests/images/imagedraw_ellipse_{mode}.png"

    # Act
    draw.ellipse(bbox, fill="green", outline="blue")

    # Assert
    assert_image_similar_tofile(im, expected, 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_ellipse_translucent(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im, "RGBA")

    # Act
    draw.ellipse(bbox, fill=(0, 255, 0, 127))

    # Assert
    expected = "Tests/images/imagedraw_ellipse_translucent.png"
    assert_image_similar_tofile(im, expected, 1)


def test_ellipse_edge() -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.ellipse(((0, 0), (W - 1, H - 1)), fill="white")

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_ellipse_edge.png", 1)


def test_ellipse_symmetric() -> None:
    for width, bbox in (
        (100, (24, 24, 75, 75)),
        (101, (25, 25, 75, 75)),
    ):
        im = Image.new("RGB", (width, 100))
        draw = ImageDraw.Draw(im)
        draw.ellipse(bbox, fill="green", outline="blue")
        assert_image_equal(im, im.transpose(Image.Transpose.FLIP_LEFT_RIGHT))


@pytest.mark.parametrize("bbox", BBOX)
def test_ellipse_width(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.ellipse(bbox, outline="blue", width=5)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_ellipse_width.png", 1)


def test_ellipse_width_large() -> None:
    # Arrange
    im = Image.new("RGB", (500, 500))
    draw = ImageDraw.Draw(im)

    # Act
    draw.ellipse((25, 25, 475, 475), outline="blue", width=75)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_ellipse_width_large.png", 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_ellipse_width_fill(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.ellipse(bbox, fill="green", outline="blue", width=5)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_ellipse_width_fill.png", 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_ellipse_zero_width(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.ellipse(bbox, fill="green", outline="blue", width=0)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_ellipse_zero_width.png")


def ellipse_various_sizes_helper(filled: bool) -> Image.Image:
    ellipse_sizes = range(32)
    image_size = sum(ellipse_sizes) + len(ellipse_sizes) + 1
    im = Image.new("RGB", (image_size, image_size))
    draw = ImageDraw.Draw(im)

    x = 1
    for w in ellipse_sizes:
        y = 1
        for h in ellipse_sizes:
            x1 = x + w
            if w:
                x1 -= 1
            y1 = y + h
            if h:
                y1 -= 1
            border = [x, y, x1, y1]
            if filled:
                draw.ellipse(border, fill="white")
            else:
                draw.ellipse(border, outline="white")
            y += h + 1
        x += w + 1

    return im


def test_ellipse_various_sizes() -> None:
    im = ellipse_various_sizes_helper(False)

    assert_image_equal_tofile(im, "Tests/images/imagedraw_ellipse_various_sizes.png")


def test_ellipse_various_sizes_filled() -> None:
    im = ellipse_various_sizes_helper(True)

    assert_image_equal_tofile(
        im, "Tests/images/imagedraw_ellipse_various_sizes_filled.png"
    )


@pytest.mark.parametrize("points", POINTS)
def test_line(points: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.line(points, fill="yellow", width=2)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_line.png")


def test_shape1() -> None:
    # Arrange
    im = Image.new("RGB", (100, 100), "white")
    draw = ImageDraw.Draw(im)
    x0, y0 = 5, 5
    x1, y1 = 5, 50
    x2, y2 = 95, 50
    x3, y3 = 95, 5

    # Act
    s = ImageDraw.Outline()
    s.move(x0, y0)
    s.curve(x1, y1, x2, y2, x3, y3)
    s.line(x0, y0)

    draw.shape(s, fill=1)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_shape1.png")


def test_shape2() -> None:
    # Arrange
    im = Image.new("RGB", (100, 100), "white")
    draw = ImageDraw.Draw(im)
    x0, y0 = 95, 95
    x1, y1 = 95, 50
    x2, y2 = 5, 50
    x3, y3 = 5, 95

    # Act
    s = ImageDraw.Outline()
    s.move(x0, y0)
    s.curve(x1, y1, x2, y2, x3, y3)
    s.line(x0, y0)

    draw.shape(s, outline="blue")

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_shape2.png")


def test_transform() -> None:
    # Arrange
    im = Image.new("RGB", (100, 100), "white")
    expected = im.copy()
    draw = ImageDraw.Draw(im)

    # Act
    s = ImageDraw.Outline()
    s.line(0, 0)
    s.transform((0, 0, 0, 0, 0, 0))

    draw.shape(s, fill=1)

    # Assert
    assert_image_equal(im, expected)


@pytest.mark.parametrize("bbox", BBOX)
@pytest.mark.parametrize("start, end", ((-92, 46), (-92.2, 46.2)))
def test_pieslice(bbox: Coords, start: float, end: float) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.pieslice(bbox, start, end, fill="white", outline="blue")

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_pieslice.png", 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_pieslice_width(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.pieslice(bbox, 10, 260, outline="blue", width=5)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_pieslice_width.png", 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_pieslice_width_fill(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    expected = "Tests/images/imagedraw_pieslice_width_fill.png"

    # Act
    draw.pieslice(bbox, 10, 260, fill="white", outline="blue", width=5)

    # Assert
    assert_image_similar_tofile(im, expected, 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_pieslice_zero_width(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.pieslice(bbox, 10, 260, fill="white", outline="blue", width=0)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_pieslice_zero_width.png")


def test_pieslice_wide() -> None:
    # Arrange
    im = Image.new("RGB", (200, 100))
    draw = ImageDraw.Draw(im)

    # Act
    draw.pieslice([0, 0, 199, 99], 190, 170, width=10, fill="white", outline="red")

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_pieslice_wide.png")


def test_pieslice_no_spikes() -> None:
    im = Image.new("RGB", (161, 161), "white")
    draw = ImageDraw.Draw(im)
    cxs = (
        [140] * 3
        + list(range(140, 19, -20))
        + [20] * 5
        + list(range(20, 141, 20))
        + [140] * 2
    )
    cys = (
        list(range(80, 141, 20))
        + [140] * 5
        + list(range(140, 19, -20))
        + [20] * 5
        + list(range(20, 80, 20))
    )

    for cx, cy, angle in zip(cxs, cys, range(0, 360, 15)):
        draw.pieslice(
            [cx - 100, cy - 100, cx + 100, cy + 100], angle, angle + 1, fill="black"
        )
        draw.point([cx, cy], fill="red")

    im_pre_erase = im.copy()
    draw.rectangle([21, 21, 139, 139], fill="white")

    assert_image_equal(im, im_pre_erase)


@pytest.mark.parametrize("points", POINTS)
def test_point(points: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.point(points, fill="yellow")

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_point.png")


def test_point_I16() -> None:
    # Arrange
    im = Image.new("I;16", (1, 1))
    draw = ImageDraw.Draw(im)

    # Act
    draw.point((0, 0), fill=0x1234)

    # Assert
    assert im.getpixel((0, 0)) == 0x1234


@pytest.mark.parametrize("points", POINTS)
def test_polygon(points: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.polygon(points, fill="red", outline="blue")

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_polygon.png")


@pytest.mark.parametrize("points", POINTS)
def test_polygon_width_I16(points: Coords) -> None:
    # Arrange
    im = Image.new("I;16", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.polygon(points, outline=0xFFFF, width=2)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_polygon_width_I.tiff")


@pytest.mark.parametrize("mode", ("RGB", "L"))
@pytest.mark.parametrize("kite_points", KITE_POINTS)
def test_polygon_kite(
    mode: str, kite_points: tuple[tuple[int, int], ...] | list[tuple[int, int]]
) -> None:
    # Test drawing lines of different gradients (dx>dy, dy>dx) and
    # vertical (dx==0) and horizontal (dy==0) lines
    # Arrange
    im = Image.new(mode, (W, H))
    draw = ImageDraw.Draw(im)
    expected = f"Tests/images/imagedraw_polygon_kite_{mode}.png"

    # Act
    draw.polygon(kite_points, fill="blue", outline="yellow")

    # Assert
    assert_image_equal_tofile(im, expected)


def test_polygon_1px_high() -> None:
    # Test drawing a 1px high polygon
    # Arrange
    im = Image.new("RGB", (3, 3))
    draw = ImageDraw.Draw(im)
    expected = "Tests/images/imagedraw_polygon_1px_high.png"

    # Act
    draw.polygon([(0, 1), (0, 1), (2, 1), (2, 1)], "#f00")

    # Assert
    assert_image_equal_tofile(im, expected)


def test_polygon_1px_high_translucent() -> None:
    # Test drawing a translucent 1px high polygon
    # Arrange
    im = Image.new("RGB", (4, 3))
    draw = ImageDraw.Draw(im, "RGBA")
    expected = "Tests/images/imagedraw_polygon_1px_high_translucent.png"

    # Act
    draw.polygon([(1, 1), (1, 1), (3, 1), (3, 1)], (255, 0, 0, 127))

    # Assert
    assert_image_equal_tofile(im, expected)


def test_polygon_translucent() -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im, "RGBA")

    # Act
    draw.polygon([(20, 80), (80, 80), (80, 20)], fill=(0, 255, 0, 127))

    # Assert
    expected = "Tests/images/imagedraw_polygon_translucent.png"
    assert_image_equal_tofile(im, expected)


@pytest.mark.parametrize("bbox", BBOX)
def test_rectangle(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.rectangle(bbox, fill="black", outline="green")

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_rectangle.png")


def test_big_rectangle() -> None:
    # Test drawing a rectangle bigger than the image
    # Arrange
    im = Image.new("RGB", (W, H))
    bbox = [(-1, -1), (W + 1, H + 1)]
    draw = ImageDraw.Draw(im)

    # Act
    draw.rectangle(bbox, fill="orange")

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_big_rectangle.png", 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_rectangle_width(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    expected = "Tests/images/imagedraw_rectangle_width.png"

    # Act
    draw.rectangle(bbox, outline="green", width=5)

    # Assert
    assert_image_equal_tofile(im, expected)


@pytest.mark.parametrize("bbox", BBOX)
def test_rectangle_width_fill(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    expected = "Tests/images/imagedraw_rectangle_width_fill.png"

    # Act
    draw.rectangle(bbox, fill="blue", outline="green", width=5)

    # Assert
    assert_image_equal_tofile(im, expected)


@pytest.mark.parametrize("bbox", BBOX)
def test_rectangle_zero_width(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.rectangle(bbox, fill="blue", outline="green", width=0)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_rectangle_zero_width.png")


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


@pytest.mark.parametrize("bbox", BBOX)
def test_rectangle_translucent_outline(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im, "RGBA")

    # Act
    draw.rectangle(bbox, fill="black", outline=(0, 255, 0, 127), width=5)

    # Assert
    assert_image_equal_tofile(
        im, "Tests/images/imagedraw_rectangle_translucent_outline.png"
    )


@pytest.mark.parametrize(
    "xy",
    [(10, 20, 190, 180), ([10, 20], [190, 180]), ((10, 20), (190, 180))],
)
def test_rounded_rectangle(
    xy: (
        tuple[int, int, int, int]
        | tuple[list[int]]
        | tuple[tuple[int, int], tuple[int, int]]
    ),
) -> None:
    # Arrange
    im = Image.new("RGB", (200, 200))
    draw = ImageDraw.Draw(im)

    # Act
    draw.rounded_rectangle(xy, 30, fill="red", outline="green", width=5)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_rounded_rectangle.png")


@pytest.mark.parametrize("top_left", (True, False))
@pytest.mark.parametrize("top_right", (True, False))
@pytest.mark.parametrize("bottom_right", (True, False))
@pytest.mark.parametrize("bottom_left", (True, False))
def test_rounded_rectangle_corners(
    top_left: bool, top_right: bool, bottom_right: bool, bottom_left: bool
) -> None:
    corners = (top_left, top_right, bottom_right, bottom_left)

    # Arrange
    im = Image.new("RGB", (200, 200))
    draw = ImageDraw.Draw(im)

    # Act
    draw.rounded_rectangle(
        (10, 20, 190, 180), 30, fill="red", outline="green", width=5, corners=corners
    )

    # Assert
    suffix = "".join(
        (
            ("y" if top_left else "n"),
            ("y" if top_right else "n"),
            ("y" if bottom_right else "n"),
            ("y" if bottom_left else "n"),
        )
    )
    assert_image_equal_tofile(
        im, "Tests/images/imagedraw_rounded_rectangle_corners_" + suffix + ".png"
    )


def test_rounded_rectangle_joined_x_different_corners() -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im, "RGBA")

    # Act
    draw.rounded_rectangle(
        (20, 10, 80, 90),
        30,
        fill="red",
        outline="green",
        width=5,
        corners=(True, False, False, False),
    )

    # Assert
    assert_image_equal_tofile(
        im, "Tests/images/imagedraw_rounded_rectangle_joined_x_different_corners.png"
    )


@pytest.mark.parametrize(
    "xy, radius, type",
    [
        ((10, 20, 190, 180), 30.5, "given"),
        ((10, 10, 181, 190), 90, "width"),
        ((10, 20, 190, 181), 85, "height"),
    ],
)
def test_rounded_rectangle_non_integer_radius(
    xy: tuple[int, int, int, int], radius: float, type: str
) -> None:
    # Arrange
    im = Image.new("RGB", (200, 200))
    draw = ImageDraw.Draw(im)

    # Act
    draw.rounded_rectangle(xy, radius, fill="red", outline="green", width=5)

    # Assert
    assert_image_equal_tofile(
        im,
        "Tests/images/imagedraw_rounded_rectangle_non_integer_radius_" + type + ".png",
    )


@pytest.mark.parametrize("bbox", BBOX)
def test_rounded_rectangle_zero_radius(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.rounded_rectangle(bbox, 0, fill="blue", outline="green", width=5)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_rectangle_width_fill.png")


@pytest.mark.parametrize(
    "xy, suffix",
    [
        ((20, 10, 80, 90), "x"),
        ((20, 10, 81, 90), "x_odd"),
        ((20, 10, 81.1, 90), "x_odd"),
        ((10, 20, 90, 80), "y"),
        ((10, 20, 90, 81), "y_odd"),
        ((10, 20, 90, 81.1), "y_odd"),
        ((20, 20, 80, 80), "both"),
    ],
)
def test_rounded_rectangle_translucent(
    xy: tuple[int, int, int, int], suffix: str
) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im, "RGBA")

    # Act
    draw.rounded_rectangle(
        xy, 30, fill=(255, 0, 0, 127), outline=(0, 255, 0, 127), width=5
    )

    # Assert
    assert_image_equal_tofile(
        im, "Tests/images/imagedraw_rounded_rectangle_" + suffix + ".png"
    )


@pytest.mark.parametrize("bbox", BBOX)
def test_floodfill(bbox: Coords) -> None:
    red = ImageColor.getrgb("red")

    mode_values: list[tuple[str, int | tuple[int, ...]]] = [
        ("L", 1),
        ("RGBA", (255, 0, 0, 0)),
        ("RGB", red),
    ]
    for mode, value in mode_values:
        # Arrange
        im = Image.new(mode, (W, H))
        draw = ImageDraw.Draw(im)
        draw.rectangle(bbox, outline="yellow", fill="green")
        centre_point = (int(W / 2), int(H / 2))

        # Act
        ImageDraw.floodfill(im, centre_point, value)

        # Assert
        expected = "Tests/images/imagedraw_floodfill_" + mode + ".png"
        with Image.open(expected) as im_floodfill:
            assert_image_equal(im, im_floodfill)

    # Test that using the same colour does not change the image
    ImageDraw.floodfill(im, centre_point, red)
    assert_image_equal(im, im_floodfill)

    # Test that filling outside the image does not change the image
    ImageDraw.floodfill(im, (W, H), red)
    assert_image_equal(im, im_floodfill)

    # Test filling at the edge of an image
    im = Image.new("RGB", (1, 1))
    ImageDraw.floodfill(im, (0, 0), red)
    assert_image_equal(im, Image.new("RGB", (1, 1), red))


@pytest.mark.parametrize("bbox", BBOX)
def test_floodfill_border(bbox: Coords) -> None:
    # floodfill() is experimental

    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    draw.rectangle(bbox, outline="yellow", fill="green")
    centre_point = (int(W / 2), int(H / 2))

    # Act
    ImageDraw.floodfill(
        im,
        centre_point,
        ImageColor.getrgb("red"),
        border=ImageColor.getrgb("black"),
    )

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_floodfill2.png")


@pytest.mark.parametrize("bbox", BBOX)
def test_floodfill_thresh(bbox: Coords) -> None:
    # floodfill() is experimental

    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    draw.rectangle(bbox, outline="darkgreen", fill="green")
    centre_point = (int(W / 2), int(H / 2))

    # Act
    ImageDraw.floodfill(im, centre_point, ImageColor.getrgb("red"), thresh=30)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_floodfill2.png")


def test_floodfill_not_negative() -> None:
    # floodfill() is experimental
    # Test that floodfill does not extend into negative coordinates

    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    draw.line((W / 2, 0, W / 2, H / 2), fill="green")
    draw.line((0, H / 2, W / 2, H / 2), fill="green")

    # Act
    ImageDraw.floodfill(im, (int(W / 4), int(H / 4)), ImageColor.getrgb("red"))

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_floodfill_not_negative.png")


def create_base_image_draw(
    size: tuple[int, int],
    mode: str = DEFAULT_MODE,
    background1: tuple[int, int, int] = WHITE,
    background2: tuple[int, int, int] = GRAY,
) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new(mode, size, background1)
    for x in range(size[0]):
        for y in range(size[1]):
            if (x + y) % 2 == 0:
                img.putpixel((x, y), background2)
    return img, ImageDraw.Draw(img)


def test_square() -> None:
    expected = os.path.join(IMAGES_PATH, "square.png")
    img, draw = create_base_image_draw((10, 10))
    draw.polygon([(2, 2), (2, 7), (7, 7), (7, 2)], BLACK)
    assert_image_equal_tofile(img, expected, "square as normal polygon failed")
    img, draw = create_base_image_draw((10, 10))
    draw.polygon([(7, 7), (7, 2), (2, 2), (2, 7)], BLACK)
    assert_image_equal_tofile(img, expected, "square as inverted polygon failed")
    img, draw = create_base_image_draw((10, 10))
    draw.rectangle((2, 2, 7, 7), BLACK)
    assert_image_equal_tofile(img, expected, "square as normal rectangle failed")


def test_triangle_right() -> None:
    img, draw = create_base_image_draw((20, 20))
    draw.polygon([(3, 5), (17, 5), (10, 12)], BLACK)
    assert_image_equal_tofile(
        img, os.path.join(IMAGES_PATH, "triangle_right.png"), "triangle right failed"
    )


@pytest.mark.parametrize(
    "fill, suffix",
    ((BLACK, "width"), (None, "width_no_fill")),
)
def test_triangle_right_width(fill: tuple[int, int, int] | None, suffix: str) -> None:
    img, draw = create_base_image_draw((100, 100))
    draw.polygon([(15, 25), (85, 25), (50, 60)], fill, WHITE, width=5)
    assert_image_equal_tofile(
        img, os.path.join(IMAGES_PATH, "triangle_right_" + suffix + ".png")
    )


def test_line_horizontal() -> None:
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 5, 14, 5), BLACK, 2)
    assert_image_equal_tofile(
        img,
        os.path.join(IMAGES_PATH, "line_horizontal_w2px_normal.png"),
        "line straight horizontal normal 2px wide failed",
    )

    img, draw = create_base_image_draw((20, 20))
    draw.line((14, 5, 5, 5), BLACK, 2)
    assert_image_equal_tofile(
        img,
        os.path.join(IMAGES_PATH, "line_horizontal_w2px_inverted.png"),
        "line straight horizontal inverted 2px wide failed",
    )

    expected = os.path.join(IMAGES_PATH, "line_horizontal_w3px.png")
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 5, 14, 5), BLACK, 3)
    assert_image_equal_tofile(
        img, expected, "line straight horizontal normal 3px wide failed"
    )
    img, draw = create_base_image_draw((20, 20))
    draw.line((14, 5, 5, 5), BLACK, 3)
    assert_image_equal_tofile(
        img, expected, "line straight horizontal inverted 3px wide failed"
    )

    img, draw = create_base_image_draw((200, 110))
    draw.line((5, 55, 195, 55), BLACK, 101)
    assert_image_equal_tofile(
        img,
        os.path.join(IMAGES_PATH, "line_horizontal_w101px.png"),
        "line straight horizontal 101px wide failed",
    )


@pytest.mark.xfail(reason="failing test")
def test_line_h_s1_w2() -> None:
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 5, 14, 6), BLACK, 2)
    assert_image_equal_tofile(
        img,
        os.path.join(IMAGES_PATH, "line_horizontal_slope1px_w2px.png"),
        "line horizontal 1px slope 2px wide failed",
    )


def test_line_vertical() -> None:
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 5, 5, 14), BLACK, 2)
    assert_image_equal_tofile(
        img,
        os.path.join(IMAGES_PATH, "line_vertical_w2px_normal.png"),
        "line straight vertical normal 2px wide failed",
    )

    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 14, 5, 5), BLACK, 2)
    assert_image_equal_tofile(
        img,
        os.path.join(IMAGES_PATH, "line_vertical_w2px_inverted.png"),
        "line straight vertical inverted 2px wide failed",
    )

    expected = os.path.join(IMAGES_PATH, "line_vertical_w3px.png")
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 5, 5, 14), BLACK, 3)
    assert_image_equal_tofile(
        img, expected, "line straight vertical normal 3px wide failed"
    )
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 14, 5, 5), BLACK, 3)
    assert_image_equal_tofile(
        img, expected, "line straight vertical inverted 3px wide failed"
    )

    img, draw = create_base_image_draw((110, 200))
    draw.line((55, 5, 55, 195), BLACK, 101)
    assert_image_equal_tofile(
        img,
        os.path.join(IMAGES_PATH, "line_vertical_w101px.png"),
        "line straight vertical 101px wide failed",
    )

    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 5, 6, 14), BLACK, 2)
    assert_image_equal_tofile(
        img,
        os.path.join(IMAGES_PATH, "line_vertical_slope1px_w2px.png"),
        "line vertical 1px slope 2px wide failed",
    )


def test_line_oblique_45() -> None:
    expected = os.path.join(IMAGES_PATH, "line_oblique_45_w3px_a.png")
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 5, 14, 14), BLACK, 3)
    assert_image_equal_tofile(img, expected, "line oblique 45 normal 3px wide A failed")
    img, draw = create_base_image_draw((20, 20))
    draw.line((14, 14, 5, 5), BLACK, 3)
    assert_image_equal_tofile(
        img, expected, "line oblique 45 inverted 3px wide A failed"
    )

    expected = os.path.join(IMAGES_PATH, "line_oblique_45_w3px_b.png")
    img, draw = create_base_image_draw((20, 20))
    draw.line((14, 5, 5, 14), BLACK, 3)
    assert_image_equal_tofile(img, expected, "line oblique 45 normal 3px wide B failed")
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 14, 14, 5), BLACK, 3)
    assert_image_equal_tofile(
        img, expected, "line oblique 45 inverted 3px wide B failed"
    )


def test_wide_line_dot() -> None:
    # Test drawing a wide "line" from one point to another just draws a single point
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.line([(50, 50), (50, 50)], width=3)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_wide_line_dot.png", 1)


def test_wide_line_larger_than_int() -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    expected = "Tests/images/imagedraw_wide_line_larger_than_int.png"

    # Act
    draw.line([(0, 0), (32768, 32768)], width=3)

    # Assert
    assert_image_similar_tofile(im, expected, 1)


@pytest.mark.parametrize(
    "xy",
    [
        [
            (400, 280),
            (380, 280),
            (450, 280),
            (440, 120),
            (350, 200),
            (310, 280),
            (300, 280),
            (250, 280),
            (250, 200),
            (150, 200),
            (150, 260),
            (50, 200),
            (150, 50),
            (250, 100),
        ],
        (
            400,
            280,
            380,
            280,
            450,
            280,
            440,
            120,
            350,
            200,
            310,
            280,
            300,
            280,
            250,
            280,
            250,
            200,
            150,
            200,
            150,
            260,
            50,
            200,
            150,
            50,
            250,
            100,
        ),
        [
            400,
            280,
            380,
            280,
            450,
            280,
            440,
            120,
            350,
            200,
            310,
            280,
            300,
            280,
            250,
            280,
            250,
            200,
            150,
            200,
            150,
            260,
            50,
            200,
            150,
            50,
            250,
            100,
        ],
    ],
)
def test_line_joint(xy: list[tuple[int, int]] | tuple[int, ...] | list[int]) -> None:
    im = Image.new("RGB", (500, 325))
    draw = ImageDraw.Draw(im)

    # Act
    draw.line(xy, GRAY, 50, "curve")

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_line_joint_curve.png", 3)


def test_textsize_empty_string() -> None:
    # https://github.com/python-pillow/Pillow/issues/2783
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    # Should not cause 'SystemError: <built-in method getsize of
    # ImagingFont object at 0x...> returned NULL without setting an error'
    draw.textbbox((0, 0), "")
    draw.textbbox((0, 0), "\n")
    draw.textbbox((0, 0), "test\n")
    draw.textlength("")


@skip_unless_feature("freetype2")
def test_textbbox_stroke() -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 20)

    # Act / Assert
    assert draw.textbbox((2, 2), "A", font, stroke_width=2) == (0, 4, 16, 20)
    assert draw.textbbox((2, 2), "A", font, stroke_width=4) == (-2, 2, 18, 22)
    assert draw.textbbox((2, 2), "ABC\nAaaa", font, stroke_width=2) == (0, 4, 52, 44)
    assert draw.textbbox((2, 2), "ABC\nAaaa", font, stroke_width=4) == (-2, 2, 54, 50)


@skip_unless_feature("freetype2")
def test_stroke() -> None:
    for suffix, stroke_fill in {"same": None, "different": "#0f0"}.items():
        # Arrange
        im = Image.new("RGB", (120, 130))
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 120)

        # Act
        draw.text((12, 12), "A", "#f00", font, stroke_width=2, stroke_fill=stroke_fill)

        # Assert
        assert_image_similar_tofile(
            im, "Tests/images/imagedraw_stroke_" + suffix + ".png", 3.1
        )


@skip_unless_feature("freetype2")
def test_stroke_float() -> None:
    # Arrange
    im = Image.new("RGB", (120, 130))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 120)

    # Act
    draw.text((12, 12), "A", "#f00", font, stroke_width=0.5)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_stroke_float.png", 3.1)


@skip_unless_feature("freetype2")
def test_stroke_descender() -> None:
    # Arrange
    im = Image.new("RGB", (120, 130))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 120)

    # Act
    draw.text((12, 2), "y", "#f00", font, stroke_width=2, stroke_fill="#0f0")

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_stroke_descender.png", 6.76)


@skip_unless_feature("freetype2")
def test_stroke_inside_gap() -> None:
    # Arrange
    im = Image.new("RGB", (120, 130))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 120)

    # Act
    draw.text((12, 12), "i", "#f00", font, stroke_width=20)

    # Assert
    for y in range(im.height):
        glyph = ""
        for x in range(im.width):
            if im.getpixel((x, y)) == (0, 0, 0):
                if glyph == "started":
                    glyph = "ended"
            else:
                assert glyph != "ended", "Gap inside stroked glyph"
                glyph = "started"


@skip_unless_feature("freetype2")
def test_split_word() -> None:
    # Arrange
    im = Image.new("RGB", (230, 55))
    expected = im.copy()
    expected_draw = ImageDraw.Draw(expected)
    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 48)
    expected_draw.text((0, 0), "paradise", font=font)

    draw = ImageDraw.Draw(im)

    # Act
    draw.text((0, 0), "par", font=font)

    length = draw.textlength("par", font=font)
    draw.text((length, 0), "adise", font=font)

    # Assert
    assert_image_equal(im, expected)


@skip_unless_feature("freetype2")
def test_stroke_multiline() -> None:
    # Arrange
    im = Image.new("RGB", (100, 250))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 120)

    # Act
    draw.multiline_text(
        (12, 12), "A\nB", "#f00", font, stroke_width=2, stroke_fill="#0f0"
    )

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_stroke_multiline.png", 3.3)


@skip_unless_feature("freetype2")
def test_setting_default_font() -> None:
    # Arrange
    im = Image.new("RGB", (100, 250))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 120)

    # Act
    ImageDraw.ImageDraw.font = font

    # Assert
    try:
        assert draw.getfont() == font
    finally:
        ImageDraw.ImageDraw.font = None
        assert isinstance(draw.getfont(), ImageFont.load_default().__class__)


def test_default_font_size() -> None:
    freetype_support = features.check_module("freetype2")
    text = "Default font at a specific size."

    im = Image.new("RGB", (220, 25))
    draw = ImageDraw.Draw(im)

    def check(func: Callable[[], None]) -> None:
        if freetype_support:
            func()
        else:
            with pytest.raises(ImportError):
                func()

    def draw_text() -> None:
        draw.text((0, 0), text, font_size=16)
        assert_image_equal_tofile(im, "Tests/images/imagedraw_default_font_size.png")

    check(draw_text)

    def draw_textlength() -> None:
        assert draw.textlength(text, font_size=16) == 216

    check(draw_textlength)

    def draw_textbbox() -> None:
        assert draw.textbbox((0, 0), text, font_size=16) == (0, 3, 216, 19)

    check(draw_textbbox)

    im = Image.new("RGB", (220, 25))
    draw = ImageDraw.Draw(im)

    def draw_multiline_text() -> None:
        draw.multiline_text((0, 0), text, font_size=16)
        assert_image_equal_tofile(im, "Tests/images/imagedraw_default_font_size.png")

    check(draw_multiline_text)

    def draw_multiline_textbbox() -> None:
        assert draw.multiline_textbbox((0, 0), text, font_size=16) == (0, 3, 216, 19)

    check(draw_multiline_textbbox)


@pytest.mark.parametrize("bbox", BBOX)
def test_same_color_outline(bbox: Coords) -> None:
    # Prepare shape
    x0, y0 = 5, 5
    x1, y1 = 5, 50
    x2, y2 = 95, 50
    x3, y3 = 95, 5

    s = ImageDraw.Outline()
    s.move(x0, y0)
    s.curve(x1, y1, x2, y2, x3, y3)
    s.line(x0, y0)

    # Begin
    for mode in ["RGB", "L"]:
        fill = "red"
        for outline in [None, "red", "#f00"]:
            for operation, args in {
                "chord": [bbox, 0, 180],
                "ellipse": [bbox],
                "shape": [s],
                "pieslice": [bbox, -90, 45],
                "polygon": [[(18, 30), (85, 30), (60, 72)]],
                "rectangle": [bbox],
            }.items():
                # Arrange
                im = Image.new(mode, (W, H))
                draw = ImageDraw.Draw(im)

                # Act
                draw_method = getattr(draw, operation)
                assert isinstance(args, list)
                args += [fill, outline]
                draw_method(*args)

                # Assert
                expected = f"Tests/images/imagedraw_outline_{operation}_{mode}.png"
                assert_image_similar_tofile(im, expected, 1)


@pytest.mark.parametrize(
    "n_sides, polygon_name, args",
    [
        (4, "square", {}),
        (8, "regular_octagon", {}),
        (4, "square_rotate_45", {"rotation": 45}),
        (3, "triangle_width", {"outline": "yellow", "width": 5}),
    ],
)
def test_draw_regular_polygon(
    n_sides: int, polygon_name: str, args: dict[str, int | str]
) -> None:
    im = Image.new("RGBA", size=(W, H), color=(255, 0, 0, 0))
    filename = f"Tests/images/imagedraw_{polygon_name}.png"
    draw = ImageDraw.Draw(im)
    bounding_circle = ((W // 2, H // 2), 25)
    rotation = int(args.get("rotation", 0))
    outline = args.get("outline")
    width = int(args.get("width", 1))
    draw.regular_polygon(bounding_circle, n_sides, rotation, "red", outline, width)
    assert_image_equal_tofile(im, filename)


@pytest.mark.parametrize(
    "n_sides, expected_vertices",
    [
        (3, [(28.35, 62.5), (71.65, 62.5), (50.0, 25.0)]),
        (4, [(32.32, 67.68), (67.68, 67.68), (67.68, 32.32), (32.32, 32.32)]),
        (
            5,
            [
                (35.31, 70.23),
                (64.69, 70.23),
                (73.78, 42.27),
                (50.0, 25.0),
                (26.22, 42.27),
            ],
        ),
        (
            6,
            [
                (37.5, 71.65),
                (62.5, 71.65),
                (75.0, 50.0),
                (62.5, 28.35),
                (37.5, 28.35),
                (25.0, 50.0),
            ],
        ),
    ],
)
def test_compute_regular_polygon_vertices(
    n_sides: int, expected_vertices: list[tuple[float, float]]
) -> None:
    bounding_circle = (W // 2, H // 2, 25)
    vertices = ImageDraw._compute_regular_polygon_vertices(bounding_circle, n_sides, 0)
    assert vertices == expected_vertices


@pytest.mark.parametrize(
    "n_sides, bounding_circle, rotation, expected_error, error_message",
    [
        (None, (50, 50, 25), 0, TypeError, "n_sides should be an int"),
        (1, (50, 50, 25), 0, ValueError, "n_sides should be an int > 2"),
        (3, 50, 0, TypeError, "bounding_circle should be a sequence"),
        (
            3,
            (50, 50, 100, 100),
            0,
            ValueError,
            "bounding_circle should contain 2D coordinates "
            r"and a radius \(e.g. \(x, y, r\) or \(\(x, y\), r\) \)",
        ),
        (
            3,
            (50, 50, "25"),
            0,
            ValueError,
            "bounding_circle should only contain numeric data",
        ),
        (
            3,
            ((50, 50, 50), 25),
            0,
            ValueError,
            r"bounding_circle centre should contain 2D coordinates \(e.g. \(x, y\)\)",
        ),
        (
            3,
            (50, 50, 0),
            0,
            ValueError,
            "bounding_circle radius should be > 0",
        ),
        (
            3,
            (50, 50, 25),
            "0",
            ValueError,
            "rotation should be an int or float",
        ),
    ],
)
def test_compute_regular_polygon_vertices_input_error_handling(
    n_sides: int,
    bounding_circle: int | tuple[int | tuple[int] | str, ...],
    rotation: int | str,
    expected_error: type[Exception],
    error_message: str,
) -> None:
    with pytest.raises(expected_error, match=error_message):
        ImageDraw._compute_regular_polygon_vertices(bounding_circle, n_sides, rotation)  # type: ignore[arg-type]


def test_continuous_horizontal_edges_polygon() -> None:
    xy = [
        (2, 6),
        (6, 6),
        (12, 6),
        (12, 12),
        (8, 12),
        (8, 8),
        (4, 8),
        (2, 8),
    ]
    img, draw = create_base_image_draw((16, 16))
    draw.polygon(xy, BLACK)
    expected = os.path.join(IMAGES_PATH, "continuous_horizontal_edges_polygon.png")
    assert_image_equal_tofile(
        img, expected, "continuous horizontal edges polygon failed"
    )


def test_discontiguous_corners_polygon() -> None:
    img, draw = create_base_image_draw((84, 68))
    draw.polygon(((1, 21), (34, 4), (71, 1), (38, 18)), BLACK)
    draw.polygon(
        ((82, 29), (82, 26), (82, 24), (67, 22), (52, 29), (52, 15), (67, 22)), BLACK
    )
    draw.polygon(((71, 44), (38, 27), (1, 24)), BLACK)
    draw.polygon(
        ((38, 66), (5, 49), (77, 49), (47, 66), (82, 63), (82, 47), (1, 47), (1, 63)),
        BLACK,
    )
    expected = os.path.join(IMAGES_PATH, "discontiguous_corners_polygon.png")
    assert_image_equal_tofile(img, expected)


def test_polygon2() -> None:
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    draw.polygon([(18, 30), (19, 31), (18, 30), (85, 30), (60, 72)], "red")
    expected = "Tests/images/imagedraw_outline_polygon_RGB.png"
    assert_image_similar_tofile(im, expected, 1)


@pytest.mark.parametrize("xy", ((1, 1, 0, 1), (1, 1, 1, 0)))
def test_incorrectly_ordered_coordinates(xy: tuple[int, int, int, int]) -> None:
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    with pytest.raises(ValueError):
        draw.arc(xy, 10, 260)
    with pytest.raises(ValueError):
        draw.chord(xy, 10, 260)
    with pytest.raises(ValueError):
        draw.ellipse(xy)
    with pytest.raises(ValueError):
        draw.pieslice(xy, 10, 260)
    with pytest.raises(ValueError):
        draw.rectangle(xy)
    with pytest.raises(ValueError):
        draw.rounded_rectangle(xy)


def test_getdraw() -> None:
    with pytest.warns(DeprecationWarning, match="'hints' parameter"):
        ImageDraw.getdraw(None, [])
