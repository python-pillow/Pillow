from helper import unittest, PillowTestCase, hopper
from PIL import Image


try:
    from PIL import ImageTk
    import Tkinter as tk
    dir(ImageTk)
    HAS_TK = True
except (OSError, ImportError) as v:
    # Skipped via setUp()
    HAS_TK = False

TK_MODES = ('1', 'L', 'P', 'RGB', 'RGBA')


class TestImageTk(PillowTestCase):

    def setUp(self):
        if not HAS_TK:
            self.skipTest("Tk not installed")
        try:
            # setup tk
            app = tk.Frame()
            # root = tk.Tk()
        except (tk.TclError) as v:
            self.skipTest("TCL Error: %s" % v)

    def test_kw(self):
        TEST_JPG = "Tests/images/hopper.jpg"
        TEST_PNG = "Tests/images/hopper.png"
        im1 = Image.open(TEST_JPG)
        im2 = Image.open(TEST_PNG)
        with open(TEST_PNG, 'rb') as fp:
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

            # _tkinter.TclError: this function is not yet supported
            # reloaded = ImageTk.getimage(im_tk)
            # self.assert_image_equal(reloaded, im)

    def test_photoimage_blank(self):
        # test a image using mode/size:
        for mode in TK_MODES:
            im_tk = ImageTk.PhotoImage(mode, (100, 100))

            self.assertEqual(im_tk.width(), 100)
            self.assertEqual(im_tk.height(), 100)

            # reloaded = ImageTk.getimage(im_tk)
            # self.assert_image_equal(reloaded, im)

    def test_bitmapimage(self):
        im = hopper('1')

        # this should not crash
        im_tk = ImageTk.BitmapImage(im)

        self.assertEqual(im_tk.width(), im.width)
        self.assertEqual(im_tk.height(), im.height)

        # reloaded = ImageTk.getimage(im_tk)
        # self.assert_image_equal(reloaded, im)


if __name__ == '__main__':
    unittest.main()
