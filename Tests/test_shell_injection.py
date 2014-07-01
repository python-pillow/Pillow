from helper import unittest, PillowTestCase, tearDownModule
from helper import djpeg_available, cjpeg_available, netpbm_available

import sys
import shutil

from PIL import Image, JpegImagePlugin, GifImagePlugin

test_jpg = "Tests/images/lena.jpg"
test_gif = "Tests/images/lena.gif"

test_filenames = (
    "temp_';",
    "temp_\";",
    "temp_'\"|",
    "temp_'\"||",
    "temp_'\"&&",
)

@unittest.skipIf(sys.platform.startswith('win32'), "requires Unix or MacOS")
class TestShellInjection(PillowTestCase):

    def assert_save_filename_check(self, src_img, save_func):
        for filename in test_filenames:
            dest_file = self.tempfile(filename)
            save_func(src_img, 0, dest_file)
            # If file can't be opened, shell injection probably occurred
            Image.open(dest_file).load()

    @unittest.skipUnless(djpeg_available(), "djpeg not available")
    def test_load_djpeg_filename(self):
        for filename in test_filenames:
            src_file = self.tempfile(filename)
            shutil.copy(test_jpg, src_file)

            im = Image.open(src_file)
            im.load_djpeg()

    @unittest.skipUnless(cjpeg_available(), "cjpeg not available")
    def test_save_cjpeg_filename(self):
        im = Image.open(test_jpg)
        self.assert_save_filename_check(im, JpegImagePlugin._save_cjpeg)

    @unittest.skipUnless(netpbm_available(), "netpbm not available")
    def test_save_netpbm_filename_bmp_mode(self):
        im = Image.open(test_gif).convert("RGB")
        self.assert_save_filename_check(im, GifImagePlugin._save_netpbm)

    @unittest.skipUnless(netpbm_available(), "netpbm not available")
    def test_save_netpbm_filename_l_mode(self):
        im = Image.open(test_gif).convert("L")
        self.assert_save_filename_check(im, GifImagePlugin._save_netpbm)


if __name__ == '__main__':
    unittest.main()

# End of file
