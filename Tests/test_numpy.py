import unittest

from PIL import Image

from .helper import PillowTestCase, hopper

try:
    import numpy
except ImportError:
    numpy = None


TEST_IMAGE_SIZE = (10, 10)


@unittest.skipIf(numpy is None, "Numpy is not installed")
class TestNumpy(PillowTestCase):
    def test_numpy_to_image(self):
        def to_image(dtype, bands=1, boolean=0):
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
        self.assert_image(to_image(numpy.bool, 1, 1), "1", TEST_IMAGE_SIZE)
        self.assert_image(to_image(numpy.bool8, 1, 1), "1", TEST_IMAGE_SIZE)

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
        if Image._ENDIAN == "<":
            self.assert_image(to_image(numpy.uint16), "I;16", TEST_IMAGE_SIZE)
        else:
            self.assert_image(to_image(numpy.uint16), "I;16B", TEST_IMAGE_SIZE)

        self.assert_image(to_image(numpy.int16), "I", TEST_IMAGE_SIZE)

        # Check 32-bit integer formats
        self.assert_image(to_image(numpy.uint32), "I", TEST_IMAGE_SIZE)
        self.assert_image(to_image(numpy.int32), "I", TEST_IMAGE_SIZE)

        # Check 64-bit integer formats
        self.assertRaises(TypeError, to_image, numpy.uint64)
        self.assertRaises(TypeError, to_image, numpy.int64)

        # Check floating-point formats
        self.assert_image(to_image(numpy.float), "F", TEST_IMAGE_SIZE)
        self.assertRaises(TypeError, to_image, numpy.float16)
        self.assert_image(to_image(numpy.float32), "F", TEST_IMAGE_SIZE)
        self.assert_image(to_image(numpy.float64), "F", TEST_IMAGE_SIZE)

        self.assert_image(to_image(numpy.uint8, 2), "LA", (10, 10))
        self.assert_image(to_image(numpy.uint8, 3), "RGB", (10, 10))
        self.assert_image(to_image(numpy.uint8, 4), "RGBA", (10, 10))

    # based on an erring example at
    # https://stackoverflow.com/questions/10854903/what-is-causing-dimension-dependent-attributeerror-in-pil-fromarray-function
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
        for x in range(0, img.size[0], int(img.size[0] / 10)):
            for y in range(0, img.size[1], int(img.size[1] / 10)):
                self.assert_deep_equal(px[x, y], np[y, x])

    def test_16bit(self):
        with Image.open("Tests/images/16bit.cropped.tif") as img:
            np_img = numpy.array(img)
            self._test_img_equals_nparray(img, np_img)
        self.assertEqual(np_img.dtype, numpy.dtype("<u2"))

    def test_1bit(self):
        # Test that 1-bit arrays convert to numpy and back
        # See: https://github.com/python-pillow/Pillow/issues/350
        arr = numpy.array([[1, 0, 0, 1, 0], [0, 1, 0, 0, 0]], "u1")
        img = Image.fromarray(arr * 255).convert("1")
        self.assertEqual(img.mode, "1")
        arr_back = numpy.array(img)
        numpy.testing.assert_array_equal(arr, arr_back)

    def test_save_tiff_uint16(self):
        # Tests that we're getting the pixel value in the right byte order.
        pixel_value = 0x1234
        a = numpy.array(
            [pixel_value] * TEST_IMAGE_SIZE[0] * TEST_IMAGE_SIZE[1], dtype=numpy.uint16
        )
        a.shape = TEST_IMAGE_SIZE
        img = Image.fromarray(a)

        img_px = img.load()
        self.assertEqual(img_px[0, 0], pixel_value)

    def test_to_array(self):
        def _to_array(mode, dtype):
            img = hopper(mode)

            # Resize to non-square
            img = img.crop((3, 0, 124, 127))
            self.assertEqual(img.size, (121, 127))

            np_img = numpy.array(img)
            self._test_img_equals_nparray(img, np_img)
            self.assertEqual(np_img.dtype, dtype)

        modes = [
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
        ]

        for mode in modes:
            _to_array(*mode)

    def test_point_lut(self):
        # see https://github.com/python-pillow/Pillow/issues/439

        data = list(range(256)) * 3
        lut = numpy.array(data, dtype=numpy.uint8)

        im = hopper()

        im.point(lut)

    def test_putdata(self):
        # shouldn't segfault
        # see https://github.com/python-pillow/Pillow/issues/1008

        im = Image.new("F", (150, 100))
        arr = numpy.zeros((15000,), numpy.float32)
        im.putdata(arr)

        self.assertEqual(len(im.getdata()), len(arr))

    def test_roundtrip_eye(self):
        for dtype in (
            numpy.bool,
            numpy.bool8,
            numpy.int8,
            numpy.int16,
            numpy.int32,
            numpy.uint8,
            numpy.uint16,
            numpy.uint32,
            numpy.float,
            numpy.float32,
            numpy.float64,
        ):
            arr = numpy.eye(10, dtype=dtype)
            numpy.testing.assert_array_equal(arr, numpy.array(Image.fromarray(arr)))

    def test_zero_size(self):
        # Shouldn't cause floating point exception
        # See https://github.com/python-pillow/Pillow/issues/2259

        im = Image.fromarray(numpy.empty((0, 0), dtype=numpy.uint8))

        self.assertEqual(im.size, (0, 0))

    def test_bool(self):
        # https://github.com/python-pillow/Pillow/issues/2044
        a = numpy.zeros((10, 2), dtype=numpy.bool)
        a[0][0] = True

        im2 = Image.fromarray(a)
        self.assertEqual(im2.getdata()[0], 255)

    def test_no_resource_warning_for_numpy_array(self):
        # https://github.com/python-pillow/Pillow/issues/835
        # Arrange
        from numpy import array

        test_file = "Tests/images/hopper.png"
        with Image.open(test_file) as im:

            # Act/Assert
            self.assert_warning(None, lambda: array(im))
