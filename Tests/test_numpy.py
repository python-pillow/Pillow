from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

import pytest

from PIL import Image, _typing

from .helper import assert_deep_equal, assert_image, hopper, skip_unless_feature

if TYPE_CHECKING:
    import numpy
    import numpy.typing as npt
else:
    numpy = pytest.importorskip("numpy", reason="NumPy not installed")

TEST_IMAGE_SIZE = (10, 10)


def test_numpy_to_image() -> None:
    def to_image(dtype: npt.DTypeLike, bands: int = 1, boolean: int = 0) -> Image.Image:
        if bands == 1:
            if boolean:
                data = [0, 255] * 50
            else:
                data = list(range(100))
            a = numpy.array(data, dtype=dtype)
            a.shape = TEST_IMAGE_SIZE
            i = Image.fromarray(a)
            if list(i.getdata()) != data:
                print("data mismatch for", dtype)
        else:
            data = list(range(100))
            a = numpy.array([[x] * bands for x in data], dtype=dtype)
            a.shape = TEST_IMAGE_SIZE[0], TEST_IMAGE_SIZE[1], bands
            i = Image.fromarray(a)
            if list(i.getchannel(0).getdata()) != list(range(100)):
                print("data mismatch for", dtype)
        return i

    # Check supported 1-bit integer formats
    assert_image(to_image(bool, 1, 1), "1", TEST_IMAGE_SIZE)
    assert_image(to_image(numpy.bool_, 1, 1), "1", TEST_IMAGE_SIZE)

    # Check supported 8-bit integer formats
    assert_image(to_image(numpy.uint8), "L", TEST_IMAGE_SIZE)
    assert_image(to_image(numpy.uint8, 3), "RGB", TEST_IMAGE_SIZE)
    assert_image(to_image(numpy.uint8, 4), "RGBA", TEST_IMAGE_SIZE)
    assert_image(to_image(numpy.int8), "I", TEST_IMAGE_SIZE)

    # Check non-fixed-size integer types
    # These may fail, depending on the platform, since we have no native
    # 64-bit int image types.
    # assert_image(to_image(numpy.uint), "I", TEST_IMAGE_SIZE)
    # assert_image(to_image(numpy.int), "I", TEST_IMAGE_SIZE)

    # Check 16-bit integer formats
    if Image._ENDIAN == "<":
        assert_image(to_image(numpy.uint16), "I;16", TEST_IMAGE_SIZE)
    else:
        assert_image(to_image(numpy.uint16), "I;16B", TEST_IMAGE_SIZE)

    assert_image(to_image(numpy.int16), "I", TEST_IMAGE_SIZE)

    # Check 32-bit integer formats
    assert_image(to_image(numpy.uint32), "I", TEST_IMAGE_SIZE)
    assert_image(to_image(numpy.int32), "I", TEST_IMAGE_SIZE)

    # Check 64-bit integer formats
    with pytest.raises(TypeError):
        to_image(numpy.uint64)
    with pytest.raises(TypeError):
        to_image(numpy.int64)

    # Check floating-point formats
    assert_image(to_image(float), "F", TEST_IMAGE_SIZE)
    with pytest.raises(TypeError):
        to_image(numpy.float16)
    assert_image(to_image(numpy.float32), "F", TEST_IMAGE_SIZE)
    assert_image(to_image(numpy.float64), "F", TEST_IMAGE_SIZE)

    assert_image(to_image(numpy.uint8, 2), "LA", (10, 10))
    assert_image(to_image(numpy.uint8, 3), "RGB", (10, 10))
    assert_image(to_image(numpy.uint8, 4), "RGBA", (10, 10))


# Based on an erring example at
# https://stackoverflow.com/questions/10854903/what-is-causing-dimension-dependent-attributeerror-in-pil-fromarray-function
def test_3d_array() -> None:
    size = (5, TEST_IMAGE_SIZE[0], TEST_IMAGE_SIZE[1])
    a = numpy.ones(size, dtype=numpy.uint8)
    assert_image(Image.fromarray(a[1, :, :]), "L", TEST_IMAGE_SIZE)
    size = (TEST_IMAGE_SIZE[0], 5, TEST_IMAGE_SIZE[1])
    a = numpy.ones(size, dtype=numpy.uint8)
    assert_image(Image.fromarray(a[:, 1, :]), "L", TEST_IMAGE_SIZE)
    size = (TEST_IMAGE_SIZE[0], TEST_IMAGE_SIZE[1], 5)
    a = numpy.ones(size, dtype=numpy.uint8)
    assert_image(Image.fromarray(a[:, :, 1]), "L", TEST_IMAGE_SIZE)


def test_1d_array() -> None:
    a = numpy.ones(5, dtype=numpy.uint8)
    assert_image(Image.fromarray(a), "L", (1, 5))


