from fractions import Fraction

from PIL import Image, TiffImagePlugin, features
from PIL.TiffImagePlugin import IFDRational

from .helper import PillowTestCase, hopper


class Test_IFDRational(PillowTestCase):
    def _test_equal(self, num, denom, target):

        t = IFDRational(num, denom)

        assert target == t
        assert t == target

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
        assert xres._val is not None
        assert xres.numerator is not None
        assert xres.denominator is not None
        assert yres._val is not None

        assert xres and 1
        assert xres and yres

    def test_ifd_rational_save(self):
        methods = (True, False)
        if not features.check("libtiff"):
            methods = (False,)

        for libtiff in methods:
            TiffImagePlugin.WRITE_LIBTIFF = libtiff

            im = hopper()
            out = self.tempfile("temp.tiff")
            res = IFDRational(301, 1)
            im.save(out, dpi=(res, res), compression="raw")

            with Image.open(out) as reloaded:
                assert float(IFDRational(301, 1)) == float(reloaded.tag_v2[282])
