from helper import unittest, PillowTestCase, hopper

import io
from PIL import Image, IcoImagePlugin

# sample ppm stream
TEST_ICO_FILE = "Tests/images/hopper.ico"


class TestFileIco(PillowTestCase):

    def test_sanity(self):
        im = Image.open(TEST_ICO_FILE)
        im.load()
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (16, 16))
        self.assertEqual(im.format, "ICO")

    def test_invalid_file(self):
        with open("Tests/images/flower.jpg", "rb") as fp:
            self.assertRaises(SyntaxError,
                              lambda: IcoImagePlugin.IcoImageFile(fp))

    def test_save_to_bytes(self):
        output = io.BytesIO()
        im = hopper()
        im.save(output, "ico", sizes=[(32, 32), (64, 64)])

        # the default image
        output.seek(0)
        reloaded = Image.open(output)
        self.assertEqual(reloaded.info['sizes'], set([(32, 32), (64, 64)]))

        self.assertEqual(im.mode, reloaded.mode)
        self.assertEqual((64, 64), reloaded.size)
        self.assertEqual(reloaded.format, "ICO")
        self.assert_image_equal(reloaded,
                                hopper().resize((64, 64), Image.LANCZOS))

        # the other one
        output.seek(0)
        reloaded = Image.open(output)
        reloaded.size = (32, 32)

        self.assertEqual(im.mode, reloaded.mode)
        self.assertEqual((32, 32), reloaded.size)
        self.assertEqual(reloaded.format, "ICO")
        self.assert_image_equal(reloaded,
                                hopper().resize((32, 32), Image.LANCZOS))

    def test_save_256x256(self):
        """Issue #2264 https://github.com/python-pillow/Pillow/issues/2264"""
        # Arrange
        im = Image.open("Tests/images/hopper_256x256.ico")
        outfile = self.tempfile("temp_saved_hopper_256x256.ico")

        # Act
        im.save(outfile)
        im_saved = Image.open(outfile)

        # Assert
        self.assertEqual(im_saved.size, (256, 256))

    def test_only_save_relevant_sizes(self):
        """Issue #2266 https://github.com/python-pillow/Pillow/issues/2266
        Should save in 16x16, 24x24, 32x32, 48x48 sizes
        and not in 16x16, 24x24, 32x32, 48x48, 48x48, 48x48, 48x48 sizes
        """
        # Arrange
        im = Image.open("Tests/images/python.ico")  # 16x16, 32x32, 48x48
        outfile = self.tempfile("temp_saved_python.ico")

        # Act
        im.save(outfile)
        im_saved = Image.open(outfile)

        # Assert
        self.assertEqual(
            im_saved.info['sizes'],
            set([(16, 16), (24, 24), (32, 32), (48, 48)]))


if __name__ == '__main__':
    unittest.main()
