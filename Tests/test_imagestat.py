from helper import unittest, PillowTestCase, hopper

from PIL import Image
from PIL import ImageStat


class TestImageStat(PillowTestCase):

    def test_sanity(self):

        im = hopper()

        st = ImageStat.Stat(im)
        st = ImageStat.Stat(im.histogram())
        st = ImageStat.Stat(im, Image.new("1", im.size, 1))

        # Check these run. Exceptions will cause failures.
        st.extrema
        st.sum
        st.mean
        st.median
        st.rms
        st.sum2
        st.var
        st.stddev

        self.assertRaises(AttributeError, lambda: st.spam)

        self.assertRaises(TypeError, lambda: ImageStat.Stat(1))

    def test_hopper(self):

        im = hopper()

        st = ImageStat.Stat(im)

        # verify a few values
        self.assertEqual(st.extrema[0], (0, 255))
        self.assertEqual(st.median[0], 72)
        self.assertEqual(st.sum[0], 1470218)
        self.assertEqual(st.sum[1], 1311896)
        self.assertEqual(st.sum[2], 1563008)

    def test_constant(self):

        im = Image.new("L", (128, 128), 128)

        st = ImageStat.Stat(im)

        self.assertEqual(st.extrema[0], (128, 128))
        self.assertEqual(st.sum[0], 128**3)
        self.assertEqual(st.sum2[0], 128**4)
        self.assertEqual(st.mean[0], 128)
        self.assertEqual(st.median[0], 128)
        self.assertEqual(st.rms[0], 128)
        self.assertEqual(st.var[0], 0)
        self.assertEqual(st.stddev[0], 0)


if __name__ == '__main__':
    unittest.main()
