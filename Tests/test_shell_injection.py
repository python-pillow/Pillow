import shutil

import pytest

from PIL import GifImagePlugin, Image, JpegImagePlugin

from .helper import cjpeg_available, djpeg_available, is_win32, netpbm_available

TEST_JPG = "Tests/images/hopper.jpg"
TEST_GIF = "Tests/images/hopper.gif"

test_filenames = ("temp_';", 'temp_";', "temp_'\"|", "temp_'\"||", "temp_'\"&&")


@pytest.mark.skipif(is_win32(), reason="Requires Unix or macOS")
class TestShellInjection:
    def assert_save_filename_check(self, tmp_path, src_img, save_func):
        for filename in test_filenames:
            dest_file = str(tmp_path / filename)
            save_func(src_img, 0, dest_file)
            # If file can't be opened, shell injection probably occurred
            with Image.open(dest_file) as im:
                im.load()

    @pytest.mark.skipif(not djpeg_available(), reason="djpeg not available")
    def test_load_djpeg_filename(self, tmp_path):
        for filename in test_filenames:
            src_file = str(tmp_path / filename)
            shutil.copy(TEST_JPG, src_file)

            with Image.open(src_file) as im:
                im.load_djpeg()

    @pytest.mark.skipif(not cjpeg_available(), reason="cjpeg not available")
    def test_save_cjpeg_filename(self, tmp_path):
        with Image.open(TEST_JPG) as im:
            self.assert_save_filename_check(tmp_path, im, JpegImagePlugin._save_cjpeg)

    @pytest.mark.skipif(not netpbm_available(), reason="Netpbm not available")
    def test_save_netpbm_filename_bmp_mode(self, tmp_path):
        with Image.open(TEST_GIF) as im:
            im = im.convert("RGB")
            self.assert_save_filename_check(tmp_path, im, GifImagePlugin._save_netpbm)

    @pytest.mark.skipif(not netpbm_available(), reason="Netpbm not available")
    def test_save_netpbm_filename_l_mode(self, tmp_path):
        with Image.open(TEST_GIF) as im:
            im = im.convert("L")
            self.assert_save_filename_check(tmp_path, im, GifImagePlugin._save_netpbm)
