from __future__ import annotations

import pytest

from PIL import Image, ImageFilter, _planar
from PIL._planar import Band, PlanarImage

from .helper import assert_image_equal, hopper

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

RGBA16 = (
    Band("R", "uint16"),
    Band("G", "uint16"),
    Band("B", "uint16"),
    Band("A", "uint16", "alpha"),
)


def edge_image() -> PlanarImage:
    # Left half opaque white, right half transparent black
    im = PlanarImage.new((16, 16), RGBA16, "RGB", (0, 0, 0, 0))
    for x in range(8):
        for y in range(16):
            im.putpixel((x, y), (65535, 65535, 65535, 65535))
    return im


def test_new() -> None:
    im = PlanarImage.new((4, 3), RGBA16, "RGB", (1, 2, 3, 4))

    assert im.mode == _planar.MODE
    assert im.size == (4, 3)
    assert im.getbands() == ("R", "G", "B", "A")
    assert im.getpixel((0, 0)) == (1, 2, 3, 4)
    assert [plane.mode for plane in im.planes] == ["I;16"] * 4


def test_mixed_sample_types() -> None:
    bands = (Band("R", "uint16"), Band("A", "uint8", "alpha"), Band("Z", "float32"))
    im = PlanarImage.new((2, 2), bands, "L", (1000, 255, 0.5))

    assert im.getpixel((1, 1)) == (1000, 255, 0.5)
    assert im.getband("Z").mode == "F"


def test_many_bands() -> None:
    bands = [Band(f"B{i}", "uint16", "extra") for i in range(12)]
    im = PlanarImage.new((2, 2), bands, "L", range(12))

    assert im.getpixel((0, 0)) == tuple(range(12))


