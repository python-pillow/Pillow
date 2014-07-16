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


if __name__ == '__main__':
    unittest.main()

# End of file
