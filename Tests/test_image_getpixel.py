from helper import unittest, PillowTestCase

from PIL import Image

Image.USE_CFFI_ACCESS = False


def color(mode):
    bands = Image.getmodebands(mode)
    if bands == 1:
        return 1
    else:
        return tuple(range(1, bands+1))


class TestImageGetPixel(PillowTestCase):

    def check(self, mode, c=None):
        if not c:
            c = color(mode)

        # check putpixel
        im = Image.new(mode, (1, 1), None)
        im.putpixel((0, 0), c)
        self.assertEqual(
            im.getpixel((0, 0)), c,
            "put/getpixel roundtrip failed for mode %s, color %s" % (mode, c))

        # check inital color
        im = Image.new(mode, (1, 1), c)
        self.assertEqual(
            im.getpixel((0, 0)), c,
            "initial color failed for mode %s, color %s " % (mode, color))

    def test_basic(self):
        for mode in ("1", "L", "LA", "I", "I;16", "I;16B", "F",
                     "P", "PA", "RGB", "RGBA", "RGBX", "CMYK", "YCbCr"):
            self.check(mode)

    def test_signedness(self):
        # see https://github.com/python-pillow/Pillow/issues/452
        # pixelaccess is using signed int* instead of uint*
        for mode in ("I;16", "I;16B"):
            self.check(mode, 2**15-1)
            self.check(mode, 2**15)
            self.check(mode, 2**15+1)
            self.check(mode, 2**16-1)


if __name__ == '__main__':
    unittest.main()

# End of file
