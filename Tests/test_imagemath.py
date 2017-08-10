from __future__ import print_function
from helper import unittest, PillowTestCase

from PIL import Image
from PIL import ImageMath


def pixel(im):
    if hasattr(im, "im"):
        return "%s %r" % (im.mode, im.getpixel((0, 0)))
    else:
        if isinstance(im, int):
            return int(im)  # hack to deal with booleans
        print(im)

A = Image.new("L", (1, 1), 1)
B = Image.new("L", (1, 1), 2)
Z = Image.new("L", (1, 1), 0)  # Z for zero
F = Image.new("F", (1, 1), 3)
I = Image.new("I", (1, 1), 4)

A2 = A.resize((2, 2))
B2 = B.resize((2, 2))

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

    def test_one_image_larger(self):
        self.assertEqual(pixel(ImageMath.eval("A+B", A=A2, B=B)), "I 3")
        self.assertEqual(pixel(ImageMath.eval("A+B", A=A, B=B2)), "I 3")

    def test_abs(self):
        self.assertEqual(pixel(ImageMath.eval("abs(A)", A=A)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("abs(B)", B=B)), "I 2")

    def test_binary_mod(self):
        self.assertEqual(pixel(ImageMath.eval("A%A", A=A)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("B%B", B=B)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("A%B", A=A, B=B)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("B%A", A=A, B=B)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("Z%A", A=A, Z=Z)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("Z%B", B=B, Z=Z)), "I 0")

    def test_bitwise_invert(self):
        self.assertEqual(pixel(ImageMath.eval("~Z", Z=Z)), "I -1")
        self.assertEqual(pixel(ImageMath.eval("~A", A=A)), "I -2")
        self.assertEqual(pixel(ImageMath.eval("~B", B=B)), "I -3")

    def test_bitwise_and(self):
        self.assertEqual(pixel(ImageMath.eval("Z&Z", A=A, Z=Z)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("Z&A", A=A, Z=Z)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("A&Z", A=A, Z=Z)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("A&A", A=A, Z=Z)), "I 1")

    def test_bitwise_or(self):
        self.assertEqual(pixel(ImageMath.eval("Z|Z", A=A, Z=Z)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("Z|A", A=A, Z=Z)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("A|Z", A=A, Z=Z)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("A|A", A=A, Z=Z)), "I 1")

    def test_bitwise_xor(self):
        self.assertEqual(pixel(ImageMath.eval("Z^Z", A=A, Z=Z)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("Z^A", A=A, Z=Z)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("A^Z", A=A, Z=Z)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("A^A", A=A, Z=Z)), "I 0")

    def test_bitwise_leftshift(self):
        self.assertEqual(pixel(ImageMath.eval("Z<<0", Z=Z)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("Z<<1", Z=Z)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("A<<0", A=A)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("A<<1", A=A)), "I 2")

    def test_bitwise_rightshift(self):
        self.assertEqual(pixel(ImageMath.eval("Z>>0", Z=Z)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("Z>>1", Z=Z)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("A>>0", A=A)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("A>>1", A=A)), "I 0")

    def test_logical_eq(self):
        self.assertEqual(pixel(ImageMath.eval("A==A", A=A)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("B==B", B=B)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("A==B", A=A, B=B)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("B==A", A=A, B=B)), "I 0")

    def test_logical_ne(self):
        self.assertEqual(pixel(ImageMath.eval("A!=A", A=A)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("B!=B", B=B)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("A!=B", A=A, B=B)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("B!=A", A=A, B=B)), "I 1")

    def test_logical_lt(self):
        self.assertEqual(pixel(ImageMath.eval("A<A", A=A)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("B<B", B=B)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("A<B", A=A, B=B)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("B<A", A=A, B=B)), "I 0")

    def test_logical_le(self):
        self.assertEqual(pixel(ImageMath.eval("A<=A", A=A)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("B<=B", B=B)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("A<=B", A=A, B=B)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("B<=A", A=A, B=B)), "I 0")

    def test_logical_gt(self):
        self.assertEqual(pixel(ImageMath.eval("A>A", A=A)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("B>B", B=B)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("A>B", A=A, B=B)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("B>A", A=A, B=B)), "I 1")

    def test_logical_ge(self):
        self.assertEqual(pixel(ImageMath.eval("A>=A", A=A)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("B>=B", B=B)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("A>=B", A=A, B=B)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("B>=A", A=A, B=B)), "I 1")

    def test_logical_equal(self):
        self.assertEqual(pixel(ImageMath.eval("equal(A, A)", A=A)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("equal(B, B)", B=B)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("equal(Z, Z)", Z=Z)), "I 1")
        self.assertEqual(pixel(ImageMath.eval("equal(A, B)", A=A, B=B)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("equal(B, A)", A=A, B=B)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("equal(A, Z)", A=A, Z=Z)), "I 0")

    def test_logical_not_equal(self):
        self.assertEqual(pixel(ImageMath.eval("notequal(A, A)", A=A)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("notequal(B, B)", B=B)), "I 0")
        self.assertEqual(pixel(ImageMath.eval("notequal(Z, Z)", Z=Z)), "I 0")
        self.assertEqual(
            pixel(ImageMath.eval("notequal(A, B)", A=A, B=B)), "I 1")
        self.assertEqual(
            pixel(ImageMath.eval("notequal(B, A)", A=A, B=B)), "I 1")
        self.assertEqual(
            pixel(ImageMath.eval("notequal(A, Z)", A=A, Z=Z)), "I 1")


if __name__ == '__main__':
    unittest.main()
