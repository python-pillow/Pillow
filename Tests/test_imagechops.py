from PIL import Image, ImageChops

from .helper import assert_image_equal, hopper

BLACK = (0, 0, 0)
BROWN = (127, 64, 0)
CYAN = (0, 255, 255)
DARK_GREEN = (0, 128, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 128, 0)
WHITE = (255, 255, 255)

GREY = 128


def test_sanity():
    im = hopper("L")

    ImageChops.constant(im, 128)
    ImageChops.duplicate(im)
    ImageChops.invert(im)
    ImageChops.lighter(im, im)
    ImageChops.darker(im, im)
    ImageChops.difference(im, im)
    ImageChops.multiply(im, im)
    ImageChops.screen(im, im)

    ImageChops.add(im, im)
    ImageChops.add(im, im, 2.0)
    ImageChops.add(im, im, 2.0, 128)
    ImageChops.subtract(im, im)
    ImageChops.subtract(im, im, 2.0)
    ImageChops.subtract(im, im, 2.0, 128)

    ImageChops.add_modulo(im, im)
    ImageChops.subtract_modulo(im, im)

    ImageChops.blend(im, im, 0.5)
    ImageChops.composite(im, im, im)

    ImageChops.soft_light(im, im)
    ImageChops.hard_light(im, im)
    ImageChops.overlay(im, im)

    ImageChops.offset(im, 10)
    ImageChops.offset(im, 10, 20)


def test_add():
    # Arrange
    with Image.open("Tests/images/imagedraw_ellipse_RGB.png") as im1:
        with Image.open("Tests/images/imagedraw_floodfill_RGB.png") as im2:

            # Act
            new = ImageChops.add(im1, im2)

    # Assert
    assert new.getbbox() == (25, 25, 76, 76)
    assert new.getpixel((50, 50)) == ORANGE


def test_add_scale_offset():
    # Arrange
    with Image.open("Tests/images/imagedraw_ellipse_RGB.png") as im1:
        with Image.open("Tests/images/imagedraw_floodfill_RGB.png") as im2:

            # Act
            new = ImageChops.add(im1, im2, scale=2.5, offset=100)

    # Assert
    assert new.getbbox() == (0, 0, 100, 100)
    assert new.getpixel((50, 50)) == (202, 151, 100)


def test_add_clip():
    # Arrange
    im = hopper()

    # Act
    new = ImageChops.add(im, im)

    # Assert
    assert new.getpixel((50, 50)) == (255, 255, 254)


def test_add_modulo():
    # Arrange
    with Image.open("Tests/images/imagedraw_ellipse_RGB.png") as im1:
        with Image.open("Tests/images/imagedraw_floodfill_RGB.png") as im2:

            # Act
            new = ImageChops.add_modulo(im1, im2)

    # Assert
    assert new.getbbox() == (25, 25, 76, 76)
    assert new.getpixel((50, 50)) == ORANGE


def test_add_modulo_no_clip():
    # Arrange
    im = hopper()

    # Act
    new = ImageChops.add_modulo(im, im)

    # Assert
    assert new.getpixel((50, 50)) == (224, 76, 254)


def test_blend():
    # Arrange
    with Image.open("Tests/images/imagedraw_ellipse_RGB.png") as im1:
        with Image.open("Tests/images/imagedraw_floodfill_RGB.png") as im2:

            # Act
            new = ImageChops.blend(im1, im2, 0.5)

    # Assert
    assert new.getbbox() == (25, 25, 76, 76)
    assert new.getpixel((50, 50)) == BROWN


def test_constant():
    # Arrange
    im = Image.new("RGB", (20, 10))

    # Act
    new = ImageChops.constant(im, GREY)

    # Assert
    assert new.size == im.size
    assert new.getpixel((0, 0)) == GREY
    assert new.getpixel((19, 9)) == GREY


def test_darker_image():
    # Arrange
    with Image.open("Tests/images/imagedraw_chord_RGB.png") as im1:
        with Image.open("Tests/images/imagedraw_outline_chord_RGB.png") as im2:

            # Act
            new = ImageChops.darker(im1, im2)

            # Assert
            assert_image_equal(new, im2)


