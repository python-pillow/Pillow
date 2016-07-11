from helper import unittest, PillowTestCase, hopper

from PIL import Image


class TestImageGetBbox(PillowTestCase):

    def test_sanity(self):

        bbox = hopper().getbbox()
        self.assertIsInstance(bbox, tuple)

    def test_bbox(self):

        # 8-bit mode
        im = Image.new("L", (100, 100), 0)
        self.assertEqual(im.getbbox(), None)

        im.paste(255, (10, 25, 90, 75))
        self.assertEqual(im.getbbox(), (10, 25, 90, 75))

        im.paste(255, (25, 10, 75, 90))
        self.assertEqual(im.getbbox(), (10, 10, 90, 90))

        im.paste(255, (-10, -10, 110, 110))
        self.assertEqual(im.getbbox(), (0, 0, 100, 100))

        # 32-bit mode
        im = Image.new("RGB", (100, 100), 0)
        self.assertEqual(im.getbbox(), None)

        im.paste(255, (10, 25, 90, 75))
        self.assertEqual(im.getbbox(), (10, 25, 90, 75))

        im.paste(255, (25, 10, 75, 90))
        self.assertEqual(im.getbbox(), (10, 10, 90, 90))

        im.paste(255, (-10, -10, 110, 110))
        self.assertEqual(im.getbbox(), (0, 0, 100, 100))


if __name__ == '__main__':
    unittest.main()
