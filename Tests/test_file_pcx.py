from helper import unittest, PillowTestCase, hopper

from PIL import Image


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

        file = "Tests/images/pil184.pcx"
        im = Image.open(file)

        self.assertEqual(im.size, (447, 144))
        self.assertEqual(im.tile[0][1], (0, 0, 447, 144))

        # Make sure all pixels are either 0 or 255.
        self.assertEqual(im.histogram()[0] + im.histogram()[255], 447*144)


if __name__ == '__main__':
    unittest.main()

# End of file
