from __future__ import annotations

from typing import Any

import pytest

from PIL import Image, ImageMath


def pixel(im: Image.Image | int) -> str | int:
    if isinstance(im, int):
        return int(im)  # hack to deal with booleans

    return f"{im.mode} {repr(im.getpixel((0, 0)))}"


A = Image.new("L", (1, 1), 1)
B = Image.new("L", (1, 1), 2)
Z = Image.new("L", (1, 1), 0)  # Z for zero
F = Image.new("F", (1, 1), 3)
I = Image.new("I", (1, 1), 4)  # noqa: E741

A2 = A.resize((2, 2))
B2 = B.resize((2, 2))

images: dict[str, Any] = {"A": A, "B": B, "F": F, "I": I}


def test_sanity() -> None:
    assert ImageMath.unsafe_eval("1") == 1
    assert ImageMath.unsafe_eval("1+A", A=2) == 3
    assert pixel(ImageMath.unsafe_eval("A+B", A=A, B=B)) == "I 3"
    assert pixel(ImageMath.unsafe_eval("A+B", **images)) == "I 3"
    assert pixel(ImageMath.unsafe_eval("float(A)+B", **images)) == "F 3.0"
    assert pixel(ImageMath.unsafe_eval("int(float(A)+B)", **images)) == "I 3"


def test_eval_deprecated() -> None:
    with pytest.warns(DeprecationWarning, match="ImageMath.eval"):
        assert ImageMath.eval("1") == 1


def test_options_deprecated() -> None:
    with pytest.warns(DeprecationWarning, match="ImageMath.unsafe_eval options"):
        assert ImageMath.unsafe_eval("1", images) == 1


def test_ops() -> None:
    assert pixel(ImageMath.unsafe_eval("-A", **images)) == "I -1"
    assert pixel(ImageMath.unsafe_eval("+B", **images)) == "L 2"

    assert pixel(ImageMath.unsafe_eval("A+B", **images)) == "I 3"
    assert pixel(ImageMath.unsafe_eval("A-B", **images)) == "I -1"
    assert pixel(ImageMath.unsafe_eval("A*B", **images)) == "I 2"
    assert pixel(ImageMath.unsafe_eval("A/B", **images)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("B**2", **images)) == "I 4"
    assert pixel(ImageMath.unsafe_eval("B**33", **images)) == "I 2147483647"

    assert pixel(ImageMath.unsafe_eval("float(A)+B", **images)) == "F 3.0"
    assert pixel(ImageMath.unsafe_eval("float(A)-B", **images)) == "F -1.0"
    assert pixel(ImageMath.unsafe_eval("float(A)*B", **images)) == "F 2.0"
    assert pixel(ImageMath.unsafe_eval("float(A)/B", **images)) == "F 0.5"
    assert pixel(ImageMath.unsafe_eval("float(B)**2", **images)) == "F 4.0"
    assert pixel(ImageMath.unsafe_eval("float(B)**33", **images)) == "F 8589934592.0"


@pytest.mark.parametrize(
    "expression",
    (
        "exec('pass')",
        "(lambda: exec('pass'))()",
        "(lambda: (lambda: exec('pass'))())()",
    ),
)
def test_prevent_exec(expression: str) -> None:
    with pytest.raises(ValueError):
        ImageMath.unsafe_eval(expression)


def test_prevent_double_underscores() -> None:
    with pytest.raises(ValueError):
        ImageMath.unsafe_eval("1", __=None)


def test_prevent_builtins() -> None:
    with pytest.raises(ValueError):
        ImageMath.unsafe_eval("(lambda: exec('exit()'))()", exec=None)


def test_logical() -> None:
    assert pixel(ImageMath.unsafe_eval("not A", **images)) == 0
    assert pixel(ImageMath.unsafe_eval("A and B", **images)) == "L 2"
    assert pixel(ImageMath.unsafe_eval("A or B", **images)) == "L 1"


def test_convert() -> None:
    assert pixel(ImageMath.unsafe_eval("convert(A+B, 'L')", **images)) == "L 3"
    assert pixel(ImageMath.unsafe_eval("convert(A+B, '1')", **images)) == "1 0"
    assert (
        pixel(ImageMath.unsafe_eval("convert(A+B, 'RGB')", **images)) == "RGB (3, 3, 3)"
    )


def test_compare() -> None:
    assert pixel(ImageMath.unsafe_eval("min(A, B)", **images)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("max(A, B)", **images)) == "I 2"
    assert pixel(ImageMath.unsafe_eval("A == 1", **images)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("A == 2", **images)) == "I 0"


