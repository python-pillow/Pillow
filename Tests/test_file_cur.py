from helper import unittest, PillowTestCase

from PIL import Image, CurImagePlugin

TEST_FILE = "Tests/images/deerstalker.cur"


class TestFileCur(PillowTestCase):

    def test_sanity(self):
        im = Image.open(TEST_FILE)

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

        no_cursors_file = "Tests/images/no_cursors.cur"

        cur = CurImagePlugin.CurImageFile(TEST_FILE)
        cur.fp = open(no_cursors_file, "rb")
        self.assertRaises(TypeError, cur._open)


if __name__ == '__main__':
    unittest.main()

# End of file
