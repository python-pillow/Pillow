from helper import unittest, PillowTestCase, hopper

from PIL import Image

import os


class TestImageLoad(PillowTestCase):

    def test_sanity(self):

        im = hopper()

        pix = im.load()

        self.assertEqual(pix[0, 0], (20, 20, 70))

    def test_close(self):
        im = Image.open("Tests/images/hopper.gif")
        im.close()
        self.assertRaises(ValueError, im.load)
        self.assertRaises(ValueError, lambda: im.getpixel((0, 0)))

    def test_contextmanager(self):
        fn = None
        with Image.open("Tests/images/hopper.gif") as im:
            fn = im.fp.fileno()
            os.fstat(fn)

        self.assertRaises(OSError, lambda: os.fstat(fn))

if __name__ == '__main__':
    unittest.main()

# End of file
