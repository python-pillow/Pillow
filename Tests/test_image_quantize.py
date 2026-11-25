from __future__ import annotations

import pytest

from PIL import Image

from .helper import (
    assert_image_similar,
    has_feature_version,
    hopper,
    is_ppc64le,
    skip_unless_feature,
)


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
    if is_ppc64le() and not has_feature_version("libimagequant", "4"):
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
        converted = image.convert("RGB")
    converted = converted.quantize()
    assert converted.mode == "P"
    assert_image_similar(converted.convert("RGB"), image, 1)


def test_quantize_no_dither() -> None:
    image = hopper()
    with Image.open("Tests/images/caption_6_33_22.png") as palette:
        palette_p = palette.convert("P")

    converted = image.quantize(dither=Image.Dither.NONE, palette=palette_p)
    assert converted.mode == "P"
    assert converted.palette is not None
    assert palette_p.palette is not None
    assert converted.palette.palette == palette_p.palette.palette


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
        palette_p = palette.convert("P")

    dither = image.quantize(dither=Image.Dither.FLOYDSTEINBERG, palette=palette_p)
    nodither = image.quantize(dither=Image.Dither.NONE, palette=palette_p)

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


@skip_unless_feature("libimagequant")
def test_resize() -> None:
    im = hopper().resize((100, 100))
    converted = im.quantize(100, Image.Quantize.LIBIMAGEQUANT)
    colors = converted.getcolors()
    assert colors is not None
    assert len(colors) == 100


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


def test_empty_palette() -> None:
    im = hopper()

    p = Image.new("P", (1, 1))
    assert p.palette is not None
    assert p.palette.palette == b""

    with pytest.raises(ValueError, match="empty palette"):
        im.quantize(palette=p)


def test_octree_quantize_rgba_alpha_resolution() -> None:
    base_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    palette = [(r, g, b, a) for a in range(128) for (r, g, b) in base_colors]
    im = Image.new("RGBA", (64, 64))
    im.putdata([palette[i % len(palette)] for i in range(64 * 64)])

    q256 = im.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
    assert q256.mode == "P"
    assert q256.palette is not None
    assert q256.palette.mode == "RGBA"
    assert len(set(q256.tobytes())) == 256
    assert_image_similar(q256.convert("RGBA").getchannel("A"), im.getchannel("A"), 1)
    assert_image_similar(q256.convert("RGBA"), im, 4)

    q64 = im.quantize(colors=64, method=Image.Quantize.FASTOCTREE)
    assert len(set(q64.tobytes())) == 64
    assert_image_similar(q64.convert("RGBA").getchannel("A"), im.getchannel("A"), 3)


def test_octree_quantize_close_rgb_with_alpha() -> None:
    # All four base RGB colors fall in the same coarse 3/4/3-bit bucket
    base_colors = [
        (100, 102, 104),
        (105, 102, 104),
        (100, 107, 104),
        (100, 102, 109),
    ]
    palette = [(r, g, b, a) for a in range(1, 129) for (r, g, b) in base_colors]
    im = Image.new("RGBA", (64, 32))
    im.putdata([palette[i % len(palette)] for i in range(64 * 32)])

    q = im.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
    assert len(set(q.tobytes())) == 256
    assert_image_similar(q.convert("RGBA"), im, 1)


def test_octree_quantize_exact_colors() -> None:
    im_rgba = Image.new("RGBA", (200, 1))
    im_rgba.putdata([(255, 0, 0, a) for a in range(1, 201)])
    q_rgba = im_rgba.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
    assert len(set(q_rgba.tobytes())) == 200
    assert q_rgba.convert("RGBA").tobytes() == im_rgba.tobytes()

    im_rgb = Image.new("RGB", (256, 1))
    im_rgb.putdata([(v, v, v) for v in range(256)])
    q_rgb = im_rgb.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
    assert len(set(q_rgb.tobytes())) == 256
    assert q_rgb.convert("RGB").tobytes() == im_rgb.tobytes()


def test_octree_quantize_rgba_gradient_and_pruning() -> None:
    # 4 base RGB quadrants with a full 0..255 radial alpha gradient (~972 colors)
    im = Image.new("RGBA", (64, 64))
    base_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    alpha = Image.radial_gradient("L").resize((64, 64))
    alpha_bytes = alpha.tobytes()
    pixels = [
        (*base_colors[(y // 32) * 2 + (x // 32)], alpha_bytes[y * 64 + x])
        for y in range(64)
        for x in range(64)
    ]
    im.putdata(pixels)

    q = im.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
    assert len(set(q.tobytes())) == 256
    assert_image_similar(q.convert("RGBA"), im, 2)

    # 16,384 distinct colors confined to 64 fine buckets (exercises online pruning)
    im_2d = Image.new("RGBA", (256, 64))
    im_2d.putdata([(0, 0, x, y * 4 + 3) for y in range(64) for x in range(256)])
    q_2d = im_2d.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
    assert len(set(q_2d.tobytes())) == 256
    assert_image_similar(q_2d.convert("RGBA"), im_2d, 9)


def test_octree_quantize_single_channel_rgb() -> None:
    im = Image.new("RGB", (256, 4))
    im.putdata([(x, 0, 0) for _ in range(4) for x in range(256)])
    q = im.quantize(colors=64, method=Image.Quantize.FASTOCTREE)
    assert len(set(q.tobytes())) == 64
    assert_image_similar(q.convert("RGB"), im, 2)


def test_octree_quantize_edge_cases() -> None:
    empty = Image.new("RGBA", (0, 0))
    q_empty = empty.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
    assert q_empty.mode == "P"
    assert q_empty.size == (0, 0)

    solid = Image.new("RGBA", (16, 16), (12, 34, 56, 78))
    q_solid = solid.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
    assert len(set(q_solid.tobytes())) == 1
    assert q_solid.convert("RGBA").tobytes() == solid.tobytes()

    q_one = solid.quantize(colors=1, method=Image.Quantize.FASTOCTREE)
    assert len(set(q_one.tobytes())) == 1
    assert q_one.convert("RGBA").tobytes() == solid.tobytes()
