import sys
import unittest

from PIL import Image

from .helper import PillowTestCase, is_win32

try:
    import numpy
except ImportError:
    numpy = None


@unittest.skipIf(is_win32(), "Win32 does not call map_buffer")
class TestMap(PillowTestCase):
    def test_overflow(self):
        # There is the potential to overflow comparisons in map.c
        # if there are > SIZE_MAX bytes in the image or if
        # the file encodes an offset that makes
        # (offset + size(bytes)) > SIZE_MAX

        # Note that this image triggers the decompression bomb warning:
        max_pixels = Image.MAX_IMAGE_PIXELS
        Image.MAX_IMAGE_PIXELS = None

        # This image hits the offset test.
        with Image.open("Tests/images/l2rgb_read.bmp") as im:
            with self.assertRaises((ValueError, MemoryError, IOError)):
                im.load()

        Image.MAX_IMAGE_PIXELS = max_pixels

    @unittest.skipIf(sys.maxsize <= 2 ** 32, "requires 64-bit system")
    @unittest.skipIf(numpy is None, "Numpy is not installed")
    def test_ysize(self):
        # Should not raise 'Integer overflow in ysize'
        arr = numpy.zeros((46341, 46341), dtype=numpy.uint8)
        Image.fromarray(arr)
