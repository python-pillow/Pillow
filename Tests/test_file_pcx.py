from helper import unittest, PillowTestCase, hopper

from PIL import Image, ImageFile, PcxImagePlugin


class TestFilePcx(PillowTestCase):

    def _roundtrip(self, im):
        f = self.tempfile("temp.pcx")
        im.save(f)
        im2 = Image.open(f)

        self.assertEqual(im2.mode, im.mode)
        self.assertEqual(im2.size, im.size)
        self.assertEqual(im2.format, "PCX")
        self.assert_image_equal(im2, im)

    def test_sanity(self):
        for mode in ('1', 'L', 'P', 'RGB'):
            self._roundtrip(hopper(mode))

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda: PcxImagePlugin.PcxImageFile(invalid_file))

    def test_odd(self):
        # see issue #523, odd sized images should have a stride that's even.
        # not that imagemagick or gimp write pcx that way.
        # we were not handling properly.
        for mode in ('1', 'L', 'P', 'RGB'):
            # larger, odd sized images are better here to ensure that
            # we handle interrupted scan lines properly.
            self._roundtrip(hopper(mode).resize((511, 511)))

    def test_pil184(self):
        # Check reading of files where xmin/xmax is not zero.

        test_file = "Tests/images/pil184.pcx"
        im = Image.open(test_file)

        self.assertEqual(im.size, (447, 144))
        self.assertEqual(im.tile[0][1], (0, 0, 447, 144))

        # Make sure all pixels are either 0 or 255.
        self.assertEqual(im.histogram()[0] + im.histogram()[255], 447*144)

    def test_1px_width(self):
        im = Image.new('L', (1, 256))
        px = im.load()
        for y in range(256):
            px[0, y] = y
        self._roundtrip(im)

    def test_large_count(self):
        im = Image.new('L', (256, 1))
        px = im.load()
        for x in range(256):
            px[x, 0] = x // 67 * 67
        self._roundtrip(im)

    def _test_buffer_overflow(self, im, size=1024):
        _last = ImageFile.MAXBLOCK
        ImageFile.MAXBLOCK = size
        try:
            self._roundtrip(im)
        finally:
            ImageFile.MAXBLOCK = _last

    def test_break_in_count_overflow(self):
        im = Image.new('L', (256, 5))
        px = im.load()
        for y in range(4):
            for x in range(256):
                px[x, y] = x % 128
        self._test_buffer_overflow(im)

    def test_break_one_in_loop(self):
        im = Image.new('L', (256, 5))
        px = im.load()
        for y in range(5):
            for x in range(256):
                px[x, y] = x % 128
        self._test_buffer_overflow(im)

    def test_break_many_in_loop(self):
        im = Image.new('L', (256, 5))
        px = im.load()
        for y in range(4):
            for x in range(256):
                px[x, y] = x % 128
        for x in range(8):
            px[x, 4] = 16
        self._test_buffer_overflow(im)

    def test_break_one_at_end(self):
        im = Image.new('L', (256, 5))
        px = im.load()
        for y in range(5):
            for x in range(256):
                px[x, y] = x % 128
        px[0, 3] = 128 + 64
        self._test_buffer_overflow(im)

    def test_break_many_at_end(self):
        im = Image.new('L', (256, 5))
        px = im.load()
        for y in range(5):
            for x in range(256):
                px[x, y] = x % 128
        for x in range(4):
            px[x * 2, 3] = 128 + 64
            px[x + 256 - 4, 3] = 0
        self._test_buffer_overflow(im)

    def test_break_padding(self):
        im = Image.new('L', (257, 5))
        px = im.load()
        for y in range(5):
            for x in range(257):
                px[x, y] = x % 128
        for x in range(5):
            px[x, 3] = 0
        self._test_buffer_overflow(im)


if __name__ == '__main__':
    unittest.main()
