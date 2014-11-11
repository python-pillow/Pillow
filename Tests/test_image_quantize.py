from helper import unittest, PillowTestCase, hopper

from PIL import Image


class TestImageQuantize(PillowTestCase):

    def test_sanity(self):
        im = hopper()

        im = im.quantize()
        self.assert_image(im, "P", im.size)

        im = hopper()
        im = im.quantize(palette=hopper("P"))
        self.assert_image(im, "P", im.size)

    def test_octree_quantize(self):
        im = hopper()

        im = im.quantize(100, Image.FASTOCTREE)
        self.assert_image(im, "P", im.size)

        assert len(im.getcolors()) == 100

    def test_rgba_quantize(self):
        im = hopper('RGBA')
        im.quantize()
        self.assertRaises(Exception, lambda: im.quantize(method=0))


if __name__ == '__main__':
    unittest.main()

# End of file
