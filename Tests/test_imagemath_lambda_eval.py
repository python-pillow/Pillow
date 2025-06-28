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
    assert ImageMath.lambda_eval(lambda args: 1) == 1
    assert ImageMath.lambda_eval(lambda args: 1 + args["A"], A=2) == 3
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] + args["B"], A=A, B=B))
        == "I 3"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] + args["B"], **images))
        == "I 3"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["float"](args["A"]) + args["B"], **images
            )
        )
        == "F 3.0"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["int"](args["float"](args["A"]) + args["B"]), **images
            )
        )
        == "I 3"
    )


def test_options_deprecated() -> None:
    with pytest.warns(DeprecationWarning, match="ImageMath.lambda_eval options"):
        assert ImageMath.lambda_eval(lambda args: 1, images) == 1


def test_ops() -> None:
    assert pixel(ImageMath.lambda_eval(lambda args: args["A"] * -1, **images)) == "I -1"

    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] + args["B"], **images))
        == "I 3"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] - args["B"], **images))
        == "I -1"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] * args["B"], **images))
        == "I 2"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] / args["B"], **images))
        == "I 0"
    )
    assert pixel(ImageMath.lambda_eval(lambda args: args["B"] ** 2, **images)) == "I 4"
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["B"] ** 33, **images))
        == "I 2147483647"
    )

    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["float"](args["A"]) + args["B"], **images
            )
        )
        == "F 3.0"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["float"](args["A"]) - args["B"], **images
            )
        )
        == "F -1.0"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["float"](args["A"]) * args["B"], **images
            )
        )
        == "F 2.0"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["float"](args["A"]) / args["B"], **images
            )
        )
        == "F 0.5"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(lambda args: args["float"](args["B"]) ** 2, **images)
        )
        == "F 4.0"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(lambda args: args["float"](args["B"]) ** 33, **images)
        )
        == "F 8589934592.0"
    )


def test_logical() -> None:
    assert pixel(ImageMath.lambda_eval(lambda args: not args["A"], **images)) == 0
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] and args["B"], **images))
        == "L 2"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] or args["B"], **images))
        == "L 1"
    )


def test_convert() -> None:
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["convert"](args["A"] + args["B"], "L"), **images
            )
        )
        == "L 3"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["convert"](args["A"] + args["B"], "1"), **images
            )
        )
        == "1 0"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["convert"](args["A"] + args["B"], "RGB"), **images
            )
        )
        == "RGB (3, 3, 3)"
    )


def test_compare() -> None:
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["min"](args["A"], args["B"]), **images
            )
        )
        == "I 1"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["max"](args["A"], args["B"]), **images
            )
        )
        == "I 2"
    )
    assert pixel(ImageMath.lambda_eval(lambda args: args["A"] == 1, **images)) == "I 1"
    assert pixel(ImageMath.lambda_eval(lambda args: args["A"] == 2, **images)) == "I 0"


def test_one_image_larger() -> None:
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] + args["B"], A=A2, B=B))
        == "I 3"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] + args["B"], A=A, B=B2))
        == "I 3"
    )


def test_abs() -> None:
    assert pixel(ImageMath.lambda_eval(lambda args: abs(args["A"]), A=A)) == "I 1"
    assert pixel(ImageMath.lambda_eval(lambda args: abs(args["B"]), B=B)) == "I 2"


def test_binary_mod() -> None:
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] % args["A"], A=A)) == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["B"] % args["B"], B=B)) == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] % args["B"], A=A, B=B))
        == "I 1"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["B"] % args["A"], A=A, B=B))
        == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["Z"] % args["A"], A=A, Z=Z))
        == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["Z"] % args["B"], B=B, Z=Z))
        == "I 0"
    )


def test_bitwise_invert() -> None:
    assert pixel(ImageMath.lambda_eval(lambda args: ~args["Z"], Z=Z)) == "I -1"
    assert pixel(ImageMath.lambda_eval(lambda args: ~args["A"], A=A)) == "I -2"
    assert pixel(ImageMath.lambda_eval(lambda args: ~args["B"], B=B)) == "I -3"


def test_bitwise_and() -> None:
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["Z"] & args["Z"], A=A, Z=Z))
        == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["Z"] & args["A"], A=A, Z=Z))
        == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] & args["Z"], A=A, Z=Z))
        == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] & args["A"], A=A, Z=Z))
        == "I 1"
    )


def test_bitwise_or() -> None:
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["Z"] | args["Z"], A=A, Z=Z))
        == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["Z"] | args["A"], A=A, Z=Z))
        == "I 1"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] | args["Z"], A=A, Z=Z))
        == "I 1"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] | args["A"], A=A, Z=Z))
        == "I 1"
    )


