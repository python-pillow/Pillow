from __future__ import annotations

import pytest

from PIL import Image

from .helper import hopper


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
        (schema, arr) = img.__arrow_c_array__()


def test_multiblock_rgba_image() -> None:
    block_size = Image.core.get_block_size()

    # check a 2 block image in 4 channel mode
    size = (4096, (block_size // 4096) // 2)
    img = Image.new("RGBA", size, (128, 127, 126, 125))

    with pytest.raises(ValueError):
        (schema, arr) = img.__arrow_c_array__()


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


def test_singleblock_l_image() -> None:
    Image.core.set_use_block_allocator(1)

    block_size = Image.core.get_block_size()

    # check a 2 block image in 4 channel mode
    size = (4096, 2 * (block_size // 4096))
    img = Image.new("L", size, 128)
    assert img.im.isblock()

    (schema, arr) = img.__arrow_c_array__()
    assert schema
    assert arr

    Image.core.set_use_block_allocator(0)


def test_singleblock_rgba_image() -> None:
    Image.core.set_use_block_allocator(1)
    block_size = Image.core.get_block_size()

    # check a 2 block image in 4 channel mode
    size = (4096, (block_size // 4096) // 2)
    img = Image.new("RGBA", size, (128, 127, 126, 125))
    assert img.im.isblock()

    (schema, arr) = img.__arrow_c_array__()
    assert schema
    assert arr
    Image.core.set_use_block_allocator(0)


def test_singleblock_l_schema() -> None:
    Image.core.set_use_block_allocator(1)
    block_size = Image.core.get_block_size()

    # check a 2 block image in single channel mode
    size = (4096, 2 * block_size // 4096)
    img = Image.new("L", size, 128)
    assert img.im.isblock()

    schema = img.__arrow_c_schema__()
    assert schema
    Image.core.set_use_block_allocator(0)


def test_singleblock_rgba_schema() -> None:
    Image.core.set_use_block_allocator(1)
    block_size = Image.core.get_block_size()

    # check a 2 block image in 4 channel mode
    size = (4096, (block_size // 4096) // 2)
    img = Image.new("RGBA", size, (128, 127, 126, 125))
    assert img.im.isblock()

    schema = img.__arrow_c_schema__()
    assert schema
    Image.core.set_use_block_allocator(0)
