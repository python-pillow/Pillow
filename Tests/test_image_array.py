import pytest

from PIL import Image

from .helper import hopper

numpy = pytest.importorskip("numpy", reason="NumPy not installed")

im = hopper().resize((128, 100))


def test_toarray():
    def test(mode):
        ai = numpy.array(im.convert(mode))
        return ai.shape, ai.dtype.str, ai.nbytes

    def test_with_dtype(dtype):
        ai = numpy.array(im, dtype=dtype)
        assert ai.dtype == dtype

    # assert test("1") == ((100, 128), '|b1', 1600))
    assert test("L") == ((100, 128), "|u1", 12800)

    # FIXME: wrong?
    assert test("I") == ((100, 128), Image._ENDIAN + "i4", 51200)
    # FIXME: wrong?
    assert test("F") == ((100, 128), Image._ENDIAN + "f4", 51200)

    assert test("LA") == ((100, 128, 2), "|u1", 25600)
    assert test("RGB") == ((100, 128, 3), "|u1", 38400)
    assert test("RGBA") == ((100, 128, 4), "|u1", 51200)
    assert test("RGBX") == ((100, 128, 4), "|u1", 51200)

    test_with_dtype(numpy.float64)
    test_with_dtype(numpy.uint8)

    with Image.open("Tests/images/truncated_jpeg.jpg") as im_truncated:
        with pytest.raises(OSError):
            numpy.array(im_truncated)


def test_fromarray():
    class Wrapper:
        """Class with API matching Image.fromarray"""

        def __init__(self, img, arr_params):
            self.img = img
            self.__array_interface__ = arr_params

        def tobytes(self):
            return self.img.tobytes()

    def test(mode):
        i = im.convert(mode)
        a = numpy.array(i)
        # Make wrapper instance for image, new array interface
        wrapped = Wrapper(
            i,
            {
                "shape": a.shape,
                "typestr": a.dtype.str,
                "version": 3,
                "data": a.data,
                "strides": 1,  # pretend it's non-contiguous
            },
        )
        out = Image.fromarray(wrapped)
        return out.mode, out.size, list(i.getdata()) == list(out.getdata())

    # assert test("1") == ("1", (128, 100), True)
    assert test("L") == ("L", (128, 100), True)
    assert test("I") == ("I", (128, 100), True)
    assert test("F") == ("F", (128, 100), True)
    assert test("LA") == ("LA", (128, 100), True)
    assert test("RGB") == ("RGB", (128, 100), True)
    assert test("RGBA") == ("RGBA", (128, 100), True)
    assert test("RGBX") == ("RGBA", (128, 100), True)

    # Test mode is None with no "typestr" in the array interface
    with pytest.raises(TypeError):
        wrapped = Wrapper(test("L"), {"shape": (100, 128)})
        Image.fromarray(wrapped)
