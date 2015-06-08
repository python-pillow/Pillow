from __future__ import print_function
from helper import unittest, PillowTestCase, hopper

from PIL import Image

try:
    import site
    import numpy
except ImportError:
    # Skip via setUp()
    pass


class TestNumpy(PillowTestCase):

    def setUp(self):
        try:
            import site
            import numpy
        except ImportError:
            self.skipTest("ImportError")

    def test_numpy_to_image(self):

        def to_image(dtype, bands=1, bool=0):
            if bands == 1:
                if bool:
                    data = [0, 1] * 50
                else:
                    data = list(range(100))
                a = numpy.array(data, dtype=dtype)
                a.shape = 10, 10
                i = Image.fromarray(a)
                if list(i.getdata()) != data:
                    print("data mismatch for", dtype)
            else:
                data = list(range(100))
                a = numpy.array([[x]*bands for x in data], dtype=dtype)
                a.shape = 10, 10, bands
                i = Image.fromarray(a)
                if list(i.split()[0].getdata()) != list(range(100)):
                    print("data mismatch for", dtype)
            # print dtype, list(i.getdata())
            return i

        # self.assert_image(to_image(numpy.bool, bool=1), "1", (10, 10))
        # self.assert_image(to_image(numpy.bool8, bool=1), "1", (10, 10))

        self.assertRaises(TypeError, lambda: to_image(numpy.uint))
        self.assert_image(to_image(numpy.uint8), "L", (10, 10))
        self.assertRaises(TypeError, lambda: to_image(numpy.uint16))
        self.assertRaises(TypeError, lambda: to_image(numpy.uint32))
        self.assertRaises(TypeError, lambda: to_image(numpy.uint64))

        self.assert_image(to_image(numpy.int8), "I", (10, 10))
        if Image._ENDIAN == '<':  # Little endian
            self.assert_image(to_image(numpy.int16), "I;16", (10, 10))
        else:
            self.assert_image(to_image(numpy.int16), "I;16B", (10, 10))
        self.assert_image(to_image(numpy.int32), "I", (10, 10))
        self.assertRaises(TypeError, lambda: to_image(numpy.int64))

        self.assert_image(to_image(numpy.float), "F", (10, 10))
        self.assert_image(to_image(numpy.float32), "F", (10, 10))
        self.assert_image(to_image(numpy.float64), "F", (10, 10))

        self.assert_image(to_image(numpy.uint8, 3), "RGB", (10, 10))
        self.assert_image(to_image(numpy.uint8, 4), "RGBA", (10, 10))

    # based on an erring example at http://is.gd/6F0esS  (which resolves to)
    # http://stackoverflow.com/questions/10854903/what-is-causing-dimension-dependent-attributeerror-in-pil-fromarray-function
    def test_3d_array(self):
        a = numpy.ones((10, 10, 10), dtype=numpy.uint8)
        self.assert_image(Image.fromarray(a[1, :, :]), "L", (10, 10))
        self.assert_image(Image.fromarray(a[:, 1, :]), "L", (10, 10))
        self.assert_image(Image.fromarray(a[:, :, 1]), "L", (10, 10))

    def _test_img_equals_nparray(self, img, np):
        self.assertEqual(img.size, np.shape[0:2])
        px = img.load()
        for x in range(0, img.size[0], int(img.size[0]/10)):
            for y in range(0, img.size[1], int(img.size[1]/10)):
                self.assert_deep_equal(px[x, y], np[y, x])

    def test_16bit(self):
        img = Image.open('Tests/images/16bit.cropped.tif')
        np_img = numpy.array(img)
        self._test_img_equals_nparray(img, np_img)
        self.assertEqual(np_img.dtype, numpy.dtype('<u2'))

    def test_to_array(self):

        def _to_array(mode, dtype):
            img = hopper(mode)
            np_img = numpy.array(img)
            self._test_img_equals_nparray(img, np_img)
            self.assertEqual(np_img.dtype, numpy.dtype(dtype))

        modes = [("L", 'uint8'),
                 ("I", 'int32'),
                 ("F", 'float32'),
                 ("RGB", 'uint8'),
                 ("RGBA", 'uint8'),
                 ("RGBX", 'uint8'),
                 ("CMYK", 'uint8'),
                 ("YCbCr", 'uint8'),
                 ("I;16", '<u2'),
                 ("I;16B", '>u2'),
                 ("I;16L", '<u2'),
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

# End of file
