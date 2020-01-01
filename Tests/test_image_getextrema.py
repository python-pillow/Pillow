from PIL import Image

from .helper import PillowTestCase, hopper


class TestImageGetExtrema(PillowTestCase):
    def test_extrema(self):
        def extrema(mode):
            return hopper(mode).getextrema()

        self.assertEqual(extrema("1"), (0, 255))
        self.assertEqual(extrema("L"), (1, 255))
        self.assertEqual(extrema("I"), (1, 255))
        self.assertEqual(extrema("F"), (1, 255))
        self.assertEqual(extrema("P"), (0, 225))  # fixed palette
        self.assertEqual(extrema("RGB"), ((0, 255), (0, 255), (0, 255)))
        self.assertEqual(extrema("RGBA"), ((0, 255), (0, 255), (0, 255), (255, 255)))
        self.assertEqual(extrema("CMYK"), ((0, 255), (0, 255), (0, 255), (0, 0)))
        self.assertEqual(extrema("I;16"), (1, 255))

    def test_true_16(self):
        with Image.open("Tests/images/16_bit_noise.tif") as im:
            self.assertEqual(im.mode, "I;16")
            extrema = im.getextrema()
        self.assertEqual(extrema, (106, 285))
