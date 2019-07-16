import os

from PIL import Image

from .helper import PillowTestCase, hopper


class TestImageLoad(PillowTestCase):
    def test_sanity(self):

        im = hopper()

        pix = im.load()

        self.assertEqual(pix[0, 0], (20, 20, 70))

    def test_close(self):
        im = Image.open("Tests/images/hopper.gif")
        im.close()
        self.assertRaises(ValueError, im.load)
        self.assertRaises(ValueError, im.getpixel, (0, 0))

    def test_contextmanager(self):
        fn = None
        with Image.open("Tests/images/hopper.gif") as im:
            fn = im.fp.fileno()
            os.fstat(fn)

        self.assertRaises(OSError, os.fstat, fn)

    def test_contextmanager_non_exclusive_fp(self):
        with open("Tests/images/hopper.gif", "rb") as fp:
            with Image.open(fp):
                pass

            self.assertFalse(fp.closed)