def test_darker_pixel():
    # Arrange
    im1 = hopper()
    with Image.open("Tests/images/imagedraw_chord_RGB.png") as im2:

        # Act
        new = ImageChops.darker(im1, im2)

    # Assert
    assert new.getpixel((50, 50)) == (240, 166, 0)


def test_difference():
    # Arrange
    with Image.open("Tests/images/imagedraw_arc_end_le_start.png") as im1:
        with Image.open("Tests/images/imagedraw_arc_no_loops.png") as im2:

            # Act
            new = ImageChops.difference(im1, im2)

    # Assert
    assert new.getbbox() == (25, 25, 76, 76)


def test_difference_pixel():
    # Arrange
    im1 = hopper()
    with Image.open("Tests/images/imagedraw_polygon_kite_RGB.png") as im2:

        # Act
        new = ImageChops.difference(im1, im2)

    # Assert
    assert new.getpixel((50, 50)) == (240, 166, 128)


def test_duplicate():
    # Arrange
    im = hopper()

    # Act
    new = ImageChops.duplicate(im)

    # Assert
    assert_image_equal(new, im)


def test_invert():
    # Arrange
    with Image.open("Tests/images/imagedraw_floodfill_RGB.png") as im:

        # Act
        new = ImageChops.invert(im)

    # Assert
    assert new.getbbox() == (0, 0, 100, 100)
    assert new.getpixel((0, 0)) == WHITE
    assert new.getpixel((50, 50)) == CYAN


def test_lighter_image():
    # Arrange
    with Image.open("Tests/images/imagedraw_chord_RGB.png") as im1:
        with Image.open("Tests/images/imagedraw_outline_chord_RGB.png") as im2:

            # Act
            new = ImageChops.lighter(im1, im2)

        # Assert
        assert_image_equal(new, im1)


def test_lighter_pixel():
    # Arrange
    im1 = hopper()
    with Image.open("Tests/images/imagedraw_chord_RGB.png") as im2:

        # Act
        new = ImageChops.lighter(im1, im2)

    # Assert
    assert new.getpixel((50, 50)) == (255, 255, 127)


def test_multiply_black():
    """If you multiply an image with a solid black image,
    the result is black."""
    # Arrange
    im1 = hopper()
    black = Image.new("RGB", im1.size, "black")

    # Act
    new = ImageChops.multiply(im1, black)

    # Assert
    assert_image_equal(new, black)


def test_multiply_green():
    # Arrange
    with Image.open("Tests/images/imagedraw_floodfill_RGB.png") as im:
        green = Image.new("RGB", im.size, "green")

        # Act
        new = ImageChops.multiply(im, green)

    # Assert
    assert new.getbbox() == (25, 25, 76, 76)
    assert new.getpixel((25, 25)) == DARK_GREEN
    assert new.getpixel((50, 50)) == BLACK


def test_multiply_white():
    """If you multiply with a solid white image, the image is unaffected."""
    # Arrange
    im1 = hopper()
    white = Image.new("RGB", im1.size, "white")

    # Act
    new = ImageChops.multiply(im1, white)

    # Assert
    assert_image_equal(new, im1)


def test_offset():
    # Arrange
    xoffset = 45
    yoffset = 20
    with Image.open("Tests/images/imagedraw_ellipse_RGB.png") as im:

        # Act
        new = ImageChops.offset(im, xoffset, yoffset)

        # Assert
        assert new.getbbox() == (0, 45, 100, 96)
        assert new.getpixel((50, 50)) == BLACK
        assert new.getpixel((50 + xoffset, 50 + yoffset)) == DARK_GREEN

        # Test no yoffset
        assert ImageChops.offset(im, xoffset) == ImageChops.offset(im, xoffset, xoffset)


def test_screen():
    # Arrange
    with Image.open("Tests/images/imagedraw_ellipse_RGB.png") as im1:
        with Image.open("Tests/images/imagedraw_floodfill_RGB.png") as im2:

            # Act
            new = ImageChops.screen(im1, im2)

    # Assert
    assert new.getbbox() == (25, 25, 76, 76)
    assert new.getpixel((50, 50)) == ORANGE