def test_bitwise_xor() -> None:
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["Z"] ^ args["Z"], A=A, Z=Z))
        == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["Z"] ^ args["A"], A=A, Z=Z))
        == "I 1"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] ^ args["Z"], A=A, Z=Z))
        == "I 1"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] ^ args["A"], A=A, Z=Z))
        == "I 0"
    )


def test_bitwise_leftshift() -> None:
    assert pixel(ImageMath.lambda_eval(lambda args: args["Z"] << 0, Z=Z)) == "I 0"
    assert pixel(ImageMath.lambda_eval(lambda args: args["Z"] << 1, Z=Z)) == "I 0"
    assert pixel(ImageMath.lambda_eval(lambda args: args["A"] << 0, A=A)) == "I 1"
    assert pixel(ImageMath.lambda_eval(lambda args: args["A"] << 1, A=A)) == "I 2"


def test_bitwise_rightshift() -> None:
    assert pixel(ImageMath.lambda_eval(lambda args: args["Z"] >> 0, Z=Z)) == "I 0"
    assert pixel(ImageMath.lambda_eval(lambda args: args["Z"] >> 1, Z=Z)) == "I 0"
    assert pixel(ImageMath.lambda_eval(lambda args: args["A"] >> 0, A=A)) == "I 1"
    assert pixel(ImageMath.lambda_eval(lambda args: args["A"] >> 1, A=A)) == "I 0"


def test_logical_eq() -> None:
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] == args["A"], A=A)) == "I 1"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["B"] == args["B"], B=B)) == "I 1"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] == args["B"], A=A, B=B))
        == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["B"] == args["A"], A=A, B=B))
        == "I 0"
    )


def test_logical_ne() -> None:
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] != args["A"], A=A)) == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["B"] != args["B"], B=B)) == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] != args["B"], A=A, B=B))
        == "I 1"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["B"] != args["A"], A=A, B=B))
        == "I 1"
    )


def test_logical_lt() -> None:
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] < args["A"], A=A)) == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["B"] < args["B"], B=B)) == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] < args["B"], A=A, B=B))
        == "I 1"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["B"] < args["A"], A=A, B=B))
        == "I 0"
    )


def test_logical_le() -> None:
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] <= args["A"], A=A)) == "I 1"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["B"] <= args["B"], B=B)) == "I 1"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] <= args["B"], A=A, B=B))
        == "I 1"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["B"] <= args["A"], A=A, B=B))
        == "I 0"
    )


def test_logical_gt() -> None:
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] > args["A"], A=A)) == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["B"] > args["B"], B=B)) == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] > args["B"], A=A, B=B))
        == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["B"] > args["A"], A=A, B=B))
        == "I 1"
    )


def test_logical_ge() -> None:
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] >= args["A"], A=A)) == "I 1"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["B"] >= args["B"], B=B)) == "I 1"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["A"] >= args["B"], A=A, B=B))
        == "I 0"
    )
    assert (
        pixel(ImageMath.lambda_eval(lambda args: args["B"] >= args["A"], A=A, B=B))
        == "I 1"
    )


def test_logical_equal() -> None:
    assert (
        pixel(
            ImageMath.lambda_eval(lambda args: args["equal"](args["A"], args["A"]), A=A)
        )
        == "I 1"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(lambda args: args["equal"](args["B"], args["B"]), B=B)
        )
        == "I 1"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(lambda args: args["equal"](args["Z"], args["Z"]), Z=Z)
        )
        == "I 1"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["equal"](args["A"], args["B"]), A=A, B=B
            )
        )
        == "I 0"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["equal"](args["B"], args["A"]), A=A, B=B
            )
        )
        == "I 0"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["equal"](args["A"], args["Z"]), A=A, Z=Z
            )
        )
        == "I 0"
    )


def test_logical_not_equal() -> None:
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["notequal"](args["A"], args["A"]), A=A
            )
        )
        == "I 0"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["notequal"](args["B"], args["B"]), B=B
            )
        )
        == "I 0"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["notequal"](args["Z"], args["Z"]), Z=Z
            )
        )
        == "I 0"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["notequal"](args["A"], args["B"]), A=A, B=B
            )
        )
        == "I 1"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["notequal"](args["B"], args["A"]), A=A, B=B
            )
        )
        == "I 1"
    )
    assert (
        pixel(
            ImageMath.lambda_eval(
                lambda args: args["notequal"](args["A"], args["Z"]), A=A, Z=Z
            )
        )
        == "I 1"
    )
