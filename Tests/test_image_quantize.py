from __future__ import annotations

import pytest
from packaging.version import parse as parse_version

from PIL import Image, features

from .helper import assert_image_similar, hopper, is_ppc64le, skip_unless_feature


def test_sanity() -> None:
    image = hopper()
    converted = image.quantize()
    assert converted.mode == "P"
    assert_image_similar(converted.convert("RGB"), image, 10)

    image = hopper()
    converted = image.quantize(palette=hopper("P"))
    assert converted.mode == "P"
    assert_image_similar(converted.convert("RGB"), image, 60)


@skip_unless_feature("libimagequant")
def test_libimagequant_quantize() -> None:
    image = hopper()
    if is_ppc64le():
        version = features.version_feature("libimagequant")
        assert version is not None
        if parse_version(version) < parse_version("4"):
            pytest.skip("Fails with libimagequant earlier than 4.0.0 on ppc64le")
    converted = image.quantize(100, Image.Quantize.LIBIMAGEQUANT)
    assert converted.mode == "P"
    assert_image_similar(converted.convert("RGB"), image, 15)
    colors = converted.getcolors()
    assert colors is not None
    assert len(colors) == 100


def test_octree_quantize() -> None:
    image = hopper()
    converted = image.quantize(100, Image.Quantize.FASTOCTREE)
    assert converted.mode == "P"
    assert_image_similar(converted.convert("RGB"), image, 20)
    colors = converted.getcolors()
    assert colors is not None
    assert len(colors) == 100


def test_rgba_quantize() -> None:
    image = hopper("RGBA")
    with pytest.raises(ValueError):
        image.quantize(method=0)

    assert image.quantize().convert().mode == "RGBA"


def test_quantize() -> None:
    with Image.open("Tests/images/caption_6_33_22.png") as image:
        image = image.convert("RGB")
    converted = image.quantize()
    assert converted.mode == "P"
    assert_image_similar(converted.convert("RGB"), image, 1)


def test_quantize_no_dither() -> None:
    image = hopper()
    with Image.open("Tests/images/caption_6_33_22.png") as palette:
        palette = palette.convert("P")

    converted = image.quantize(dither=Image.Dither.NONE, palette=palette)
    assert converted.mode == "P"
    assert converted.palette is not None
    assert palette.palette is not None
    assert converted.palette.palette == palette.palette.palette


def test_quantize_no_dither2() -> None:
    im = Image.new("RGB", (9, 1))
    im.putdata([(p,) * 3 for p in range(0, 36, 4)])

    palette = Image.new("P", (1, 1))
    data = (0, 0, 0, 32, 32, 32)
    palette.putpalette(data)
    quantized = im.quantize(dither=Image.Dither.NONE, palette=palette)

    assert quantized.palette is not None
    assert tuple(quantized.palette.palette) == data

    px = quantized.load()
    assert px is not None
    for x in range(9):
        assert px[x, 0] == (0 if x < 5 else 1)


def test_quantize_dither_diff() -> None:
    image = hopper()
    with Image.open("Tests/images/caption_6_33_22.png") as palette:
        palette = palette.convert("P")

    dither = image.quantize(dither=Image.Dither.FLOYDSTEINBERG, palette=palette)
    nodither = image.quantize(dither=Image.Dither.NONE, palette=palette)

    assert dither.tobytes() != nodither.tobytes()


@pytest.mark.parametrize(
    "method", (Image.Quantize.MEDIANCUT, Image.Quantize.MAXCOVERAGE)
)
def test_quantize_kmeans(method: Image.Quantize) -> None:
    im = hopper()
    no_kmeans = im.quantize(kmeans=0, method=method)
    kmeans = im.quantize(kmeans=1, method=method)
    assert kmeans.tobytes() != no_kmeans.tobytes()

    with pytest.raises(ValueError):
        im.quantize(kmeans=-1, method=method)


def test_colors() -> None:
    im = hopper()
    colors = 2
    converted = im.quantize(colors)
    assert converted.palette is not None
    assert len(converted.palette.palette) == colors * len("RGB")


def test_transparent_colors_equal() -> None:
    im = Image.new("RGBA", (1, 2), (0, 0, 0, 0))
    px = im.load()
    assert px is not None
    px[0, 1] = (255, 255, 255, 0)

    converted = im.quantize()
    converted_px = converted.load()
    assert converted_px is not None
    assert converted_px[0, 0] == converted_px[0, 1]


@pytest.mark.parametrize(
    "method, color",
    (
        (Image.Quantize.MEDIANCUT, (0, 0, 0)),
        (Image.Quantize.MAXCOVERAGE, (0, 0, 0)),
        (Image.Quantize.FASTOCTREE, (0, 0, 0)),
        (Image.Quantize.FASTOCTREE, (0, 0, 0, 0)),
    ),
)
def test_palette(method: Image.Quantize, color: tuple[int, ...]) -> None:
    im = Image.new("RGBA" if len(color) == 4 else "RGB", (1, 1), color)

    converted = im.quantize(method=method)
    assert converted.palette is not None
    assert converted.getpixel((0, 0)) == converted.palette.colors[color]


def test_small_palette() -> None:
    # Arrange
    im = hopper()

    colors = (255, 0, 0, 0, 0, 255)
    p = Image.new("P", (1, 1))
    p.putpalette(colors)

    # Act
    im = im.quantize(palette=p)

    # Assert
    quantized_colors = im.getcolors()
    assert quantized_colors is not None
    assert len(quantized_colors) == 2