def _test_img_equals_nparray(img: Image.Image, np_img: _typing.NumpyArray) -> None:
    assert len(np_img.shape) >= 2
    np_size = np_img.shape[1], np_img.shape[0]
    assert img.size == np_size
    px = img.load()
    assert px is not None
    for x in range(0, img.size[0], int(img.size[0] / 10)):
        for y in range(0, img.size[1], int(img.size[1] / 10)):
            assert_deep_equal(px[x, y], np_img[y, x])


def test_16bit() -> None:
    with Image.open("Tests/images/16bit.cropped.tif") as img:
        np_img = numpy.array(img)
        _test_img_equals_nparray(img, np_img)
    assert np_img.dtype == numpy.dtype("<u2")


def test_1bit() -> None:
    # Test that 1-bit arrays convert to numpy and back
    # See: https://github.com/python-pillow/Pillow/issues/350
    arr = numpy.array([[1, 0, 0, 1, 0], [0, 1, 0, 0, 0]], "u1")
    img = Image.fromarray(arr * 255).convert("1")
    assert img.mode == "1"
    arr_back = numpy.array(img)
    numpy.testing.assert_array_equal(arr, arr_back)


def test_save_tiff_uint16() -> None:
    # Tests that we're getting the pixel value in the right byte order.
    pixel_value = 0x1234
    a = numpy.array(
        [pixel_value] * TEST_IMAGE_SIZE[0] * TEST_IMAGE_SIZE[1], dtype=numpy.uint16
    )
    a.shape = TEST_IMAGE_SIZE
    img = Image.fromarray(a)

    img_px = img.load()
    assert img_px is not None
    assert img_px[0, 0] == pixel_value


@pytest.mark.parametrize(
    "mode, dtype",
    (
        ("L", numpy.uint8),
        ("I", numpy.int32),
        ("F", numpy.float32),
        ("LA", numpy.uint8),
        ("RGB", numpy.uint8),
        ("RGBA", numpy.uint8),
        ("RGBX", numpy.uint8),
        ("CMYK", numpy.uint8),
        ("YCbCr", numpy.uint8),
        ("I;16", "<u2"),
        ("I;16B", ">u2"),
        ("I;16L", "<u2"),
        ("HSV", numpy.uint8),
    ),
)
def test_to_array(mode: str, dtype: npt.DTypeLike) -> None:
    img = hopper(mode)

    # Resize to non-square
    img = img.crop((3, 0, 124, 127))
    assert img.size == (121, 127)

    np_img = numpy.array(img)
    _test_img_equals_nparray(img, np_img)
    assert np_img.dtype == dtype


def test_point_lut() -> None:
    # See https://github.com/python-pillow/Pillow/issues/439

    data = list(range(256)) * 3
    lut = numpy.array(data, dtype=numpy.uint8)

    im = hopper()

    im.point(lut)


def test_putdata() -> None:
    # Shouldn't segfault
    # See https://github.com/python-pillow/Pillow/issues/1008

    im = Image.new("F", (150, 100))
    arr = numpy.zeros((15000,), numpy.float32)
    im.putdata(arr)

    assert len(im.getdata()) == len(arr)


def test_resize() -> None:
    im = hopper()
    size = (64, 64)

    im_resized = im.resize(numpy.array(size))

    assert im_resized.size == size


@pytest.mark.parametrize(
    "dtype",
    (
        bool,
        numpy.bool_,
        numpy.int8,
        numpy.int16,
        numpy.int32,
        numpy.uint8,
        numpy.uint16,
        numpy.uint32,
        float,
        numpy.float32,
        numpy.float64,
    ),
)
def test_roundtrip_eye(dtype: npt.DTypeLike) -> None:
    arr = numpy.eye(10, dtype=dtype)
    numpy.testing.assert_array_equal(arr, numpy.array(Image.fromarray(arr)))


def test_zero_size() -> None:
    # Shouldn't cause floating point exception
    # See https://github.com/python-pillow/Pillow/issues/2259

    im = Image.fromarray(numpy.empty((0, 0), dtype=numpy.uint8))

    assert im.size == (0, 0)


@skip_unless_feature("libtiff")
def test_transposed() -> None:
    with Image.open("Tests/images/g4_orientation_5.tif") as im:
        assert im.size == (590, 88)

        a = numpy.array(im)
        assert a.shape == (88, 590)


def test_bool() -> None:
    # https://github.com/python-pillow/Pillow/issues/2044
    a = numpy.zeros((10, 2), dtype=bool)
    a[0][0] = True

    im2 = Image.fromarray(a)
    assert im2.getdata()[0] == 255


def test_no_resource_warning_for_numpy_array() -> None:
    # https://github.com/python-pillow/Pillow/issues/835
    # Arrange
    from numpy import array

    test_file = "Tests/images/hopper.png"
    with Image.open(test_file) as im:
        # Act/Assert
        with warnings.catch_warnings():
            array(im)
