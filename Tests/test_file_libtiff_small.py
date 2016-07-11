from helper import unittest

from PIL import Image

from test_file_libtiff import LibTiffTestCase


class TestFileLibTiffSmall(LibTiffTestCase):

    """ The small lena image was failing on open in the libtiff
        decoder because the file pointer was set to the wrong place
        by a spurious seek. It wasn't failing with the byteio method.

        It was fixed by forcing an lseek to the beginning of the
        file just before reading in libtiff. These tests remain
        to ensure that it stays fixed. """

    def test_g4_hopper_file(self):
        """Testing the open file load path"""

        test_file = "Tests/images/hopper_g4.tif"
        with open(test_file, 'rb') as f:
            im = Image.open(f)

            self.assertEqual(im.size, (128, 128))
            self._assert_noerr(im)

    def test_g4_hopper_bytesio(self):
        """Testing the bytesio loading code path"""
        from io import BytesIO
        test_file = "Tests/images/hopper_g4.tif"
        s = BytesIO()
        with open(test_file, 'rb') as f:
            s.write(f.read())
            s.seek(0)
        im = Image.open(s)

        self.assertEqual(im.size, (128, 128))
        self._assert_noerr(im)

    def test_g4_hopper(self):
        """The 128x128 lena image failed for some reason."""

        test_file = "Tests/images/hopper_g4.tif"
        im = Image.open(test_file)

        self.assertEqual(im.size, (128, 128))
        self._assert_noerr(im)


if __name__ == '__main__':
    unittest.main()