@pytest.mark.parametrize(
    "planes, bands, message",
    (
        ([], [], "number of bands"),
        ([Image.new("L", (1, 1))], [], "must match"),
        ([Image.new("L", (1, 1))], [Band("R", "uint16")], "plane has mode L"),
        (
            [Image.new("L", (1, 1)), Image.new("L", (2, 1))],
            [Band("R", "uint8"), Band("G", "uint8")],
            "same size",
        ),
        (
            [Image.new("L", (1, 1))] * 2,
            [Band("R", "uint8"), Band("R", "uint8")],
            "unique",
        ),
        (
            [Image.new("L", (1, 1))] * 2,
            [Band("A", "uint8", "alpha"), Band("B", "uint8", "alpha")],
            "one alpha band",
        ),
    ),
)
def test_invalid(planes: list[Image.Image], bands: list[Band], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        PlanarImage(planes, bands, "RGB")


def test_too_many_bands() -> None:
    bands = [Band(f"B{i}", "uint8") for i in range(_planar.MAX_BANDS + 1)]
    with pytest.raises(ValueError, match="number of bands"):
        PlanarImage.new((1, 1), bands, "L")


def test_invalid_band() -> None:
    with pytest.raises(ValueError, match="sample type"):
        Band("R", "uint64")
    with pytest.raises(ValueError, match="role"):
        Band("R", "uint8", "depth")


def test_premultiplied_without_alpha() -> None:
    with pytest.raises(ValueError, match="alpha band"):
        PlanarImage.new((1, 1), [Band("L", "uint8")], "L", premultiplied=True)


@pytest.mark.parametrize("mode", ("L", "LA", "La", "RGB", "RGBA", "RGBa", "CMYK"))
def test_roundtrip_existing_modes(mode: str) -> None:
    im = hopper(mode)
    planar = PlanarImage.from_image(im)

    assert planar.getbands() == im.getbands()
    assert_image_equal(planar.to_image(), im)


@pytest.mark.parametrize("mode", ("I;16", "I", "F"))
def test_roundtrip_single_band(mode: str) -> None:
    im = hopper(mode)
    assert_image_equal(PlanarImage.from_image(im).to_image(), im)


def test_to_image_no_match() -> None:
    with pytest.raises(ValueError, match="no existing mode"):
        PlanarImage.new((1, 1), RGBA16, "RGB").to_image()


def test_unsupported_mode() -> None:
    with pytest.raises(ValueError, match="cannot be described"):
        PlanarImage.from_image(hopper("P"))


@pytest.mark.parametrize(
    "op",
    (
        lambda im: im.crop((10, 20, 60, 90)),
        lambda im: im.transpose(Image.Transpose.ROTATE_90),
        lambda im: im.resize((50, 70), Image.Resampling.BICUBIC),
        lambda im: im.rotate(30, Image.Resampling.BILINEAR, expand=True),
        lambda im: im.filter(ImageFilter.GaussianBlur(2)),
    ),
)
def test_per_plane_matches_interleaved(op: Callable[[Any], Any]) -> None:
    # Without alpha, applying an operation per plane gives exactly the same
    # result as applying it to the interleaved image
    im = hopper("RGB")
    assert_image_equal(op(PlanarImage.from_image(im)).to_image(), op(im))


@pytest.mark.parametrize(
    "op",
    (
        lambda im: im.resize((50, 70), Image.Resampling.BICUBIC),
        lambda im: im.rotate(30, Image.Resampling.BILINEAR),
    ),
)
def test_opaque_alpha_matches_interleaved(op: Callable[[Any], Any]) -> None:
    im = hopper("RGBA")
    assert_image_equal(op(PlanarImage.from_image(im)).to_image(), op(im))


def test_resize_premultiplies_alpha() -> None:
    resized = edge_image().resize((5, 5), Image.Resampling.BILINEAR)

    for x in range(5):
        r, g, b, a = resized.getpixel((x, 2))
        if a:
            # Transparent black does not darken partially transparent edges
            assert (r, g, b) == (65535, 65535, 65535)


def test_resize_naive_darkens_edges() -> None:
    # Resizing each plane without premultiplying darkens partially transparent
    # edges, which is why resize() premultiplies
    im = edge_image()
    planes = [p.resize((5, 5), Image.Resampling.BILINEAR) for p in im.planes]
    naive = PlanarImage(planes, im.bands, im.colorspace)

    edge = [naive.getpixel((x, 2)) for x in range(5)]
    assert any(0 < a < 65535 and r < 65535 for r, g, b, a in edge)


def test_premultiplied_image_resizes_per_plane() -> None:
    im = PlanarImage.from_image(hopper("RGBa"))
    resized = im.resize((50, 70), Image.Resampling.BICUBIC)

    assert resized.premultiplied
    assert_image_equal(
        resized.to_image(), hopper("RGBa").resize((50, 70), Image.Resampling.BICUBIC)
    )


def test_float_alpha() -> None:
    bands = (Band("L", "float32"), Band("A", "float32", "alpha"))
    im = PlanarImage.new((4, 1), bands, "L", (0.0, 0.0))
    im.putpixel((0, 0), (1.0, 1.0))
    im.putpixel((1, 0), (1.0, 1.0))

    resized = im.resize((2, 1), Image.Resampling.BILINEAR)

    value, alpha = resized.getpixel((1, 0))
    assert 0 < alpha < 1
    assert value == pytest.approx(1.0)


def test_int32_alpha() -> None:
    bands = (Band("L", "int32"), Band("A", "int32", "alpha"))
    im = PlanarImage.new((2, 2), bands, "L")
    with pytest.raises(ValueError, match="int32 alpha"):
        im.resize((1, 1), Image.Resampling.BILINEAR)


def test_nearest_does_not_premultiply() -> None:
    im = edge_image()
    resized = im.resize((5, 5), Image.Resampling.NEAREST)
    expected = [p.resize((5, 5), Image.Resampling.NEAREST) for p in im.planes]
    for plane, e in zip(resized.planes, expected):
        assert_image_equal(plane, e)


def test_uint16_filter_unsupported() -> None:
    # Not every operation is supported by every single-band mode yet
    im = PlanarImage.new((4, 4), RGBA16, "RGB")
    with pytest.raises(ValueError):
        im.filter(ImageFilter.GaussianBlur(1))


def test_getband_is_a_copy() -> None:
    im = PlanarImage.new((2, 2), RGBA16, "RGB")
    band = im.getband("R")
    band.putpixel((0, 0), 5)

    assert im.getpixel((0, 0))[0] == 0
    assert [b.getpixel((0, 0)) for b in im.split()] == [0, 0, 0, 0]


def test_copy() -> None:
    im = PlanarImage.new((2, 2), RGBA16, "RGB")
    copy = im.copy()
    copy.putpixel((0, 0), (1, 2, 3, 4))

    assert im.getpixel((0, 0)) == (0, 0, 0, 0)


def test_putpixel_wrong_length() -> None:
    im = PlanarImage.new((2, 2), RGBA16, "RGB")
    with pytest.raises(ValueError, match="one entry per band"):
        im.putpixel((0, 0), (1, 2))


def test_new_wrong_color_length() -> None:
    with pytest.raises(ValueError, match="one value per band"):
        PlanarImage.new((2, 2), RGBA16, "RGB", (1, 2))


def test_repr() -> None:
    im = PlanarImage.new((4, 3), RGBA16[:2], "RGB")
    assert repr(im) == "<PlanarImage RGB (R:uint16, G:uint16) size=4x3>"
