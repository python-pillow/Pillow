from __future__ import annotations

import pytest

from PIL import Image, ImageEnhance

from .helper import assert_image_equal, hopper


def test_sanity() -> None:
    # FIXME: assert_image
    # Implicit asserts no exception:
    ImageEnhance.Color(hopper()).enhance(0.5)
    ImageEnhance.Contrast(hopper()).enhance(0.5)
    ImageEnhance.Brightness(hopper()).enhance(0.5)
    ImageEnhance.Sharpness(hopper()).enhance(0.5)


def test_crash() -> None:
    # crashes on small images
    im = Image.new("RGB", (1, 1))
    ImageEnhance.Sharpness(im).enhance(0.5)


def _half_transparent_image() -> Image.Image:
    # returns an image, half transparent, half solid
    im = hopper("RGB")

    transparent = Image.new("L", im.size, 0)
    solid = Image.new("L", (im.size[0] // 2, im.size[1]), 255)
    transparent.paste(solid, (0, 0))
    im.putalpha(transparent)

    return im


def _check_alpha(
    im: Image.Image, original: Image.Image, op: str, amount: float
) -> None:
    assert im.getbands() == original.getbands()
    assert_image_equal(
        im.getchannel("A"),
        original.getchannel("A"),
        f"Diff on {op}: {amount}",
    )


@pytest.mark.parametrize("op", ("Color", "Brightness", "Contrast", "Sharpness"))
def test_alpha(op: str) -> None:
    # Issue https://github.com/python-pillow/Pillow/issues/899
    # Is alpha preserved through image enhancement?

    original = _half_transparent_image()

    for amount in [0, 0.5, 1.0]:
        _check_alpha(
            getattr(ImageEnhance, op)(original).enhance(amount),
            original,
            op,
            amount,
        )


@pytest.mark.parametrize("mode", ("I;16", "I;16B", "I;16L", "I;16N"))
@pytest.mark.parametrize("op", ("Color", "Brightness", "Contrast", "Sharpness"))
def test_16bit(mode: str, op: str) -> None:
    im = Image.new(mode, (10, 10), 1000)
    enhanced = getattr(ImageEnhance, op)(im).enhance(0.5)
    assert enhanced.mode == mode
    assert enhanced.size == im.size


@pytest.mark.parametrize("mode", ("I;16", "I;16B", "I;16L", "I;16N"))
def test_16bit_values(mode: str) -> None:
    # Brightness
    im = Image.new(mode, (2, 2), 1000)
    assert getattr(ImageEnhance, "Brightness")(im).enhance(0.0).getpixel((0, 0)) == 0
    assert getattr(ImageEnhance, "Brightness")(im).enhance(0.5).getpixel((0, 0)) == 500
    assert getattr(ImageEnhance, "Brightness")(im).enhance(1.0).getpixel((0, 0)) == 1000
    assert getattr(ImageEnhance, "Brightness")(im).enhance(2.0).getpixel((0, 0)) == 2000

    # Contrast
    im2 = Image.new(mode, (2, 1))
    im2.putpixel((0, 0), 1000)
    im2.putpixel((1, 0), 3000)
    c = ImageEnhance.Contrast(im2)
    assert c.enhance(0.0).getpixel((0, 0)) == 2000
    assert c.enhance(0.0).getpixel((1, 0)) == 2000
    assert c.enhance(0.5).getpixel((0, 0)) == 1500
    assert c.enhance(0.5).getpixel((1, 0)) == 2500
    assert c.enhance(1.0).getpixel((0, 0)) == 1000
    assert c.enhance(1.0).getpixel((1, 0)) == 3000
    assert c.enhance(2.0).getpixel((0, 0)) == 0
    assert c.enhance(2.0).getpixel((1, 0)) == 4000

    # Color (grayscale is unchanged)
    col = ImageEnhance.Color(im)
    assert col.enhance(0.0).getpixel((0, 0)) == 1000
    assert col.enhance(0.5).getpixel((0, 0)) == 1000
    assert col.enhance(2.0).getpixel((0, 0)) == 1000
