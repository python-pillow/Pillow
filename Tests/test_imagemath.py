from helper import unittest, PillowTestCase, tearDownModule

from PIL import Image
from PIL import ImageMath


def pixel(im):
    if hasattr(im, "im"):
        return "%s %r" % (im.mode, im.getpixel((0, 0)))
    else:
        if isinstance(im, type(0)):
            return int(im)  # hack to deal with booleans
        print(im)

A = Image.new("L", (1, 1), 1)
B = Image.new("L", (1, 1), 2)
F = Image.new("F", (1, 1), 3)
I = Image.new("I", (1, 1), 4)

images = {"A": A, "B": B, "F": F, "I": I}


class TestImageMath(PillowTestCase):

    def test_sanity(self):
        self.assertEqual(ImageMath.eval("1"), 1)
        self.assertEqual(ImageMath.eval("1+A", A=2), 3)
        self.assertEqual(pixel(ImageMath.eval("A+B", A=A, B=B)), "I 3")
        self.assertEqual(pixel(ImageMath.eval("A+B", images)), "I 3")
        self.assertEqual(pixel(ImageMath.eval("float(A)+B", images)), "F 3.0")
        self.assertEqual(pixel(
            ImageMath.eval("int(float(A)+B)", images)), "I 3")

    def test_ops(self):

        self.assertEqual(pixel(ImageMath.eval("-A", images)), "I -1")
        self.assertEqual(pixel(ImageMath.eval("+B", images)), "L 2")

        self.assertEqual(pixel(ImageMath.eval("A+B", images)), "I 3")
        self.assertEqual(pixel(ImageMath.eval("A-B", images)), "I -1")
        self.assertEqual(pixel(ImageMath.eval("A*B", images)), "I 2")
        self.assertEqual(pixel(ImageMath.eval("A/B", images)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("B**2", images)), "I 4")
        self.assertEqual(pixel(
            ImageMath.eval("B**33", images)), "I 2147483647")

        self.assertEqual(pixel(ImageMath.eval("float(A)+B", images)), "F 3.0")
        self.assertEqual(pixel(ImageMath.eval("float(A)-B", images)), "F -1.0")
        self.assertEqual(pixel(ImageMath.eval("float(A)*B", images)), "F 2.0")
        self.assertEqual(pixel(ImageMath.eval("float(A)/B", images)), "F 0.5")
        self.assertEqual(pixel(ImageMath.eval("float(B)**2", images)), "F 4.0")
        self.assertEqual(pixel(
            ImageMath.eval("float(B)**33", images)), "F 8589934592.0")

    def test_logical(self):
        self.assertEqual(pixel(ImageMath.eval("not A", images)), 0)
        self.assertEqual(pixel(ImageMath.eval("A and B", images)), "L 2")
        self.assertEqual(pixel(ImageMath.eval("A or B", images)), "L 1")

    def test_convert(self):
        self.assertEqual(pixel(
            ImageMath.eval("convert(A+B, 'L')", images)), "L 3")
        self.assertEqual(pixel(
            ImageMath.eval("convert(A+B, '1')", images)), "1 0")
        self.assertEqual(pixel(
            ImageMath.eval("convert(A+B, 'RGB')", images)), "RGB (3, 3, 3)")

    def test_compare(self):
        self.assertEqual(pixel(ImageMath.eval("min(A, B)", images)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("max(A, B)", images)), "I 2")
        self.assertEqual(pixel(ImageMath.eval("A == 1", images)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("A == 2", images)), "I 0")


if __name__ == '__main__':
    unittest.main()

# End of file
