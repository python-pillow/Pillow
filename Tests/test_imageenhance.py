from PIL import Image, ImageEnhance

from .helper import assert_image_equal, hopper


def test_sanity():
    # FIXME: assert_image
    # Implicit asserts no exception:
    ImageEnhance.Color(hopper()).enhance(0.5)
    ImageEnhance.Contrast(hopper()).enhance(0.5)
    ImageEnhance.Brightness(hopper()).enhance(0.5)
    ImageEnhance.Sharpness(hopper()).enhance(0.5)


def test_crash():
    # crashes on small images
    im = Image.new("RGB", (1, 1))
    ImageEnhance.Sharpness(im).enhance(0.5)


def _half_transparent_image():
    # returns an image, half transparent, half solid
    im = hopper("RGB")

    transparent = Image.new("L", im.size, 0)
    solid = Image.new("L", (im.size[0] // 2, im.size[1]), 255)
    transparent.paste(solid, (0, 0))
    im.putalpha(transparent)

    return im


def _check_alpha(im, original, op, amount):
    assert im.getbands() == original.getbands()
    assert_image_equal(
        im.getchannel("A"),
        original.getchannel("A"),
        f"Diff on {op}: {amount}",
    )


def test_alpha():
    # Issue https://github.com/python-pillow/Pillow/issues/899
    # Is alpha preserved through image enhancement?

    original = _half_transparent_image()

    for op in ["Color", "Brightness", "Contrast", "Sharpness"]:
        for amount in [0, 0.5, 1.0]:
            _check_alpha(
                getattr(ImageEnhance, op)(original).enhance(amount),
                original,
                op,
                amount,
            )
