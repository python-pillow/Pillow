from io import BytesIO

from PIL import Image

from .test_file_libtiff import LibTiffTestCase


class TestFileLibTiffSmall(LibTiffTestCase):

    """The small lena image was failing on open in the libtiff
    decoder because the file pointer was set to the wrong place
    by a spurious seek. It wasn't failing with the byteio method.

    It was fixed by forcing an lseek to the beginning of the
    file just before reading in libtiff. These tests remain
    to ensure that it stays fixed."""

    def test_g4_hopper_file(self, tmp_path):
        """Testing the open file load path"""

        test_file = "Tests/images/hopper_g4.tif"
        with open(test_file, "rb") as f:
            with Image.open(f) as im:
                assert im.size == (128, 128)
                self._assert_noerr(tmp_path, im)

    def test_g4_hopper_bytesio(self, tmp_path):
        """Testing the bytesio loading code path"""
        test_file = "Tests/images/hopper_g4.tif"
        s = BytesIO()
        with open(test_file, "rb") as f:
            s.write(f.read())
            s.seek(0)
        with Image.open(s) as im:
            assert im.size == (128, 128)
            self._assert_noerr(tmp_path, im)

    def test_g4_hopper(self, tmp_path):
        """The 128x128 lena image failed for some reason."""

        test_file = "Tests/images/hopper_g4.tif"
        with Image.open(test_file) as im:
            assert im.size == (128, 128)
            self._assert_noerr(tmp_path, im)
