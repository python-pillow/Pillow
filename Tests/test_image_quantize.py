import pytest

from PIL import Image

from .helper import assert_image, assert_image_similar, hopper, is_ppc64le


def test_sanity():
    image = hopper()
    converted = image.quantize()
    assert_image(converted, "P", converted.size)
    assert_image_similar(converted.convert("RGB"), image, 10)

    image = hopper()
    converted = image.quantize(palette=hopper("P"))
    assert_image(converted, "P", converted.size)
    assert_image_similar(converted.convert("RGB"), image, 60)


@pytest.mark.xfail(is_ppc64le(), reason="failing on ppc64le on GHA")
def test_libimagequant_quantize():
    image = hopper()
    try:
        converted = image.quantize(100, Image.LIBIMAGEQUANT)
    except ValueError as ex:  # pragma: no cover
        if "dependency" in str(ex).lower():
            pytest.skip("libimagequant support not available")
        else:
            raise
    assert_image(converted, "P", converted.size)
    assert_image_similar(converted.convert("RGB"), image, 15)
    assert len(converted.getcolors()) == 100


def test_octree_quantize():
    image = hopper()
    converted = image.quantize(100, Image.FASTOCTREE)
    assert_image(converted, "P", converted.size)
    assert_image_similar(converted.convert("RGB"), image, 20)
    assert len(converted.getcolors()) == 100


def test_rgba_quantize():
    image = hopper("RGBA")
    with pytest.raises(ValueError):
        image.quantize(method=0)

    assert image.quantize().convert().mode == "RGBA"


def test_quantize():
    with Image.open("Tests/images/caption_6_33_22.png") as image:
        image = image.convert("RGB")
    converted = image.quantize()
    assert_image(converted, "P", converted.size)
    assert_image_similar(converted.convert("RGB"), image, 1)


def test_quantize_no_dither():
    image = hopper()
    with Image.open("Tests/images/caption_6_33_22.png") as palette:
        palette = palette.convert("P")

    converted = image.quantize(dither=0, palette=palette)
    assert_image(converted, "P", converted.size)
    assert converted.palette.palette == palette.palette.palette


def test_quantize_dither_diff():
    image = hopper()
    with Image.open("Tests/images/caption_6_33_22.png") as palette:
        palette = palette.convert("P")

    dither = image.quantize(dither=1, palette=palette)
    nodither = image.quantize(dither=0, palette=palette)

    assert dither.tobytes() != nodither.tobytes()


def test_transparent_colors_equal():
    im = Image.new("RGBA", (1, 2), (0, 0, 0, 0))
    px = im.load()
    px[0, 1] = (255, 255, 255, 0)

    converted = im.quantize()
    converted_px = converted.load()
    assert converted_px[0, 0] == converted_px[0, 1]
