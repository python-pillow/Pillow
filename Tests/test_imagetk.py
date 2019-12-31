import unittest

from PIL import Image

from .helper import PillowTestCase, hopper

try:
    from PIL import ImageTk

    import tkinter as tk

    dir(ImageTk)
    HAS_TK = True
except (OSError, ImportError):
    # Skipped via setUp()
    HAS_TK = False

TK_MODES = ("1", "L", "P", "RGB", "RGBA")


@unittest.skipUnless(HAS_TK, "Tk not installed")
class TestImageTk(PillowTestCase):
    def setUp(self):
        try:
            # setup tk
            tk.Frame()
            # root = tk.Tk()
        except tk.TclError as v:
            self.skipTest("TCL Error: %s" % v)

    def test_kw(self):
        TEST_JPG = "Tests/images/hopper.jpg"
        TEST_PNG = "Tests/images/hopper.png"
        with Image.open(TEST_JPG) as im1:
            with Image.open(TEST_PNG) as im2:
                with open(TEST_PNG, "rb") as fp:
                    data = fp.read()
                kw = {"file": TEST_JPG, "data": data}

                # Test "file"
                im = ImageTk._get_image_from_kw(kw)
                self.assert_image_equal(im, im1)

                # Test "data"
                im = ImageTk._get_image_from_kw(kw)
                self.assert_image_equal(im, im2)

        # Test no relevant entry
        im = ImageTk._get_image_from_kw(kw)
        self.assertIsNone(im)

    def test_photoimage(self):
        for mode in TK_MODES:
            # test as image:
            im = hopper(mode)

            # this should not crash
            im_tk = ImageTk.PhotoImage(im)

            self.assertEqual(im_tk.width(), im.width)
            self.assertEqual(im_tk.height(), im.height)

            reloaded = ImageTk.getimage(im_tk)
            self.assert_image_equal(reloaded, im.convert("RGBA"))

    def test_photoimage_blank(self):
        # test a image using mode/size:
        for mode in TK_MODES:
            im_tk = ImageTk.PhotoImage(mode, (100, 100))

            self.assertEqual(im_tk.width(), 100)
            self.assertEqual(im_tk.height(), 100)

            # reloaded = ImageTk.getimage(im_tk)
            # self.assert_image_equal(reloaded, im)

    def test_bitmapimage(self):
        im = hopper("1")

        # this should not crash
        im_tk = ImageTk.BitmapImage(im)

        self.assertEqual(im_tk.width(), im.width)
        self.assertEqual(im_tk.height(), im.height)

        # reloaded = ImageTk.getimage(im_tk)
        # self.assert_image_equal(reloaded, im)
