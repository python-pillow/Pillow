from PIL import Image, ImageChops

from .helper import PillowTestCase, hopper

BLACK = (0, 0, 0)
BROWN = (127, 64, 0)
CYAN = (0, 255, 255)
DARK_GREEN = (0, 128, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 128, 0)
WHITE = (255, 255, 255)

GREY = 128


class TestImageChops(PillowTestCase):
    def test_sanity(self):

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

        ImageChops.offset(im, 10)
        ImageChops.offset(im, 10, 20)

    def test_add(self):
        # Arrange
        with Image.open("Tests/images/imagedraw_ellipse_RGB.png") as im1:
            with Image.open("Tests/images/imagedraw_floodfill_RGB.png") as im2:

                # Act
                new = ImageChops.add(im1, im2)

        # Assert
        self.assertEqual(new.getbbox(), (25, 25, 76, 76))
        self.assertEqual(new.getpixel((50, 50)), ORANGE)

    def test_add_scale_offset(self):
        # Arrange
        with Image.open("Tests/images/imagedraw_ellipse_RGB.png") as im1:
            with Image.open("Tests/images/imagedraw_floodfill_RGB.png") as im2:

                # Act
                new = ImageChops.add(im1, im2, scale=2.5, offset=100)

        # Assert
        self.assertEqual(new.getbbox(), (0, 0, 100, 100))
        self.assertEqual(new.getpixel((50, 50)), (202, 151, 100))

    def test_add_clip(self):
        # Arrange
        im = hopper()

        # Act
        new = ImageChops.add(im, im)

        # Assert
        self.assertEqual(new.getpixel((50, 50)), (255, 255, 254))

    def test_add_modulo(self):
        # Arrange
        with Image.open("Tests/images/imagedraw_ellipse_RGB.png") as im1:
            with Image.open("Tests/images/imagedraw_floodfill_RGB.png") as im2:

                # Act
                new = ImageChops.add_modulo(im1, im2)

        # Assert
        self.assertEqual(new.getbbox(), (25, 25, 76, 76))
        self.assertEqual(new.getpixel((50, 50)), ORANGE)

    def test_add_modulo_no_clip(self):
        # Arrange
        im = hopper()

        # Act
        new = ImageChops.add_modulo(im, im)

        # Assert
        self.assertEqual(new.getpixel((50, 50)), (224, 76, 254))

    def test_blend(self):
        # Arrange
        with Image.open("Tests/images/imagedraw_ellipse_RGB.png") as im1:
            with Image.open("Tests/images/imagedraw_floodfill_RGB.png") as im2:

                # Act
                new = ImageChops.blend(im1, im2, 0.5)

        # Assert
        self.assertEqual(new.getbbox(), (25, 25, 76, 76))
        self.assertEqual(new.getpixel((50, 50)), BROWN)

    def test_constant(self):
        # Arrange
        im = Image.new("RGB", (20, 10))

        # Act
        new = ImageChops.constant(im, GREY)

        # Assert
        self.assertEqual(new.size, im.size)
        self.assertEqual(new.getpixel((0, 0)), GREY)
        self.assertEqual(new.getpixel((19, 9)), GREY)

    def test_darker_image(self):
        # Arrange
        with Image.open("Tests/images/imagedraw_chord_RGB.png") as im1:
            with Image.open("Tests/images/imagedraw_outline_chord_RGB.png") as im2:

                # Act
                new = ImageChops.darker(im1, im2)

                # Assert
                self.assert_image_equal(new, im2)

    def test_darker_pixel(self):
        # Arrange
        im1 = hopper()
        with Image.open("Tests/images/imagedraw_chord_RGB.png") as im2:

            # Act
            new = ImageChops.darker(im1, im2)

        # Assert
        self.assertEqual(new.getpixel((50, 50)), (240, 166, 0))

    def test_difference(self):
        # Arrange
        with Image.open("Tests/images/imagedraw_arc_end_le_start.png") as im1:
            with Image.open("Tests/images/imagedraw_arc_no_loops.png") as im2:

                # Act
                new = ImageChops.difference(im1, im2)

        # Assert
        self.assertEqual(new.getbbox(), (25, 25, 76, 76))

    def test_difference_pixel(self):
        # Arrange
        im1 = hopper()
        with Image.open("Tests/images/imagedraw_polygon_kite_RGB.png") as im2:

            # Act
            new = ImageChops.difference(im1, im2)

        # Assert
        self.assertEqual(new.getpixel((50, 50)), (240, 166, 128))

    def test_duplicate(self):
        # Arrange
        im = hopper()

        # Act
        new = ImageChops.duplicate(im)

        # Assert
        self.assert_image_equal(new, im)

    def test_invert(self):
        # Arrange
        with Image.open("Tests/images/imagedraw_floodfill_RGB.png") as im:

            # Act
            new = ImageChops.invert(im)

        # Assert
        self.assertEqual(new.getbbox(), (0, 0, 100, 100))
        self.assertEqual(new.getpixel((0, 0)), WHITE)
        self.assertEqual(new.getpixel((50, 50)), CYAN)

    def test_lighter_image(self):
        # Arrange
        with Image.open("Tests/images/imagedraw_chord_RGB.png") as im1:
            with Image.open("Tests/images/imagedraw_outline_chord_RGB.png") as im2:

                # Act
                new = ImageChops.lighter(im1, im2)

        # Assert
        self.assert_image_equal(new, im1)

    def test_lighter_pixel(self):
        # Arrange
        im1 = hopper()
        with Image.open("Tests/images/imagedraw_chord_RGB.png") as im2:

            # Act
            new = ImageChops.lighter(im1, im2)

        # Assert
        self.assertEqual(new.getpixel((50, 50)), (255, 255, 127))

    def test_multiply_black(self):
        """If you multiply an image with a solid black image,
        the result is black."""
        # Arrange
        im1 = hopper()
        black = Image.new("RGB", im1.size, "black")

        # Act
        new = ImageChops.multiply(im1, black)

        # Assert
        self.assert_image_equal(new, black)

    def test_multiply_green(self):
        # Arrange
        with Image.open("Tests/images/imagedraw_floodfill_RGB.png") as im:
            green = Image.new("RGB", im.size, "green")

            # Act
            new = ImageChops.multiply(im, green)

        # Assert
        self.assertEqual(new.getbbox(), (25, 25, 76, 76))
        self.assertEqual(new.getpixel((25, 25)), DARK_GREEN)
        self.assertEqual(new.getpixel((50, 50)), BLACK)

    def test_multiply_white(self):
        """If you multiply with a solid white image,
        the image is unaffected."""
        # Arrange
        im1 = hopper()
        white = Image.new("RGB", im1.size, "white")

        # Act
        new = ImageChops.multiply(im1, white)

        # Assert
        self.assert_image_equal(new, im1)

    def test_offset(self):
        # Arrange
        xoffset = 45
        yoffset = 20
        with Image.open("Tests/images/imagedraw_ellipse_RGB.png") as im:

            # Act
            new = ImageChops.offset(im, xoffset, yoffset)

        # Assert
        self.assertEqual(new.getbbox(), (0, 45, 100, 96))
        self.assertEqual(new.getpixel((50, 50)), BLACK)
        self.assertEqual(new.getpixel((50 + xoffset, 50 + yoffset)), DARK_GREEN)

        # Test no yoffset
        self.assertEqual(
            ImageChops.offset(im, xoffset), ImageChops.offset(im, xoffset, xoffset)
        )

    def test_screen(self):
        # Arrange
        with Image.open("Tests/images/imagedraw_ellipse_RGB.png") as im1:
            with Image.open("Tests/images/imagedraw_floodfill_RGB.png") as im2:

                # Act
                new = ImageChops.screen(im1, im2)

        # Assert
        self.assertEqual(new.getbbox(), (25, 25, 76, 76))
        self.assertEqual(new.getpixel((50, 50)), ORANGE)

    def test_subtract(self):
        # Arrange
        with Image.open("Tests/images/imagedraw_chord_RGB.png") as im1:
            with Image.open("Tests/images/imagedraw_outline_chord_RGB.png") as im2:

                # Act
                new = ImageChops.subtract(im1, im2)

        # Assert
        self.assertEqual(new.getbbox(), (25, 50, 76, 76))
        self.assertEqual(new.getpixel((50, 50)), GREEN)
        self.assertEqual(new.getpixel((50, 51)), BLACK)

    def test_subtract_scale_offset(self):
        # Arrange
        with Image.open("Tests/images/imagedraw_chord_RGB.png") as im1:
            with Image.open("Tests/images/imagedraw_outline_chord_RGB.png") as im2:

                # Act
                new = ImageChops.subtract(im1, im2, scale=2.5, offset=100)

        # Assert
        self.assertEqual(new.getbbox(), (0, 0, 100, 100))
        self.assertEqual(new.getpixel((50, 50)), (100, 202, 100))

    def test_subtract_clip(self):
        # Arrange
        im1 = hopper()
        with Image.open("Tests/images/imagedraw_chord_RGB.png") as im2:

            # Act
            new = ImageChops.subtract(im1, im2)

        # Assert
        self.assertEqual(new.getpixel((50, 50)), (0, 0, 127))

    def test_subtract_modulo(self):
        # Arrange
        with Image.open("Tests/images/imagedraw_chord_RGB.png") as im1:
            with Image.open("Tests/images/imagedraw_outline_chord_RGB.png") as im2:

                # Act
                new = ImageChops.subtract_modulo(im1, im2)

        # Assert
        self.assertEqual(new.getbbox(), (25, 50, 76, 76))
        self.assertEqual(new.getpixel((50, 50)), GREEN)
        self.assertEqual(new.getpixel((50, 51)), BLACK)

    def test_subtract_modulo_no_clip(self):
        # Arrange
        im1 = hopper()
        with Image.open("Tests/images/imagedraw_chord_RGB.png") as im2:

            # Act
            new = ImageChops.subtract_modulo(im1, im2)

        # Assert
        self.assertEqual(new.getpixel((50, 50)), (241, 167, 127))

    def test_logical(self):
        def table(op, a, b):
            out = []
            for x in (a, b):
                imx = Image.new("1", (1, 1), x)
                for y in (a, b):
                    imy = Image.new("1", (1, 1), y)
                    out.append(op(imx, imy).getpixel((0, 0)))
            return tuple(out)

        self.assertEqual(table(ImageChops.logical_and, 0, 1), (0, 0, 0, 255))
        self.assertEqual(table(ImageChops.logical_or, 0, 1), (0, 255, 255, 255))
        self.assertEqual(table(ImageChops.logical_xor, 0, 1), (0, 255, 255, 0))

        self.assertEqual(table(ImageChops.logical_and, 0, 128), (0, 0, 0, 255))
        self.assertEqual(table(ImageChops.logical_or, 0, 128), (0, 255, 255, 255))
        self.assertEqual(table(ImageChops.logical_xor, 0, 128), (0, 255, 255, 0))

        self.assertEqual(table(ImageChops.logical_and, 0, 255), (0, 0, 0, 255))
        self.assertEqual(table(ImageChops.logical_or, 0, 255), (0, 255, 255, 255))
        self.assertEqual(table(ImageChops.logical_xor, 0, 255), (0, 255, 255, 0))
