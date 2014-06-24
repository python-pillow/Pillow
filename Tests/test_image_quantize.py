from helper import unittest, PillowTestCase, tearDownModule, lena

from PIL import Image


class TestImageQuantize(PillowTestCase):

    def test_sanity(self):
        im = lena()

        im = im.quantize()
        self.assert_image(im, "P", im.size)

        im = lena()
        im = im.quantize(palette=lena("P"))
        self.assert_image(im, "P", im.size)

    def test_octree_quantize(self):
        im = lena()

        im = im.quantize(100, Image.FASTOCTREE)
        self.assert_image(im, "P", im.size)

        assert len(im.getcolors()) == 100

    def test_rgba_quantize(self):
        im = lena('RGBA')
        im.quantize()
        self.assertRaises(Exception, lambda: im.quantize(method=0))


if __name__ == '__main__':
    unittest.main()

# End of file
