from helper import unittest, PillowTestCase, hopper

from PIL import Image


class TestImageQuantize(PillowTestCase):

    def test_sanity(self):
        image = hopper()
        converted = image.quantize()
        self.assert_image(converted, 'P', converted.size)
        self.assert_image_similar(converted.convert('RGB'), image, 10)

        image = hopper()
        converted = image.quantize(palette=hopper('P'))
        self.assert_image(converted, 'P', converted.size)
        self.assert_image_similar(converted.convert('RGB'), image, 60)

    def test_libimagequant_quantize(self):
        image = hopper()
        try:
            converted = image.quantize(100, Image.LIBIMAGEQUANT)
        except ValueError as ex:
            if 'dependency' in str(ex).lower():
                self.skipTest('libimagequant support not available')
            else:
                raise
        self.assert_image(converted, 'P', converted.size)
        self.assert_image_similar(converted.convert('RGB'), image, 15)
        assert len(converted.getcolors()) == 100

    def test_octree_quantize(self):
        image = hopper()
        converted = image.quantize(100, Image.FASTOCTREE)
        self.assert_image(converted, 'P', converted.size)
        self.assert_image_similar(converted.convert('RGB'), image, 20)
        assert len(converted.getcolors()) == 100

    def test_rgba_quantize(self):
        image = hopper('RGBA')
        image.quantize()
        self.assertRaises(Exception, lambda: image.quantize(method=0))

    def test_quantize(self):
        image = Image.open('Tests/images/caption_6_33_22.png').convert('RGB')
        converted = image.quantize()
        self.assert_image(converted, 'P', converted.size)
        self.assert_image_similar(converted.convert('RGB'), image, 1)


if __name__ == '__main__':
    unittest.main()
