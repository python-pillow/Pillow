from helper import unittest, PillowTestCase, tearDownModule, lena

from PIL import Image
from PIL import ImageEnhance


class TestImageEnhance(PillowTestCase):

    def test_sanity(self):

        # FIXME: assert_image
        # Implicit asserts no exception:
        ImageEnhance.Color(lena()).enhance(0.5)
        ImageEnhance.Contrast(lena()).enhance(0.5)
        ImageEnhance.Brightness(lena()).enhance(0.5)
        ImageEnhance.Sharpness(lena()).enhance(0.5)

    def test_crash(self):

        # crashes on small images
        im = Image.new("RGB", (1, 1))
        ImageEnhance.Sharpness(im).enhance(0.5)


if __name__ == '__main__':
    unittest.main()

# End of file
