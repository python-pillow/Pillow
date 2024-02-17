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
