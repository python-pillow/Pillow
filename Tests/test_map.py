from helper import PillowTestCase, unittest

from PIL import Image

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
        im = Image.open('Tests/images/l2rgb_read.bmp')
        with self.assertRaises((ValueError, MemoryError)):
            im.load()

        Image.MAX_IMAGE_PIXELS = max_pixels


if __name__ == '__main__':
    unittest.main()