def test_subtract():
    # Arrange
    with Image.open("Tests/images/imagedraw_chord_RGB.png") as im1:
        with Image.open("Tests/images/imagedraw_outline_chord_RGB.png") as im2:

            # Act
            new = ImageChops.subtract(im1, im2)

    # Assert
    assert new.getbbox() == (25, 50, 76, 76)
    assert new.getpixel((50, 51)) == GREEN
    assert new.getpixel((50, 52)) == BLACK


def test_subtract_scale_offset():
    # Arrange
    with Image.open("Tests/images/imagedraw_chord_RGB.png") as im1:
        with Image.open("Tests/images/imagedraw_outline_chord_RGB.png") as im2:

            # Act
            new = ImageChops.subtract(im1, im2, scale=2.5, offset=100)

    # Assert
    assert new.getbbox() == (0, 0, 100, 100)
    assert new.getpixel((50, 50)) == (100, 202, 100)


def test_subtract_clip():
    # Arrange
    im1 = hopper()
    with Image.open("Tests/images/imagedraw_chord_RGB.png") as im2:

        # Act
        new = ImageChops.subtract(im1, im2)

    # Assert
    assert new.getpixel((50, 50)) == (0, 0, 127)


def test_subtract_modulo():
    # Arrange
    with Image.open("Tests/images/imagedraw_chord_RGB.png") as im1:
        with Image.open("Tests/images/imagedraw_outline_chord_RGB.png") as im2:

            # Act
            new = ImageChops.subtract_modulo(im1, im2)

    # Assert
    assert new.getbbox() == (25, 50, 76, 76)
    assert new.getpixel((50, 51)) == GREEN
    assert new.getpixel((50, 52)) == BLACK


def test_subtract_modulo_no_clip():
    # Arrange
    im1 = hopper()
    with Image.open("Tests/images/imagedraw_chord_RGB.png") as im2:

        # Act
        new = ImageChops.subtract_modulo(im1, im2)

    # Assert
    assert new.getpixel((50, 50)) == (241, 167, 127)


def test_soft_light():
    # Arrange
    im1 = Image.open("Tests/images/hopper.png")
    im2 = Image.open("Tests/images/hopper-XYZ.png")

    # Act
    new = ImageChops.soft_light(im1, im2)

    # Assert
    assert new.getpixel((64, 64)) == (163, 54, 32)
    assert new.getpixel((15, 100)) == (1, 1, 3)


def test_hard_light():
    # Arrange
    im1 = Image.open("Tests/images/hopper.png")
    im2 = Image.open("Tests/images/hopper-XYZ.png")

    # Act
    new = ImageChops.hard_light(im1, im2)

    # Assert
    assert new.getpixel((64, 64)) == (144, 50, 27)
    assert new.getpixel((15, 100)) == (1, 1, 2)


def test_overlay():
    # Arrange
    im1 = Image.open("Tests/images/hopper.png")
    im2 = Image.open("Tests/images/hopper-XYZ.png")

    # Act
    new = ImageChops.overlay(im1, im2)

    # Assert
    assert new.getpixel((64, 64)) == (159, 50, 27)
    assert new.getpixel((15, 100)) == (1, 1, 2)


def test_logical():
    def table(op, a, b):
        out = []
        for x in (a, b):
            imx = Image.new("1", (1, 1), x)
            for y in (a, b):
                imy = Image.new("1", (1, 1), y)
                out.append(op(imx, imy).getpixel((0, 0)))
        return tuple(out)

    assert table(ImageChops.logical_and, 0, 1) == (0, 0, 0, 255)
    assert table(ImageChops.logical_or, 0, 1) == (0, 255, 255, 255)
    assert table(ImageChops.logical_xor, 0, 1) == (0, 255, 255, 0)

    assert table(ImageChops.logical_and, 0, 128) == (0, 0, 0, 255)
    assert table(ImageChops.logical_or, 0, 128) == (0, 255, 255, 255)
    assert table(ImageChops.logical_xor, 0, 128) == (0, 255, 255, 0)

    assert table(ImageChops.logical_and, 0, 255) == (0, 0, 0, 255)
    assert table(ImageChops.logical_or, 0, 255) == (0, 255, 255, 255)
    assert table(ImageChops.logical_xor, 0, 255) == (0, 255, 255, 0)
