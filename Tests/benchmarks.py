"""
pytest-benchmark tests for Pillow features.
"""

from __future__ import annotations

import pathlib
from io import BytesIO

import pytest

from PIL import Image, ImageFilter
from PIL.Image import Resampling, Transpose

TYPE_CHECKING = False

if TYPE_CHECKING:
    from pytest_benchmark.fixture import (  # type: ignore[import-not-found]
        BenchmarkFixture,
    )

pytest.importorskip(
    "pytest_benchmark",
    reason="benchmarks.py requires pytest-benchmark",
)

# These can be adjusted to add more modes to benchmark
# (however all features benchmarked might not support all PIL modes).
MODES = ["RGB", "RGBA", "L", "LA"]

# The size for generated test images.
# Note that adjusting this will naturally change how long operations take.
# The `bench` fixture takes care of saving this information in the extra info
# for the benchmark run, so that throughput (Mpx/s) can be recomputed in the future.
SIZES = [(1024, 1024)]

# For benchmarks that act on test fixture files, these are the paths loaded.
IMAGES_PATH = pathlib.Path(__file__).parent / "images"
PATHS = [
    IMAGES_PATH / "flower2.jpg",
]

# These are derived from the other configuration, above.
RGB_MODES = [mode for mode in MODES if mode.startswith("RGB")]
ALPHA_MODES = [mode for mode in MODES if mode.endswith("A")]


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


def make_pillow_image(
    mode: str,
    size: tuple[int, int],
    pattern_offset: int = 0,
) -> Image.Image:
    im = Image.new("RGB", size)
    n = im.width * im.height * 3
    period = bytes((i + pattern_offset) % 256 for i in range(256))
    im.frombytes((period * (n // 256 + 1))[:n])
    return im.convert(mode)


@pytest.mark.benchmark(group="composition")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_blend(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
) -> None:
    im1 = make_pillow_image(mode, size)
    im2 = make_pillow_image(mode, size, pattern_offset=1024)
    result = bench(Image.blend, im1, im2, 0.5)
    assert result.size == im1.size


@pytest.mark.benchmark(group="scale")
@pytest.mark.parametrize("resampler", Resampling, ids=lambda r: r.name)
@pytest.mark.parametrize("scale", [0.01, 0.125, 0.8, 2.14])
@pytest.mark.parametrize("mode", MODES)
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
@pytest.mark.parametrize("mode", ALPHA_MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_alpha_composition(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
) -> None:
    im = make_pillow_image(mode, size)
    second = im.copy()
    bench.extra_info["label"] = ["Composition"]
    bench(Image.alpha_composite, im, second)


@pytest.mark.benchmark(group="convert")
@pytest.mark.parametrize(
    "mode_from, mode_to",
    [
        ("RGB", "L"),
        ("RGBA", "LA"),
        ("RGBa", "RGBA"),
        ("RGBA", "RGBa"),
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
@pytest.mark.parametrize("mode", MODES)
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
