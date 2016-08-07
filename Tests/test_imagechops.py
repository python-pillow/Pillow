from helper import unittest, PillowTestCase, hopper

from PIL import Image
from PIL import ImageChops


class TestImageChops(PillowTestCase):

    def test_sanity(self):

        im = hopper("L")

        ImageChops.constant(im, 128)
        ImageChops.duplicate(im)
        ImageChops.invert(im)
        ImageChops.lighter(im, im)
        ImageChops.darker(im, im)
        ImageChops.difference(im, im)
        ImageChops.multiply(im, im)
        ImageChops.screen(im, im)

        ImageChops.add(im, im)
        ImageChops.add(im, im, 2.0)
        ImageChops.add(im, im, 2.0, 128)
        ImageChops.subtract(im, im)
        ImageChops.subtract(im, im, 2.0)
        ImageChops.subtract(im, im, 2.0, 128)

        ImageChops.add_modulo(im, im)
        ImageChops.subtract_modulo(im, im)

        ImageChops.blend(im, im, 0.5)
        ImageChops.composite(im, im, im)

        ImageChops.offset(im, 10)
        ImageChops.offset(im, 10, 20)

    def test_logical(self):

        def table(op, a, b):
            out = []
            for x in (a, b):
                imx = Image.new("1", (1, 1), x)
                for y in (a, b):
                    imy = Image.new("1", (1, 1), y)
                    out.append(op(imx, imy).getpixel((0, 0)))
            return tuple(out)

        self.assertEqual(
            table(ImageChops.logical_and, 0, 1), (0, 0, 0, 255))
        self.assertEqual(
            table(ImageChops.logical_or, 0, 1), (0, 255, 255, 255))
        self.assertEqual(
            table(ImageChops.logical_xor, 0, 1), (0, 255, 255, 0))

        self.assertEqual(
            table(ImageChops.logical_and, 0, 128), (0, 0, 0, 255))
        self.assertEqual(
            table(ImageChops.logical_or, 0, 128), (0, 255, 255, 255))
        self.assertEqual(
            table(ImageChops.logical_xor, 0, 128), (0, 255, 255, 0))

        self.assertEqual(
            table(ImageChops.logical_and, 0, 255), (0, 0, 0, 255))
        self.assertEqual(
            table(ImageChops.logical_or, 0, 255), (0, 255, 255, 255))
        self.assertEqual(
            table(ImageChops.logical_xor, 0, 255), (0, 255, 255, 0))


if __name__ == '__main__':
    unittest.main()
