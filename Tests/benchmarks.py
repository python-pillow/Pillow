"""
pytest-benchmark tests for Pillow features.
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import re
import warnings
from importlib.util import find_spec
from io import BytesIO

import pytest

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
from PIL.Image import Resampling, Transform, Transpose

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Callable

    BenchmarkSave = Callable[[Image.Image], None]

    from pytest_benchmark.fixture import (  # type: ignore[unused-ignore, import-not-found]
        BenchmarkFixture,
    )

if not (find_spec("pytest_benchmark") or find_spec("pytest_codspeed")):
    pytest.skip("pytest-benchmark or pytest-codspeed required", allow_module_level=True)

_save_results = os.environ.get("PILLOW_BENCHMARK_SAVE_RESULTS_PATH")
SAVE_RESULTS_PATH = pathlib.Path(_save_results) if _save_results else None

# These can be adjusted to add more modes to benchmark
# (however all features benchmarked might not support all PIL modes).
MODES = ["RGB", "RGBA", "L", "LA"]

# The size for generated test images.
# Note that adjusting this will naturally change how long operations take.
# The `bench` fixture takes care of saving this information in the extra info
# for the benchmark run, so that throughput (Mpx/s) can be recomputed in the future.
SIZES = [(1237, 811)]  # Primes, non-power-of-two, asymmetric, approximately 1024x1024

# For benchmarks that act on test fixture files, these are the paths loaded.
IMAGES_PATH = pathlib.Path(__file__).parent / "images"
PATHS = [
    IMAGES_PATH / "flower2.jpg",
]

# These are derived from the other configuration, above.
RGB_MODES = [mode for mode in MODES if mode.startswith("RGB")]
ALPHA_MODES = [mode for mode in MODES if mode.endswith("A")]
SCALE_MODES = [*MODES, "I", "F"]


def _format_size(size: tuple[int, int]) -> str:
    return f"{size[0]}x{size[1]}"


def _format_path(path: pathlib.Path) -> str:
    return path.name


@pytest.fixture
def bench(
    request: pytest.FixtureRequest,
    benchmark: BenchmarkFixture,
) -> BenchmarkFixture:
    """
    pytest-benchmark with extra information.
    """
    try:
        benchmark.extra_info["mode"] = request.getfixturevalue("mode")
    except LookupError:
        pass
    try:
        size = request.getfixturevalue("size")
        benchmark.extra_info["size"] = _format_size(size)
        benchmark.extra_info["pixels"] = size[0] * size[1]
    except LookupError:
        pass
    return benchmark


@pytest.fixture
def benchmark_save(request: pytest.FixtureRequest) -> BenchmarkSave:
    """
    Fixture to save a benchmark image, if so configured.
    """

    def save(im: Image.Image) -> None:
        if SAVE_RESULTS_PATH:
            safe_name = re.sub("[^-a-zA-Z0-9]", "_", str(request.node.name))
            name = (SAVE_RESULTS_PATH / safe_name).with_suffix(".png")
            try:
                SAVE_RESULTS_PATH.mkdir(parents=True, exist_ok=True)
                im.save(name)
            except Exception as e:
                warnings.warn(
                    f"Failed to save benchmark result to {name}: {e}",
                    stacklevel=2,
                )

    return save


def make_pillow_image(
    mode: str,
    size: tuple[int, int],
    seed: int = 0,
) -> Image.Image:
    """
    Generate a synthetic test image with the given mode and size.
    Different seeds give different final images.
    """
    width, height = size
    vertical = Image.linear_gradient("L")
    horizontal = vertical.transpose(Transpose.ROTATE_90)
    radial = Image.radial_gradient("L")
    base = Image.merge("RGB", (horizontal, vertical, radial)).resize(
        size, Resampling.BILINEAR
    )
    # SHAKE128 gives us a predictable noise pattern.
    noise_bytes = hashlib.shake_128(f"pillow-benchmark-{seed}".encode()).digest(
        width * height * 3
    )
    noise = Image.frombytes("RGB", size, noise_bytes)

    def centered_box(area_fraction: float) -> tuple[int, int, int, int]:
        inset = (1 - area_fraction**0.5) / 2
        return (
            round(width * inset),
            round(height * inset),
            round(width * (1 - inset)),
            round(height * (1 - inset)),
        )

    im = base
    noise_box = centered_box(1 / 2)
    im.paste(noise.crop(noise_box), noise_box)  # Noise in the middle
    im.paste(tuple(noise_bytes[:3]), centered_box(1 / 6))  # Solid center
    if seed:
        im = ImageChops.offset(im, seed * 383, seed * 271)
    return im.convert(mode)


BBOX_SCENARIOS: dict[str, tuple[float, str] | None] = {
    "half-centered": (0.5, "center"),
    "small-centered": (0.1, "center"),
    "half-corner": (0.5, "corner"),
    "empty": None,
}


def make_bbox_image(
    mode: str,
    size: tuple[int, int],
    region: tuple[float, str] | None,
) -> Image.Image:
    im = Image.new(mode, size, 0)
    if region is None:
        return im
    fraction, placement = region
    w, h = size
    bw, bh = max(1, round(w * fraction)), max(1, round(h * fraction))
    if placement == "center":
        left, top = (w - bw) // 2, (h - bh) // 2
    else:
        left, top = w - bw, h - bh
    nbands = len(im.getbands())
    color = (255, 128, 64, 255)[:nbands] if nbands > 1 else 255
    im.paste(color, (left, top, left + bw - 1, top + bh - 1))
    return im


@pytest.mark.benchmark(group="composition")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_blend(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
) -> None:
    im1 = make_pillow_image(mode, size)
    im2 = make_pillow_image(mode, size, seed=1)
    result = bench(Image.blend, im1, im2, 0.5)
    assert result.size == im1.size


@pytest.mark.benchmark(group="scale")
@pytest.mark.parametrize("resampler", Resampling, ids=lambda r: r.name)
@pytest.mark.parametrize("scale", [0.01, 0.125, 0.8, 2.14])
@pytest.mark.parametrize("mode", SCALE_MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_scale(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
    scale: float,
    resampler: Resampling,
) -> None:
    im = make_pillow_image(mode, size)
    dest = (round(scale * im.width), round(scale * im.height))
    bench.extra_info["label"] = [f"{dest[0]}x{dest[1]}", resampler.name]
    bench(im.resize, dest, resampler)


REDUCE_FACTORS = [
    (1, 2),  # ImagingReduce1x2
    (1, 3),  # ImagingReduce1x3
    (1, 7),  # ImagingReduce1xN
    (2, 1),  # ImagingReduce2x1
    (2, 2),  # ImagingReduce2x2
    (3, 1),  # ImagingReduce3x1
    (3, 3),  # ImagingReduce3x3
    (3, 5),  # ImagingReduceNxN
    (4, 4),  # ImagingReduce4x4
    (5, 5),  # ImagingReduce5x5
    (7, 1),  # ImagingReduceNx1
]


@pytest.mark.benchmark(group="scale")
@pytest.mark.parametrize("factor", REDUCE_FACTORS, ids=lambda f: f"{f[0]}x{f[1]}")
@pytest.mark.parametrize("mode", SCALE_MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_reduce(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
    factor: tuple[int, int],
) -> None:
    im = make_pillow_image(mode, size)
    bench.extra_info["label"] = [f"reduce {factor[0]}x{factor[1]}"]
    result = bench(im.reduce, factor)
    assert result.size == (
        -(-im.width // factor[0]),
        -(-im.height // factor[1]),
    )


@pytest.mark.benchmark(group="blur")
@pytest.mark.parametrize("radius", [1, 10, 30])
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_box_blur(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
    radius: int,
) -> None:
    im = make_pillow_image(mode, size)
    bench.extra_info["label"] = [f"{radius}px"]
    bench(im.filter, ImageFilter.BoxBlur(radius))


@pytest.mark.benchmark(group="composition")
@pytest.mark.parametrize("alpha", ["opaque", "transparent", "mixed"])
@pytest.mark.parametrize("mode", ALPHA_MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_alpha_composite(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
    alpha: str,
) -> None:
    im1 = make_pillow_image(mode, size)
    im2 = make_pillow_image(mode, size, seed=1)
    if alpha == "opaque":
        im2.putalpha(255)
    elif alpha == "transparent":
        im2.putalpha(0)
    else:  # "mixed"
        width, height = size
        gradient = bytes((x * 256) // width for x in range(width)) * height
        im2.putalpha(Image.frombytes("L", size, gradient))
    bench.extra_info["label"] = ["Composition", alpha]
    result = bench(Image.alpha_composite, im1, im2)
    assert result.size == im1.size


@pytest.mark.benchmark(group="convert")
@pytest.mark.parametrize(
    "mode_from, mode_to",
    [
        # bilevel <-> greyscale (in-place path: l2bit / bit2l)
        ("L", "1"),
        ("1", "L"),
        # greyscale <-> colour (pack / expand)
        ("RGB", "L"),
        ("L", "RGB"),
        ("RGB", "1"),
        ("LA", "RGBA"),
        # channel add / drop / premultiply
        ("RGB", "RGBA"),
        ("RGBA", "RGB"),
        ("RGBA", "LA"),
        ("RGBa", "RGBA"),
        ("RGBA", "RGBa"),
        # palette expansion (p2rgb / p2rgba / pa2rgb / pa2rgba)
        ("P", "RGB"),
        ("P", "RGBA"),
        ("PA", "RGB"),
        ("PA", "RGBA"),
        # colorspace conversions
        ("RGB", "YCbCr"),
        ("YCbCr", "RGB"),
        ("RGB", "HSV"),
        ("HSV", "RGB"),
        ("RGB", "CMYK"),
        ("CMYK", "RGB"),
        # integer / float modes
        ("L", "I"),
        ("I", "L"),
        ("L", "F"),
        ("F", "L"),
        ("RGB", "I;16"),
    ],
)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_convert(
    bench: BenchmarkFixture,
    mode_from: str,
    mode_to: str,
    size: tuple[int, int],
) -> None:
    im = make_pillow_image(mode_from, size)
    bench.extra_info["label"] = [f"{mode_from} to {mode_to}"]
    bench(im.convert, mode_to)


@pytest.mark.benchmark(group="crop")
@pytest.mark.parametrize(
    "scale",
    [
        (0.9, 0.9),
        (1.1, 1.1),
        (1.1, 0.9),
    ],
)
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_crop(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
    scale: tuple[float, float],
) -> None:
    im = make_pillow_image(mode, size)
    w, h = im.size
    width, height = round(scale[0] * w), round(scale[1] * h)
    left = (w - width) // 2
    top = (h - height) // 2
    box = (left, top, left + width, top + height)
    bench.extra_info["label"] = [f"{width}x{height}"]
    bench(im.crop, box)


@pytest.mark.benchmark(group="filter")
@pytest.mark.parametrize(
    "filter",
    [
        ImageFilter.SMOOTH,
        ImageFilter.SHARPEN,
        ImageFilter.SMOOTH_MORE,
    ],
    ids=lambda f: f.name,
)
@pytest.mark.parametrize("mode", [*MODES, "I;16"])
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_filter(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
    filter: type[ImageFilter.BuiltinFilter],
) -> None:
    im = make_pillow_image(mode, size)
    bench.extra_info["label"] = [filter.name]
    bench(im.filter, filter)


@pytest.mark.benchmark(group="filter")
@pytest.mark.parametrize(
    "rank_filter",
    [
        ImageFilter.MedianFilter(3),
        ImageFilter.MedianFilter(5),
        ImageFilter.MinFilter(3),
    ],
    ids=lambda f: f"{f.name}{f.size}",
)
@pytest.mark.parametrize("mode", ["L", "I", "F"])
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_rank_filter(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
    rank_filter: ImageFilter.RankFilter,
) -> None:
    im = make_pillow_image(mode, size)
    bench.extra_info["label"] = [f"{rank_filter.name}{rank_filter.size}"]
    bench(im.filter, rank_filter)


@pytest.mark.benchmark(group="lut")
@pytest.mark.parametrize(
    "channels, table_size",
    [
        (3, 4),
        (3, 16),
        (3, 36),
        (4, 4),
        (4, 16),
        (4, 36),
    ],
)
@pytest.mark.parametrize("mode", RGB_MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_lut(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
    channels: int,
    table_size: int,
) -> None:
    im = make_pillow_image(mode, size)
    if channels == 3:
        lut = ImageFilter.Color3DLUT.generate(
            table_size, lambda r, g, b: (r, g, b), channels, "RGB"
        )
    else:
        lut = ImageFilter.Color3DLUT.generate(
            table_size, lambda r, g, b: (r, g, b, r), channels, "RGBA"
        )

    bench.extra_info["label"] = [f"{table_size}³ table to {channels}D"]
    bench(im.filter, lut)


@pytest.mark.benchmark(group="transform")
@pytest.mark.parametrize(
    "method, data",
    [
        (Transform.AFFINE, (1.1, 0.1, -20, 0.05, 0.95, -10)),
        (Transform.PERSPECTIVE, (1.0, 0.1, -20, 0.05, 1.0, -10, 0.0002, 0.0001)),
        (Transform.QUAD, (10, 20, 5, 1000, 1010, 1005, 1005, 8)),
    ],
    ids=["AFFINE", "PERSPECTIVE", "QUAD"],
)
@pytest.mark.parametrize(
    "resample",
    [Resampling.NEAREST, Resampling.BILINEAR, Resampling.BICUBIC],
    ids=lambda r: r.name,
)
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_transform(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
    method: Transform,
    data: tuple[float, ...],
    resample: Resampling,
) -> None:
    im = make_pillow_image(mode, size)
    bench.extra_info["label"] = [method.name, resample.name]
    bench(im.transform, size, method, data, resample)


@pytest.mark.benchmark(group="rotate_right")
@pytest.mark.parametrize("op", Transpose, ids=lambda t: t.name)
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_rotate_right(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
    op: Transpose,
) -> None:
    im = make_pillow_image(mode, size)
    bench.extra_info["label"] = [op.name]
    bench(im.transpose, op)


@pytest.mark.benchmark(group="draw")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_draw_rectangle(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
) -> None:
    # Exercise various fill functions.
    im = Image.new(mode, size)
    draw = ImageDraw.Draw(im)
    nbands = len(im.getbands())
    ink = (200, 50, 25, 255)[:nbands] if nbands > 1 else 200
    w, h = size
    bench(lambda: draw.rectangle((0, 0, w - 1, h - 1), fill=ink))


@pytest.mark.benchmark(group="draw")
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_draw_rectangle_blend(bench: BenchmarkFixture, size: tuple[int, int]) -> None:
    # Exercise fill functions with blending.
    im = Image.new("RGB", size)
    draw = ImageDraw.Draw(im, "RGBA")
    w, h = size
    bench(lambda: draw.rectangle((0, 0, w - 1, h - 1), fill=(200, 50, 25, 127)))


@pytest.mark.benchmark(group="draw")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_draw_polygon(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
) -> None:
    # Exercise the polygon scanline filler, which is not the rectangle fast path.
    im = Image.new(mode, size)
    draw = ImageDraw.Draw(im)
    nbands = len(im.getbands())
    ink = (200, 50, 25, 255)[:nbands] if nbands > 1 else 200
    w, h = size
    xy = [(0, 0), (w - 1, 30), (w - 20, h - 1), (10, h - 20)]
    bench(lambda: draw.polygon(xy, fill=ink))


def _zigzag(size: tuple[int, int], segments: int = 16) -> list[tuple[int, int]]:
    w, h = size
    return [
        (0 if i % 2 == 0 else w - 1, i * (h - 1) // segments)
        for i in range(segments + 1)
    ]


@pytest.mark.benchmark(group="draw")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_draw_lines(bench: BenchmarkFixture, mode: str, size: tuple[int, int]) -> None:
    # Exercise point-by-point line drawing (a polyline is a single C call).
    im = Image.new(mode, size)
    draw = ImageDraw.Draw(im)
    nbands = len(im.getbands())
    ink = (200, 50, 25, 255)[:nbands] if nbands > 1 else 200
    xy = _zigzag(size)
    bench(lambda: draw.line(xy, fill=ink))


@pytest.mark.benchmark(group="draw")
@pytest.mark.parametrize("alpha", [0, 127, 255])
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_draw_lines_blend(
    bench: BenchmarkFixture,
    size: tuple[int, int],
    alpha: int,
) -> None:
    # Exercise line drawing with blending; alpha 0 and 255 have fast paths.
    im = Image.new("RGB", size)
    draw = ImageDraw.Draw(im, "RGBA")
    xy = _zigzag(size)
    bench.extra_info["label"] = [f"alpha={alpha}"]
    bench(lambda: draw.line(xy, fill=(200, 50, 25, alpha)))


@pytest.mark.benchmark(group="load")
@pytest.mark.parametrize("path", PATHS, ids=_format_path)
def test_load(bench: BenchmarkFixture, path: pathlib.Path) -> None:
    def run() -> None:
        with Image.open(path) as im:
            im.load()

    bench(run)


@pytest.mark.benchmark(group="save")
@pytest.mark.parametrize("path", PATHS, ids=_format_path)
def test_save_jpeg(bench: BenchmarkFixture, path: pathlib.Path) -> None:
    with Image.open(path) as im:
        im.load()
    bench(lambda: im.save(BytesIO(), format="JPEG", quality=85))


@pytest.mark.benchmark(group="allocate")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_allocate(bench: BenchmarkFixture, mode: str, size: tuple[int, int]) -> None:
    bench.extra_info["label"] = [f"mode {mode}"]
    bench(Image.new, mode, size)


@pytest.mark.benchmark(group="allocate")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_unpack(bench: BenchmarkFixture, mode: str, size: tuple[int, int]) -> None:
    im = make_pillow_image(mode, size)
    data = im.tobytes()
    bench.extra_info["label"] = [f"Unpack from {mode}"]
    bench(im.frombytes, data)


@pytest.mark.benchmark(group="allocate")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_pack(bench: BenchmarkFixture, mode: str, size: tuple[int, int]) -> None:
    im = make_pillow_image(mode, size)
    bench.extra_info["label"] = [f"Pack to {mode}"]
    bench(im.tobytes)


@pytest.mark.benchmark(group="allocate")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_split(bench: BenchmarkFixture, mode: str, size: tuple[int, int]) -> None:
    im = make_pillow_image(mode, size)
    bench.extra_info["label"] = [f"split {mode}"]
    bench(im.split)


@pytest.mark.benchmark(group="allocate")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_getband(bench: BenchmarkFixture, mode: str, size: tuple[int, int]) -> None:
    im = make_pillow_image(mode, size)
    band = len(im.getbands()) - 1
    bench.extra_info["label"] = [f"get {mode[band]} of {mode}"]
    bench(im.getchannel, band)


@pytest.mark.benchmark(group="allocate")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_merge(bench: BenchmarkFixture, mode: str, size: tuple[int, int]) -> None:
    im = make_pillow_image(mode, size)
    bands = im.split()
    bench.extra_info["label"] = [f"merge {mode}"]
    bench(Image.merge, mode, bands)


@pytest.mark.benchmark(group="allocate")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_fill(bench: BenchmarkFixture, mode: str, size: tuple[int, int]) -> None:
    nbands = len(Image.new(mode, (1, 1)).getbands())
    color = (10, 20, 30, 40)[:nbands] if nbands > 1 else 10
    bench.extra_info["label"] = [f"fill {mode}"]
    bench(Image.new, mode, size, color)


@pytest.mark.benchmark(group="allocate")
@pytest.mark.parametrize("mode", ["1", "F", "I", "L", "P"])
def test_linear_gradient(bench: BenchmarkFixture, mode: str) -> None:
    result = bench(Image.linear_gradient, mode)
    assert result.size == (256, 256)
    assert result.mode == mode


@pytest.mark.benchmark(group="allocate")
@pytest.mark.parametrize("mode", ["1", "F", "I", "L", "P"])
def test_radial_gradient(bench: BenchmarkFixture, mode: str) -> None:
    result = bench(Image.radial_gradient, mode)
    assert result.size == (256, 256)
    assert result.mode == mode


CHOPS_OPS = [
    ImageChops.add,
    ImageChops.subtract,
    ImageChops.multiply,
    ImageChops.screen,
    ImageChops.difference,
    ImageChops.lighter,
    ImageChops.darker,
    ImageChops.add_modulo,
    ImageChops.soft_light,
    ImageChops.hard_light,
    ImageChops.overlay,
]


@pytest.mark.benchmark(group="chops")
@pytest.mark.parametrize("op", CHOPS_OPS, ids=lambda f: f.__name__)
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_chops(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
    op: Callable[[Image.Image, Image.Image], Image.Image],
) -> None:
    im1 = make_pillow_image(mode, size)
    im2 = make_pillow_image(mode, size, seed=1)
    bench.extra_info["label"] = [op.__name__]
    result = bench(op, im1, im2)
    assert result.size == im1.size


@pytest.mark.benchmark(group="chops")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_invert(bench: BenchmarkFixture, mode: str, size: tuple[int, int]) -> None:
    im = make_pillow_image(mode, size)
    bench.extra_info["label"] = ["invert"]
    bench(ImageChops.invert, im)


@pytest.mark.benchmark(group="chops")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_offset(bench: BenchmarkFixture, mode: str, size: tuple[int, int]) -> None:
    im = make_pillow_image(mode, size)
    bench.extra_info["label"] = ["offset"]
    bench(ImageChops.offset, im, 123, 45)


@pytest.mark.benchmark(group="extrema")
@pytest.mark.parametrize("mode", ["L", "LA", "I", "F", "RGB", "RGBA", "CMYK"])
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_getextrema(bench: BenchmarkFixture, mode: str, size: tuple[int, int]) -> None:
    im = make_pillow_image(mode, size)
    bench.extra_info["label"] = [f"extrema {mode}"]
    bench(im.getextrema)


@pytest.mark.benchmark(group="bbox")
@pytest.mark.parametrize("scenario", list(BBOX_SCENARIOS))
@pytest.mark.parametrize("mode", ["L", "LA", "I;16", "RGB", "RGBA"])
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_getbbox(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
    scenario: str,
) -> None:
    im = make_bbox_image(mode, size, BBOX_SCENARIOS[scenario])
    bench.extra_info["label"] = [scenario]
    bench(im.getbbox)


@pytest.mark.benchmark(group="histogram")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_histogram(bench: BenchmarkFixture, mode: str, size: tuple[int, int]) -> None:
    im = make_pillow_image(mode, size)
    bench.extra_info["label"] = [f"histogram {mode}"]
    bench(im.histogram)


@pytest.mark.benchmark(group="histogram")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_histogram_masked(
    bench: BenchmarkFixture, mode: str, size: tuple[int, int]
) -> None:
    im = make_pillow_image(mode, size)
    mask = make_pillow_image("L", size)
    bench.extra_info["label"] = [f"masked histogram {mode}"]
    bench(im.histogram, mask)


L_MATRIX = (0.299, 0.587, 0.114, 0.0)
RGB_MATRIX = (
    0.412, 0.357, 0.180, 0.0,
    0.212, 0.715, 0.072, 0.0,
    0.019, 0.119, 0.950, 0.0,
)  # fmt: skip


@pytest.mark.benchmark(group="convert")
@pytest.mark.parametrize(
    "mode_to, matrix",
    [("L", L_MATRIX), ("RGB", RGB_MATRIX)],
)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_matrix_convert(
    bench: BenchmarkFixture,
    mode_to: str,
    matrix: tuple[float, ...],
    size: tuple[int, int],
) -> None:
    im = make_pillow_image("RGB", size)
    bench.extra_info["label"] = [f"matrix RGB to {mode_to}"]
    bench(im.convert, mode_to, matrix)


@pytest.mark.benchmark(group="point")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_point_lut(bench: BenchmarkFixture, mode: str, size: tuple[int, int]) -> None:
    im = make_pillow_image(mode, size)
    lut = [255 - i for i in range(256)] * len(im.getbands())
    bench.extra_info["label"] = [f"LUT {mode}"]
    bench(im.point, lut)


@pytest.mark.benchmark(group="point")
@pytest.mark.parametrize("mode", ["I", "F", "LA", "RGBA"])
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_point_transform(
    bench: BenchmarkFixture, mode: str, size: tuple[int, int]
) -> None:
    im = make_pillow_image(mode, size)
    bench.extra_info["label"] = [f"transform {mode}"]
    bench(im.point, lambda v: v * 1.5 + 3.0)


@pytest.mark.benchmark(group="font")
@pytest.mark.parametrize("mode", ["", "1", "L"])
def test_font_getmask(bench: BenchmarkFixture, mode: str) -> None:
    font = ImageFont.load_default_imagefont()
    text = "The quick brown fox jumps over the lazy dog. " * 8
    bench.extra_info["label"] = [f"getmask mode {mode!r}"]
    mask = bench(font.getmask, text, mode)
    assert mask.size[0] > 0


@pytest.mark.benchmark(group="quantize")
@pytest.mark.parametrize("mode", [m for m in MODES if m in ("L", "RGB", "RGBA")])
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_quantize(bench: BenchmarkFixture, mode: str, size: tuple[int, int]) -> None:
    im = make_pillow_image(mode, size)
    bench.extra_info["label"] = [f"quantize {mode}"]
    result = bench(im.quantize, 256)
    assert result.mode == "P"


@pytest.mark.benchmark(group="quantize")
@pytest.mark.parametrize("output_mode", ["P", "PA"])
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_quantize_grayscale_to_palette(
    bench: BenchmarkFixture,
    output_mode: str,
    size: tuple[int, int],
) -> None:
    im = make_pillow_image("L", size)
    bench.extra_info["label"] = [f"quantize L to {output_mode}"]
    result = bench(im.convert, output_mode)
    assert result.mode == output_mode
    assert result.convert("L").tobytes() == im.tobytes()


@pytest.mark.benchmark(group="quantize")
@pytest.mark.parametrize(
    "dither",
    [Image.Dither.NONE, Image.Dither.FLOYDSTEINBERG],
    ids=["none", "floyd-steinberg"],
)
@pytest.mark.parametrize("output_mode", ["P", "PA"])
@pytest.mark.parametrize(
    "source_type",
    [
        "synthetic",
        *(pytest.param(image, id=f"{image.stem}") for image in PATHS),
    ],
)
@pytest.mark.parametrize("palette_type", ["exact", "grayscale", "web"])
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_quantize_to_palette(
    bench: BenchmarkFixture,
    benchmark_save: BenchmarkSave,
    dither: Image.Dither,
    output_mode: str,
    source_type: str | pathlib.Path,
    palette_type: str,
    size: tuple[int, int],
) -> None:
    if isinstance(source_type, pathlib.Path):
        with Image.open(source_type) as source_im:
            im = source_im.convert("RGB").resize(size)
    elif source_type == "synthetic":
        im = make_pillow_image("RGB", size)
    if palette_type == "exact":
        palette = im.quantize(256)
        im = palette.convert("RGB")
    elif palette_type == "web":
        palette = Image.new("RGB", (1, 1)).convert(
            "P",
            palette=Image.Palette.WEB,
            dither=Image.Dither.NONE,
        )
    else:
        palette = Image.new("P", (1, 1))
        palette.putpalette(tuple(channel for i in range(256) for channel in (i, i, i)))

    bench.extra_info["label"] = [
        (
            f"{source_type} RGB to {output_mode}, "
            f"{palette_type} palette, "
            f"{dither.name.lower()} dither"
        ),
    ]
    if output_mode == "P":
        result = bench(im.quantize, palette=palette, dither=dither)
    else:
        result = bench(lambda: im._new(im.im.convert(output_mode, dither, palette.im)))
    assert result.mode == output_mode
    benchmark_save(result)
