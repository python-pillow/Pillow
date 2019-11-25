import io

from PIL import IcoImagePlugin, Image, ImageDraw

from .helper import PillowTestCase, hopper

TEST_ICO_FILE = "Tests/images/hopper.ico"


class TestFileIco(PillowTestCase):
    def test_sanity(self):
        with Image.open(TEST_ICO_FILE) as im:
            im.load()
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (16, 16))
        self.assertEqual(im.format, "ICO")
        self.assertEqual(im.get_format_mimetype(), "image/x-icon")

    def test_invalid_file(self):
        with open("Tests/images/flower.jpg", "rb") as fp:
            self.assertRaises(SyntaxError, IcoImagePlugin.IcoImageFile, fp)

    def test_save_to_bytes(self):
        output = io.BytesIO()
        im = hopper()
        im.save(output, "ico", sizes=[(32, 32), (64, 64)])

        # the default image
        output.seek(0)
        with Image.open(output) as reloaded:
            self.assertEqual(reloaded.info["sizes"], {(32, 32), (64, 64)})

            self.assertEqual(im.mode, reloaded.mode)
            self.assertEqual((64, 64), reloaded.size)
            self.assertEqual(reloaded.format, "ICO")
            self.assert_image_equal(reloaded, hopper().resize((64, 64), Image.LANCZOS))

        # the other one
        output.seek(0)
        with Image.open(output) as reloaded:
            reloaded.size = (32, 32)

            self.assertEqual(im.mode, reloaded.mode)
            self.assertEqual((32, 32), reloaded.size)
            self.assertEqual(reloaded.format, "ICO")
            self.assert_image_equal(reloaded, hopper().resize((32, 32), Image.LANCZOS))

    def test_incorrect_size(self):
        with Image.open(TEST_ICO_FILE) as im:
            with self.assertRaises(ValueError):
                im.size = (1, 1)

    def test_save_256x256(self):
        """Issue #2264 https://github.com/python-pillow/Pillow/issues/2264"""
        # Arrange
        with Image.open("Tests/images/hopper_256x256.ico") as im:
            outfile = self.tempfile("temp_saved_hopper_256x256.ico")

            # Act
            im.save(outfile)
        with Image.open(outfile) as im_saved:

            # Assert
            self.assertEqual(im_saved.size, (256, 256))

    def test_only_save_relevant_sizes(self):
        """Issue #2266 https://github.com/python-pillow/Pillow/issues/2266
        Should save in 16x16, 24x24, 32x32, 48x48 sizes
        and not in 16x16, 24x24, 32x32, 48x48, 48x48, 48x48, 48x48 sizes
        """
        # Arrange
        with Image.open("Tests/images/python.ico") as im:  # 16x16, 32x32, 48x48
            outfile = self.tempfile("temp_saved_python.ico")
            # Act
            im.save(outfile)

        with Image.open(outfile) as im_saved:
            # Assert
            self.assertEqual(
                im_saved.info["sizes"], {(16, 16), (24, 24), (32, 32), (48, 48)}
            )

    def test_unexpected_size(self):
        # This image has been manually hexedited to state that it is 16x32
        # while the image within is still 16x16
        def open():
            with Image.open("Tests/images/hopper_unexpected.ico") as im:
                self.assertEqual(im.size, (16, 16))

        self.assert_warning(UserWarning, open)

    def test_draw_reloaded(self):
        with Image.open(TEST_ICO_FILE) as im:
            outfile = self.tempfile("temp_saved_hopper_draw.ico")

            draw = ImageDraw.Draw(im)
            draw.line((0, 0) + im.size, "#f00")
            im.save(outfile)

        with Image.open(outfile) as im:
            im.save("Tests/images/hopper_draw.ico")
            with Image.open("Tests/images/hopper_draw.ico") as reloaded:
                self.assert_image_equal(im, reloaded)
