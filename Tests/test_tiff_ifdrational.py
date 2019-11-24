from fractions import Fraction

from PIL import Image, TiffImagePlugin
from PIL.TiffImagePlugin import IFDRational

from .helper import PillowTestCase, hopper


class Test_IFDRational(PillowTestCase):
    def _test_equal(self, num, denom, target):

        t = IFDRational(num, denom)

        self.assertEqual(target, t)
        self.assertEqual(t, target)

    def test_sanity(self):

        self._test_equal(1, 1, 1)
        self._test_equal(1, 1, Fraction(1, 1))

        self._test_equal(2, 2, 1)
        self._test_equal(1.0, 1, Fraction(1, 1))

        self._test_equal(Fraction(1, 1), 1, Fraction(1, 1))
        self._test_equal(IFDRational(1, 1), 1, 1)

        self._test_equal(1, 2, Fraction(1, 2))
        self._test_equal(1, 2, IFDRational(1, 2))

    def test_nonetype(self):
        # Fails if the _delegate function doesn't return a valid function

        xres = IFDRational(72)
        yres = IFDRational(72)
        self.assertIsNotNone(xres._val)
        self.assertIsNotNone(xres.numerator)
        self.assertIsNotNone(xres.denominator)
        self.assertIsNotNone(yres._val)

        self.assertTrue(xres and 1)
        self.assertTrue(xres and yres)

    def test_ifd_rational_save(self):
        methods = (True, False)
        if "libtiff_encoder" not in dir(Image.core):
            methods = (False,)

        for libtiff in methods:
            TiffImagePlugin.WRITE_LIBTIFF = libtiff

            im = hopper()
            out = self.tempfile("temp.tiff")
            res = IFDRational(301, 1)
            im.save(out, dpi=(res, res), compression="raw")

            with Image.open(out) as reloaded:
                self.assertEqual(
                    float(IFDRational(301, 1)), float(reloaded.tag_v2[282])
                )
