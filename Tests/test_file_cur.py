from helper import unittest, PillowTestCase

from PIL import Image, CurImagePlugin


class TestFileCur(PillowTestCase):

    def test_sanity(self):
        # Arrange
        test_file = "Tests/images/deerstalker.cur"

        # Act
        im = Image.open(test_file)

        # Assert
        self.assertEqual(im.size, (32, 32))
        self.assertIsInstance(im, CurImagePlugin.CurImageFile)
        # Check some pixel colors to ensure image is loaded properly
        self.assertEqual(im.getpixel((10, 1)), (0, 0, 0, 0))
        self.assertEqual(im.getpixel((11, 1)), (253, 254, 254, 1))
        self.assertEqual(im.getpixel((16, 16)), (84, 87, 86, 255))

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda: CurImagePlugin.CurImageFile(invalid_file))


if __name__ == '__main__':
    unittest.main()

# End of file
