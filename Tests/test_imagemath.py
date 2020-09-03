from PIL import Image, ImageMath


def pixel(im):
    if hasattr(im, "im"):
        return "{} {}".format(im.mode, repr(im.getpixel((0, 0))))
    else:
        if isinstance(im, int):
            return int(im)  # hack to deal with booleans
        print(im)


A = Image.new("L", (1, 1), 1)
B = Image.new("L", (1, 1), 2)
Z = Image.new("L", (1, 1), 0)  # Z for zero
F = Image.new("F", (1, 1), 3)
I = Image.new("I", (1, 1), 4)  # noqa: E741

A2 = A.resize((2, 2))
B2 = B.resize((2, 2))

images = {"A": A, "B": B, "F": F, "I": I}


def test_sanity():
    assert ImageMath.eval("1") == 1
    assert ImageMath.eval("1+A", A=2) == 3
    assert pixel(ImageMath.eval("A+B", A=A, B=B)) == "I 3"
    assert pixel(ImageMath.eval("A+B", images)) == "I 3"
    assert pixel(ImageMath.eval("float(A)+B", images)) == "F 3.0"
    assert pixel(ImageMath.eval("int(float(A)+B)", images)) == "I 3"


def test_ops():
    assert pixel(ImageMath.eval("-A", images)) == "I -1"
    assert pixel(ImageMath.eval("+B", images)) == "L 2"

    assert pixel(ImageMath.eval("A+B", images)) == "I 3"
    assert pixel(ImageMath.eval("A-B", images)) == "I -1"
    assert pixel(ImageMath.eval("A*B", images)) == "I 2"
    assert pixel(ImageMath.eval("A/B", images)) == "I 0"
    assert pixel(ImageMath.eval("B**2", images)) == "I 4"
    assert pixel(ImageMath.eval("B**33", images)) == "I 2147483647"

    assert pixel(ImageMath.eval("float(A)+B", images)) == "F 3.0"
    assert pixel(ImageMath.eval("float(A)-B", images)) == "F -1.0"
    assert pixel(ImageMath.eval("float(A)*B", images)) == "F 2.0"
    assert pixel(ImageMath.eval("float(A)/B", images)) == "F 0.5"
    assert pixel(ImageMath.eval("float(B)**2", images)) == "F 4.0"
    assert pixel(ImageMath.eval("float(B)**33", images)) == "F 8589934592.0"


def test_logical():
    assert pixel(ImageMath.eval("not A", images)) == 0
    assert pixel(ImageMath.eval("A and B", images)) == "L 2"
    assert pixel(ImageMath.eval("A or B", images)) == "L 1"


def test_convert():
    assert pixel(ImageMath.eval("convert(A+B, 'L')", images)) == "L 3"
    assert pixel(ImageMath.eval("convert(A+B, '1')", images)) == "1 0"
    assert pixel(ImageMath.eval("convert(A+B, 'RGB')", images)) == "RGB (3, 3, 3)"


def test_compare():
    assert pixel(ImageMath.eval("min(A, B)", images)) == "I 1"
    assert pixel(ImageMath.eval("max(A, B)", images)) == "I 2"
    assert pixel(ImageMath.eval("A == 1", images)) == "I 1"
    assert pixel(ImageMath.eval("A == 2", images)) == "I 0"


def test_one_image_larger():
    assert pixel(ImageMath.eval("A+B", A=A2, B=B)) == "I 3"
    assert pixel(ImageMath.eval("A+B", A=A, B=B2)) == "I 3"


def test_abs():
    assert pixel(ImageMath.eval("abs(A)", A=A)) == "I 1"
    assert pixel(ImageMath.eval("abs(B)", B=B)) == "I 2"


def test_binary_mod():
    assert pixel(ImageMath.eval("A%A", A=A)) == "I 0"
    assert pixel(ImageMath.eval("B%B", B=B)) == "I 0"
    assert pixel(ImageMath.eval("A%B", A=A, B=B)) == "I 1"
    assert pixel(ImageMath.eval("B%A", A=A, B=B)) == "I 0"
    assert pixel(ImageMath.eval("Z%A", A=A, Z=Z)) == "I 0"
    assert pixel(ImageMath.eval("Z%B", B=B, Z=Z)) == "I 0"


def test_bitwise_invert():
    assert pixel(ImageMath.eval("~Z", Z=Z)) == "I -1"
    assert pixel(ImageMath.eval("~A", A=A)) == "I -2"
    assert pixel(ImageMath.eval("~B", B=B)) == "I -3"


def test_bitwise_and():
    assert pixel(ImageMath.eval("Z&Z", A=A, Z=Z)) == "I 0"
    assert pixel(ImageMath.eval("Z&A", A=A, Z=Z)) == "I 0"
    assert pixel(ImageMath.eval("A&Z", A=A, Z=Z)) == "I 0"
    assert pixel(ImageMath.eval("A&A", A=A, Z=Z)) == "I 1"