def test_one_image_larger() -> None:
    assert pixel(ImageMath.unsafe_eval("A+B", A=A2, B=B)) == "I 3"
    assert pixel(ImageMath.unsafe_eval("A+B", A=A, B=B2)) == "I 3"


def test_abs() -> None:
    assert pixel(ImageMath.unsafe_eval("abs(A)", A=A)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("abs(B)", B=B)) == "I 2"


def test_binary_mod() -> None:
    assert pixel(ImageMath.unsafe_eval("A%A", A=A)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("B%B", B=B)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("A%B", A=A, B=B)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("B%A", A=A, B=B)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("Z%A", A=A, Z=Z)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("Z%B", B=B, Z=Z)) == "I 0"


def test_bitwise_invert() -> None:
    assert pixel(ImageMath.unsafe_eval("~Z", Z=Z)) == "I -1"
    assert pixel(ImageMath.unsafe_eval("~A", A=A)) == "I -2"
    assert pixel(ImageMath.unsafe_eval("~B", B=B)) == "I -3"


def test_bitwise_and() -> None:
    assert pixel(ImageMath.unsafe_eval("Z&Z", A=A, Z=Z)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("Z&A", A=A, Z=Z)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("A&Z", A=A, Z=Z)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("A&A", A=A, Z=Z)) == "I 1"


def test_bitwise_or() -> None:
    assert pixel(ImageMath.unsafe_eval("Z|Z", A=A, Z=Z)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("Z|A", A=A, Z=Z)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("A|Z", A=A, Z=Z)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("A|A", A=A, Z=Z)) == "I 1"


def test_bitwise_xor() -> None:
    assert pixel(ImageMath.unsafe_eval("Z^Z", A=A, Z=Z)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("Z^A", A=A, Z=Z)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("A^Z", A=A, Z=Z)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("A^A", A=A, Z=Z)) == "I 0"


def test_bitwise_leftshift() -> None:
    assert pixel(ImageMath.unsafe_eval("Z<<0", Z=Z)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("Z<<1", Z=Z)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("A<<0", A=A)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("A<<1", A=A)) == "I 2"


def test_bitwise_rightshift() -> None:
    assert pixel(ImageMath.unsafe_eval("Z>>0", Z=Z)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("Z>>1", Z=Z)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("A>>0", A=A)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("A>>1", A=A)) == "I 0"


def test_logical_eq() -> None:
    assert pixel(ImageMath.unsafe_eval("A==A", A=A)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("B==B", B=B)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("A==B", A=A, B=B)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("B==A", A=A, B=B)) == "I 0"


def test_logical_ne() -> None:
    assert pixel(ImageMath.unsafe_eval("A!=A", A=A)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("B!=B", B=B)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("A!=B", A=A, B=B)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("B!=A", A=A, B=B)) == "I 1"


def test_logical_lt() -> None:
    assert pixel(ImageMath.unsafe_eval("A<A", A=A)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("B<B", B=B)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("A<B", A=A, B=B)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("B<A", A=A, B=B)) == "I 0"


def test_logical_le() -> None:
    assert pixel(ImageMath.unsafe_eval("A<=A", A=A)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("B<=B", B=B)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("A<=B", A=A, B=B)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("B<=A", A=A, B=B)) == "I 0"


def test_logical_gt() -> None:
    assert pixel(ImageMath.unsafe_eval("A>A", A=A)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("B>B", B=B)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("A>B", A=A, B=B)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("B>A", A=A, B=B)) == "I 1"


def test_logical_ge() -> None:
    assert pixel(ImageMath.unsafe_eval("A>=A", A=A)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("B>=B", B=B)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("A>=B", A=A, B=B)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("B>=A", A=A, B=B)) == "I 1"


def test_logical_equal() -> None:
    assert pixel(ImageMath.unsafe_eval("equal(A, A)", A=A)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("equal(B, B)", B=B)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("equal(Z, Z)", Z=Z)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("equal(A, B)", A=A, B=B)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("equal(B, A)", A=A, B=B)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("equal(A, Z)", A=A, Z=Z)) == "I 0"


def test_logical_not_equal() -> None:
    assert pixel(ImageMath.unsafe_eval("notequal(A, A)", A=A)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("notequal(B, B)", B=B)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("notequal(Z, Z)", Z=Z)) == "I 0"
    assert pixel(ImageMath.unsafe_eval("notequal(A, B)", A=A, B=B)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("notequal(B, A)", A=A, B=B)) == "I 1"
    assert pixel(ImageMath.unsafe_eval("notequal(A, Z)", A=A, Z=Z)) == "I 1"
