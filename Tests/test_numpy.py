from __future__ import print_function
import sys
from helper import unittest, PillowTestCase, hopper

from PIL import Image

try:
    import site
    import numpy
    assert site  # silence warning
    assert numpy  # silence warning
except ImportError:
    # Skip via setUp()
    pass

TEST_IMAGE_SIZE = (10, 10)

# Numpy on pypy as of pypy 5.3.1 is corrupting the numpy.array(Image)
# call such that it's returning a object of type numpy.ndarray, but
# the repr is that of a PIL.Image. Size and shape are 1 and (), not the
# size and shape of the array. This causes failures in several tests.
SKIP_NUMPY_ON_PYPY = hasattr(sys, 'pypy_version_info') and (
    sys.pypy_version_info <= (5, 3, 1, 'final', 0))


class TestNumpy(PillowTestCase):

    def setUp(self):
        try:
            import site
            import numpy
            assert site  # silence warning
            assert numpy  # silence warning
        except ImportError:
            self.skipTest("ImportError")

    def test_numpy_to_image(self):

        def to_image(dtype, bands=1, boolean=0):
            if bands == 1:
                if boolean:
                    data = [0, 1] * 50
                else:
                    data = list(range(100))
                a = numpy.array(data, dtype=dtype)
                a.shape = TEST_IMAGE_SIZE
                i = Image.fromarray(a)
                if list(i.getdata()) != data:
                    print("data mismatch for", dtype)
            else:
                data = list(range(100))
                a = numpy.array([[x]*bands for x in data], dtype=dtype)
                a.shape = TEST_IMAGE_SIZE[0], TEST_IMAGE_SIZE[1], bands
                i = Image.fromarray(a)
                if list(i.split()[0].getdata()) != list(range(100)):
                    print("data mismatch for", dtype)
            # print(dtype, list(i.getdata()))
            return i

        # Check supported 1-bit integer formats
        self.assertRaises(TypeError, lambda: to_image(numpy.bool))
        self.assertRaises(TypeError, lambda: to_image(numpy.bool8))

        # Check supported 8-bit integer formats
        self.assert_image(to_image(numpy.uint8), "L", TEST_IMAGE_SIZE)
        self.assert_image(to_image(numpy.uint8, 3), "RGB", TEST_IMAGE_SIZE)
        self.assert_image(to_image(numpy.uint8, 4), "RGBA", TEST_IMAGE_SIZE)
        self.assert_image(to_image(numpy.int8), "I", TEST_IMAGE_SIZE)

        # Check non-fixed-size integer types
        # These may fail, depending on the platform, since we have no native
        # 64 bit int image types.
        # self.assert_image(to_image(numpy.uint), "I", TEST_IMAGE_SIZE)
        # self.assert_image(to_image(numpy.int), "I", TEST_IMAGE_SIZE)

        # Check 16-bit integer formats
        if Image._ENDIAN == '<':
            self.assert_image(to_image(numpy.uint16), "I;16", TEST_IMAGE_SIZE)
        else:
            self.assert_image(to_image(numpy.uint16), "I;16B", TEST_IMAGE_SIZE)

        self.assert_image(to_image(numpy.int16), "I", TEST_IMAGE_SIZE)

        # Check 32-bit integer formats
        self.assert_image(to_image(numpy.uint32), "I", TEST_IMAGE_SIZE)
        self.assert_image(to_image(numpy.int32), "I", TEST_IMAGE_SIZE)

        # Check 64-bit integer formats
        self.assertRaises(TypeError, lambda: to_image(numpy.uint64))
        self.assertRaises(TypeError, lambda: to_image(numpy.int64))

        # Check floating-point formats
        self.assert_image(to_image(numpy.float), "F", TEST_IMAGE_SIZE)
        self.assertRaises(TypeError, lambda: to_image(numpy.float16))
        self.assert_image(to_image(numpy.float32), "F", TEST_IMAGE_SIZE)
        self.assert_image(to_image(numpy.float64), "F", TEST_IMAGE_SIZE)

        self.assert_image(to_image(numpy.uint8, 2), "LA", (10, 10))
        self.assert_image(to_image(numpy.uint8, 3), "RGB", (10, 10))
        self.assert_image(to_image(numpy.uint8, 4), "RGBA", (10, 10))

    # based on an erring example at
    # http://stackoverflow.com/questions/10854903/what-is-causing-dimension-dependent-attributeerror-in-pil-fromarray-function
    def test_3d_array(self):
        size = (5, TEST_IMAGE_SIZE[0], TEST_IMAGE_SIZE[1])
        a = numpy.ones(size, dtype=numpy.uint8)
        self.assert_image(Image.fromarray(a[1, :, :]), "L", TEST_IMAGE_SIZE)
        size = (TEST_IMAGE_SIZE[0], 5, TEST_IMAGE_SIZE[1])
        a = numpy.ones(size, dtype=numpy.uint8)
        self.assert_image(Image.fromarray(a[:, 1, :]), "L", TEST_IMAGE_SIZE)
        size = (TEST_IMAGE_SIZE[0], TEST_IMAGE_SIZE[1], 5)
        a = numpy.ones(size, dtype=numpy.uint8)
        self.assert_image(Image.fromarray(a[:, :, 1]), "L", TEST_IMAGE_SIZE)

    def _test_img_equals_nparray(self, img, np):
        self.assertGreaterEqual(len(np.shape), 2)
        np_size = np.shape[1], np.shape[0]
        self.assertEqual(img.size, np_size)
        px = img.load()
        for x in range(0, img.size[0], int(img.size[0]/10)):
            for y in range(0, img.size[1], int(img.size[1]/10)):
                self.assert_deep_equal(px[x, y], np[y, x])

    @unittest.skipIf(SKIP_NUMPY_ON_PYPY, "numpy.array(Image) is flaky on PyPy")
    def test_16bit(self):
        img = Image.open('Tests/images/16bit.cropped.tif')
        np_img = numpy.array(img)
        self._test_img_equals_nparray(img, np_img)
        self.assertEqual(np_img.dtype, numpy.dtype('<u2'))

    def test_1bit(self):
        # Test that 1-bit arrays convert to numpy and back
        # See: https://github.com/python-pillow/Pillow/issues/350
        arr = numpy.array([[1, 0, 0, 1, 0], [0, 1, 0, 0, 0]], 'u1')
        img = Image.fromarray(arr * 255).convert('1')
        self.assertEqual(img.mode, '1')
        arr_back = numpy.array(img)
        numpy.testing.assert_array_equal(arr, arr_back)

    def test_save_tiff_uint16(self):
        # Tests that we're getting the pixel value in the right byte order.
        pixel_value = 0x1234
        a = numpy.array([pixel_value] * TEST_IMAGE_SIZE[0] * TEST_IMAGE_SIZE[1], dtype=numpy.uint16)
        a.shape = TEST_IMAGE_SIZE
        img = Image.fromarray(a)

        img_px = img.load()
        self.assertEqual(img_px[0, 0], pixel_value)

    @unittest.skipIf(SKIP_NUMPY_ON_PYPY, "numpy.array(Image) is flaky on PyPy")
    def test_to_array(self):

        def _to_array(mode, dtype):
            img = hopper(mode)

            # Resize to non-square
            img = img.crop((3, 0, 124, 127))
            self.assertEqual(img.size, (121, 127))

            np_img = numpy.array(img)
            self._test_img_equals_nparray(img, np_img)
            self.assertEqual(np_img.dtype, numpy.dtype(dtype))

        modes = [("L", 'uint8'),
                 ("I", 'int32'),
                 ("F", 'float32'),
                 ("LA", 'uint8'),
                 ("RGB", 'uint8'),
                 ("RGBA", 'uint8'),
                 ("RGBX", 'uint8'),
                 ("CMYK", 'uint8'),
                 ("YCbCr", 'uint8'),
                 ("I;16", '<u2'),
                 ("I;16B", '>u2'),
                 ("I;16L", '<u2'),
                 ("HSV", 'uint8'),
                 ]

        for mode in modes:
            _to_array(*mode)

    def test_point_lut(self):
        # see https://github.com/python-pillow/Pillow/issues/439

        data = list(range(256))*3
        lut = numpy.array(data, dtype='uint8')

        im = hopper()

        im.point(lut)

    def test_putdata(self):
        # shouldn't segfault
        # see https://github.com/python-pillow/Pillow/issues/1008

        im = Image.new('F', (150, 100))
        arr = numpy.zeros((15000,), numpy.float32)
        im.putdata(arr)

        self.assertEqual(len(im.getdata()), len(arr))


if __name__ == '__main__':
    unittest.main()
