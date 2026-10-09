from __future__ import annotations

from pathlib import Path

import pytest

from PIL import Image

from .helper import assert_image_equal, hopper


@pytest.mark.parametrize(
    "mode, dest_modes",
    (
        ("L", ["I", "F", "LA", "RGB", "RGBA", "RGBX", "CMYK", "YCbCr", "HSV"]),
        ("I", ["L", "F"]),  # Technically I;32 can work for any 4x8bit storage.
        ("F", ["I", "L", "LA", "RGB", "RGBA", "RGBX", "CMYK", "YCbCr", "HSV"]),
        ("LA", ["L", "F"]),
        ("RGB", ["L", "F"]),
        ("RGBA", ["L", "F"]),
        ("RGBX", ["L", "F"]),
        ("CMYK", ["L", "F"]),
        ("YCbCr", ["L", "F"]),
        ("HSV", ["L", "F"]),
    ),
)
def test_invalid_array_type(mode: str, dest_modes: list[str]) -> None:
    img = hopper(mode)
    for dest_mode in dest_modes:
        with pytest.raises(ValueError):
            Image.fromarrow(img, dest_mode, img.size)


def test_invalid_array_size() -> None:
    img = hopper("RGB")

    assert img.size != (10, 10)
    with pytest.raises(ValueError):
        Image.fromarrow(img, "RGB", (10, 10))


def test_release_schema() -> None:
    # these should not error out, valgrind should be clean
    img = hopper("L")
    schema = img.__arrow_c_schema__()
    del schema


def test_release_array() -> None:
    # these should not error out, valgrind should be clean
    img = hopper("L")
    array, schema = img.__arrow_c_array__()
    del array
    del schema


def test_readonly() -> None:
    img = hopper("L")
    reloaded = Image.fromarrow(img, img.mode, img.size)
    assert reloaded.readonly == 1
    reloaded._readonly = 0
    assert reloaded.readonly == 1


