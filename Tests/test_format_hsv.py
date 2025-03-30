from __future__ import annotations

import colorsys
import itertools
from typing import Callable

from PIL import Image

from .helper import assert_image_similar, hopper


def int_to_float(i: int) -> float:
    return i / 255


def tuple_to_ints(tp: tuple[float, float, float]) -> tuple[int, int, int]:
    x, y, z = tp
    return int(x * 255.0), int(y * 255.0), int(z * 255.0)


def test_sanity() -> None:
    Image.new("HSV", (100, 100))


def linear_gradient() -> Image.Image:
    im = Image.linear_gradient(mode="L")
    im90 = im.rotate(90)

    (px, h) = im.size

    r = Image.new("L", (px * 3, h))
    g = r.copy()
    b = r.copy()

    r.paste(im, (0, 0))
    r.paste(im90, (px, 0))

    g.paste(im90, (0, 0))
    g.paste(im, (2 * px, 0))

    b.paste(im, (px, 0))
    b.paste(im90, (2 * px, 0))

    return Image.merge("RGB", (r, g, b))


def to_xxx_colorsys(
    im: Image.Image,
    func: Callable[[float, float, float], tuple[float, float, float]],
    mode: str,
) -> Image.Image:
    # convert the hard way using the library colorsys routines.

    (r, g, b) = im.split()

    conv_func = int_to_float

    converted = [
        tuple_to_ints(func(conv_func(_r), conv_func(_g), conv_func(_b)))
        for (_r, _g, _b) in itertools.zip_longest(r.tobytes(), g.tobytes(), b.tobytes())
    ]

    new_bytes = b"".join(
        bytes(chr(h) + chr(s) + chr(v), "latin-1") for (h, s, v) in converted
    )

    hsv = Image.frombytes(mode, r.size, new_bytes)

    return hsv


def to_hsv_colorsys(im: Image.Image) -> Image.Image:
    return to_xxx_colorsys(im, colorsys.rgb_to_hsv, "HSV")


def to_rgb_colorsys(im: Image.Image) -> Image.Image:
    return to_xxx_colorsys(im, colorsys.hsv_to_rgb, "RGB")


def test_linear_gradient() -> None:
    src = linear_gradient().resize((3 * 32, 32), Image.Resampling.BILINEAR)
    im = src.convert("HSV")
    comparable = to_hsv_colorsys(src)

    assert_image_similar(
        im.getchannel(0), comparable.getchannel(0), 1, "Hue conversion is wrong"
    )
    assert_image_similar(
        im.getchannel(1),
        comparable.getchannel(1),
        1,
        "Saturation conversion is wrong",
    )
    assert_image_similar(
        im.getchannel(2), comparable.getchannel(2), 1, "Value conversion is wrong"
    )

    comparable = src
    im = im.convert("RGB")

    assert_image_similar(
        im.getchannel(0), comparable.getchannel(0), 3, "R conversion is wrong"
    )
    assert_image_similar(
        im.getchannel(1), comparable.getchannel(1), 3, "G conversion is wrong"
    )
    assert_image_similar(
        im.getchannel(2), comparable.getchannel(2), 3, "B conversion is wrong"
    )


def test_convert() -> None:
    im = hopper("RGB").convert("HSV")
    comparable = to_hsv_colorsys(hopper("RGB"))

    assert_image_similar(
        im.getchannel(0), comparable.getchannel(0), 1, "Hue conversion is wrong"
    )
    assert_image_similar(
        im.getchannel(1),
        comparable.getchannel(1),
        1,
        "Saturation conversion is wrong",
    )
    assert_image_similar(
        im.getchannel(2), comparable.getchannel(2), 1, "Value conversion is wrong"
    )


def test_hsv_to_rgb() -> None:
    comparable = to_hsv_colorsys(hopper("RGB"))
    converted = comparable.convert("RGB")
    comparable = to_rgb_colorsys(comparable)

    assert_image_similar(
        converted.getchannel(0),
        comparable.getchannel(0),
        3,
        "R conversion is wrong",
    )
    assert_image_similar(
        converted.getchannel(1),
        comparable.getchannel(1),
        3,
        "G conversion is wrong",
    )
    assert_image_similar(
        converted.getchannel(2),
        comparable.getchannel(2),
        3,
        "B conversion is wrong",
    )
