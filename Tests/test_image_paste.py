from helper import unittest, PillowTestCase, hopper

from PIL import Image


class TestImagingPaste(PillowTestCase):
    masks = {}

    def mask_1(self, size):
        mask = Image.new('1', size)
        px = mask.load()
        for y in range(mask.height):
            for x in range(mask.width):
                px[y, x] = (x + y) % 2
        return mask

    def mask_L(self, size):
        mask = Image.new('L', size)
        px = mask.load()
        for y in range(mask.height):
            for x in range(mask.width):
                px[y, x] = (x + y) % 255
        return mask

    def mask_RGBA(self, size):
        mask = Image.new('RGB', size, 'red').split()
        return Image.merge('RGBA', mask + (self.mask_L(size),))

    def mask_RGBa(self, size):
        mask = Image.new('RGB', size, 'red').split()
        return Image.merge('RGBa', mask + (self.mask_L(size),))

    def test_image_solid(self):
        for mode in ('L', 'RGB'):
            im = Image.new(mode, (200, 200), 'red')
            im2 = hopper(mode)

            im.paste(im2, (0, 0))

            im = im.crop((0, 0) + im2.size)
            self.assert_image_equal(im, im2)

    def test_image_mask_1(self):
        for mode in ('L', 'RGB'):
            im = Image.new(mode, (200, 200), 'red')
            im2 = hopper(mode)
            mask = self.mask_1(im2.size)

            im.paste(im2, (0, 0), mask)

    def test_image_mask_L(self):
        for mode in ('L', 'RGB'):
            im = Image.new(mode, (200, 200), 'red')
            im2 = hopper(mode)
            mask = self.mask_L(im2.size)

            im.paste(im2, (0, 0), mask)

    def test_image_mask_RGBA(self):
        for mode in ('L', 'RGB'):
            im = Image.new(mode, (200, 200), 'red')
            im2 = hopper(mode)
            mask = self.mask_RGBA(im2.size)

            im.paste(im2, (0, 0), mask)

    def test_image_mask_RGBa(self):
        for mode in ('L', 'RGB'):
            im = Image.new(mode, (200, 200), 'red')
            im2 = hopper(mode)
            mask = self.mask_RGBa(im2.size)

            im.paste(im2, (0, 0), mask)

    def test_color_solid(self):
        for mode in ('L', 'RGB'):
            im = hopper(mode)
            im2 = 'red'

            im.paste(im2)

    def test_color_mask_1(self):
        for mode in ('L', 'RGB'):
            im = hopper(mode)
            im2 = 'red'
            mask = self.mask_1(im.size)

            im.paste(im2, (0, 0), mask)

    def test_color_mask_L(self):
        for mode in ('L', 'RGB'):
            im = hopper(mode)
            im2 = 'red'
            mask = self.mask_L(im.size)

            im.paste(im2, (0, 0), mask)

    def test_color_mask_RGBA(self):
        for mode in ('L', 'RGB'):
            im = hopper(mode)
            im2 = 'red'
            mask = self.mask_RGBA(im.size)

            im.paste(im2, (0, 0), mask)

    def test_color_mask_RGBa(self):
        for mode in ('L', 'RGB'):
            im = hopper(mode)
            im2 = 'red'
            mask = self.mask_RGBa(im.size)

            im.paste(im2, (0, 0), mask)
