from helper import unittest, PillowTestCase, tearDownModule

from PIL import ImageFilter


class TestImageFilter(PillowTestCase):

    def test_sanity(self):
        # see test_image_filter for more tests

        # Check these run. Exceptions cause failures.
        ImageFilter.MaxFilter
        ImageFilter.MedianFilter
        ImageFilter.MinFilter
        ImageFilter.ModeFilter
        ImageFilter.Kernel((3, 3), list(range(9)))
        ImageFilter.GaussianBlur
        ImageFilter.GaussianBlur(5)
        ImageFilter.UnsharpMask
        ImageFilter.UnsharpMask(10)

        ImageFilter.BLUR
        ImageFilter.CONTOUR
        ImageFilter.DETAIL
        ImageFilter.EDGE_ENHANCE
        ImageFilter.EDGE_ENHANCE_MORE
        ImageFilter.EMBOSS
        ImageFilter.FIND_EDGES
        ImageFilter.SMOOTH
        ImageFilter.SMOOTH_MORE
        ImageFilter.SHARPEN


if __name__ == '__main__':
    unittest.main()

# End of file