def test_bitwise_or():
    assert pixel(ImageMath.eval("Z|Z", A=A, Z=Z)) == "I 0"
    assert pixel(ImageMath.eval("Z|A", A=A, Z=Z)) == "I 1"
    assert pixel(ImageMath.eval("A|Z", A=A, Z=Z)) == "I 1"
    assert pixel(ImageMath.eval("A|A", A=A, Z=Z)) == "I 1"


def test_bitwise_xor():
    assert pixel(ImageMath.eval("Z^Z", A=A, Z=Z)) == "I 0"
    assert pixel(ImageMath.eval("Z^A", A=A, Z=Z)) == "I 1"
    assert pixel(ImageMath.eval("A^Z", A=A, Z=Z)) == "I 1"
    assert pixel(ImageMath.eval("A^A", A=A, Z=Z)) == "I 0"


def test_bitwise_leftshift():
    assert pixel(ImageMath.eval("Z<<0", Z=Z)) == "I 0"
    assert pixel(ImageMath.eval("Z<<1", Z=Z)) == "I 0"
    assert pixel(ImageMath.eval("A<<0", A=A)) == "I 1"
    assert pixel(ImageMath.eval("A<<1", A=A)) == "I 2"


def test_bitwise_rightshift():
    assert pixel(ImageMath.eval("Z>>0", Z=Z)) == "I 0"
    assert pixel(ImageMath.eval("Z>>1", Z=Z)) == "I 0"
    assert pixel(ImageMath.eval("A>>0", A=A)) == "I 1"
    assert pixel(ImageMath.eval("A>>1", A=A)) == "I 0"


def test_logical_eq():
    assert pixel(ImageMath.eval("A==A", A=A)) == "I 1"
    assert pixel(ImageMath.eval("B==B", B=B)) == "I 1"
    assert pixel(ImageMath.eval("A==B", A=A, B=B)) == "I 0"
    assert pixel(ImageMath.eval("B==A", A=A, B=B)) == "I 0"


def test_logical_ne():
    assert pixel(ImageMath.eval("A!=A", A=A)) == "I 0"
    assert pixel(ImageMath.eval("B!=B", B=B)) == "I 0"
    assert pixel(ImageMath.eval("A!=B", A=A, B=B)) == "I 1"
    assert pixel(ImageMath.eval("B!=A", A=A, B=B)) == "I 1"


def test_logical_lt():
    assert pixel(ImageMath.eval("A<A", A=A)) == "I 0"
    assert pixel(ImageMath.eval("B<B", B=B)) == "I 0"
    assert pixel(ImageMath.eval("A<B", A=A, B=B)) == "I 1"
    assert pixel(ImageMath.eval("B<A", A=A, B=B)) == "I 0"


def test_logical_le():
    assert pixel(ImageMath.eval("A<=A", A=A)) == "I 1"
    assert pixel(ImageMath.eval("B<=B", B=B)) == "I 1"
    assert pixel(ImageMath.eval("A<=B", A=A, B=B)) == "I 1"
    assert pixel(ImageMath.eval("B<=A", A=A, B=B)) == "I 0"


def test_logical_gt():
    assert pixel(ImageMath.eval("A>A", A=A)) == "I 0"
    assert pixel(ImageMath.eval("B>B", B=B)) == "I 0"
    assert pixel(ImageMath.eval("A>B", A=A, B=B)) == "I 0"
    assert pixel(ImageMath.eval("B>A", A=A, B=B)) == "I 1"


def test_logical_ge():
    assert pixel(ImageMath.eval("A>=A", A=A)) == "I 1"
    assert pixel(ImageMath.eval("B>=B", B=B)) == "I 1"
    assert pixel(ImageMath.eval("A>=B", A=A, B=B)) == "I 0"
    assert pixel(ImageMath.eval("B>=A", A=A, B=B)) == "I 1"


def test_logical_equal():
    assert pixel(ImageMath.eval("equal(A, A)", A=A)) == "I 1"
    assert pixel(ImageMath.eval("equal(B, B)", B=B)) == "I 1"
    assert pixel(ImageMath.eval("equal(Z, Z)", Z=Z)) == "I 1"
    assert pixel(ImageMath.eval("equal(A, B)", A=A, B=B)) == "I 0"
    assert pixel(ImageMath.eval("equal(B, A)", A=A, B=B)) == "I 0"
    assert pixel(ImageMath.eval("equal(A, Z)", A=A, Z=Z)) == "I 0"


def test_logical_not_equal():
    assert pixel(ImageMath.eval("notequal(A, A)", A=A)) == "I 0"
    assert pixel(ImageMath.eval("notequal(B, B)", B=B)) == "I 0"
    assert pixel(ImageMath.eval("notequal(Z, Z)", Z=Z)) == "I 0"
    assert pixel(ImageMath.eval("notequal(A, B)", A=A, B=B)) == "I 1"
    assert pixel(ImageMath.eval("notequal(B, A)", A=A, B=B)) == "I 1"
    assert pixel(ImageMath.eval("notequal(A, Z)", A=A, Z=Z)) == "I 1"