def test_multiblock_l_image() -> None:
    block_size = Image.core.get_block_size()

    # check a 2 block image in single channel mode
    size = (4096, 2 * block_size // 4096)
    img = Image.new("L", size, 128)

    with pytest.raises(ValueError):
        schema, arr = img.__arrow_c_array__()


def test_multiblock_rgba_image() -> None:
    block_size = Image.core.get_block_size()

    # check a 2 block image in 4 channel mode
    size = (4096, (block_size // 4096) // 2)
    img = Image.new("RGBA", size, (128, 127, 126, 125))

    with pytest.raises(ValueError):
        schema, arr = img.__arrow_c_array__()


def test_multiblock_l_schema() -> None:
    block_size = Image.core.get_block_size()

    # check a 2 block image in single channel mode
    size = (4096, 2 * block_size // 4096)
    img = Image.new("L", size, 128)

    with pytest.raises(ValueError):
        img.__arrow_c_schema__()


def test_multiblock_rgba_schema() -> None:
    block_size = Image.core.get_block_size()

    # check a 2 block image in 4 channel mode
    size = (4096, (block_size // 4096) // 2)
    img = Image.new("RGBA", size, (128, 127, 126, 125))

    with pytest.raises(ValueError):
        img.__arrow_c_schema__()


@pytest.mark.usefixtures("enable_block_allocator")
def test_singleblock_l_image() -> None:
    block_size = Image.core.get_block_size()

    # check a 2 block image in 4 channel mode
    size = (4096, 2 * (block_size // 4096))
    img = Image.new("L", size, 128)
    assert img.im.isblock()

    schema, arr = img.__arrow_c_array__()
    assert schema
    assert arr


@pytest.mark.usefixtures("enable_block_allocator")
def test_singleblock_rgba_image() -> None:
    block_size = Image.core.get_block_size()

    # check a 2 block image in 4 channel mode
    size = (4096, (block_size // 4096) // 2)
    img = Image.new("RGBA", size, (128, 127, 126, 125))
    assert img.im.isblock()

    schema, arr = img.__arrow_c_array__()
    assert schema
    assert arr


@pytest.mark.usefixtures("enable_block_allocator")
def test_singleblock_l_schema() -> None:
    block_size = Image.core.get_block_size()

    # check a 2 block image in single channel mode
    size = (4096, 2 * block_size // 4096)
    img = Image.new("L", size, 128)
    assert img.im.isblock()

    schema = img.__arrow_c_schema__()
    assert schema


@pytest.mark.usefixtures("enable_block_allocator")
def test_singleblock_rgba_schema() -> None:
    block_size = Image.core.get_block_size()

    # check a 2 block image in 4 channel mode
    size = (4096, (block_size // 4096) // 2)
    img = Image.new("RGBA", size, (128, 127, 126, 125))
    assert img.im.isblock()

    schema = img.__arrow_c_schema__()
    assert schema


@pytest.mark.usefixtures("aligned_arena")
@pytest.mark.parametrize("mode", ("L", "RGBA"))
def test_aligned_rows_not_contiguous(mode: str) -> None:
    # Rows are padded to the alignment, so they aren't back to back
    img = hopper(mode).crop((0, 0, 3, 3))

    with pytest.raises(ValueError, match="not contiguous"):
        img.__arrow_c_array__()
    with pytest.raises(ValueError, match="not contiguous"):
        img.__arrow_c_schema__()


@pytest.mark.usefixtures("aligned_arena")
@pytest.mark.parametrize("mode, width", (("L", 64), ("RGBA", 16)))
def test_aligned_rows_contiguous(mode: str, width: int) -> None:
    # Rows are exactly the alignment, so there is no padding,
    # but the first row may start after the start of the block
    for height in range(1, 9):
        img = hopper(mode).crop((0, 0, width, height))

        reloaded = Image.fromarrow(img, img.mode, img.size)
        assert_image_equal(img, reloaded)


@pytest.mark.parametrize("mode", ("L", "RGBA"))
def test_mapped_image(mode: str) -> None:
    expected = hopper(mode).crop((0, 0, 5, 3))
    img = Image.frombuffer(mode, expected.size, expected.tobytes(), "raw", mode, 0, 1)

    reloaded = Image.fromarrow(img, img.mode, img.size)
    assert_image_equal(expected, reloaded)


@pytest.mark.parametrize(
    "mode, ext",
    (("L", "tif"), ("RGBA", "tif"), ("L", "ppm")),
)
def test_mapped_file(tmp_path: Path, mode: str, ext: str) -> None:
    expected = hopper(mode)
    filename = tmp_path / f"temp.{ext}"
    expected.save(filename)

    with Image.open(filename) as im:
        im.load()
        assert im.map is not None  # memory-mapped
        reloaded = Image.fromarrow(im, im.mode, im.size)
        assert_image_equal(expected, reloaded)


@pytest.mark.parametrize("stride, ystep", ((4, 1), (0, -1)))
def test_mapped_image_not_contiguous(stride: int, ystep: int) -> None:
    img = Image.frombuffer("L", (3, 3), bytes(range(12)), "raw", "L", stride, ystep)

    with pytest.raises(ValueError, match="not contiguous"):
        img.__arrow_c_array__()


@pytest.mark.parametrize("use_block_allocator", (0, 1))
@pytest.mark.parametrize("size", ((0, 0), (0, 3), (3, 0)))
@pytest.mark.parametrize("mode", ("L", "RGBA"))
def test_empty_image(
    mode: str, size: tuple[int, int], use_block_allocator: int
) -> None:
    Image.core.set_use_block_allocator(use_block_allocator)
    try:
        img = Image.new(mode, size)
    finally:
        Image.core.set_use_block_allocator(0)

    schema, array = img.__arrow_c_array__()
    assert schema
    assert array


@pytest.mark.parametrize("mode", ("L", "RGBA"))
def test_frombuffer_image(mode: str) -> None:
    # Trigger from GHSA-4fj2-qr5f-54hc
    # Fixed, no error from GHSA-654x-cwwv-5j9c
    size = (4, 4)
    buffer = bytes(size[0] * size[1] * Image.getmodebands(mode))
    img = Image.frombuffer(mode, size, buffer, "raw", mode, 0, 1)

    img2 = Image.fromarrow(img, mode, img.size)
    assert img2.tobytes()


def test_mapped_image(tmp_path: Path) -> None:
    # Trigger from GHSA-4fj2-qr5f-54hc
    # Fixed, no error from GHSA-654x-cwwv-5j9c
    path = tmp_path / "temp.pgm"
    hopper("L").save(path)

    with Image.open(path) as img:
        img.load()
        assert img.map is not None

        img2 = Image.fromarrow(img, img.mode, img.size)
        assert img2.tobytes()
