from PIL import ImagePalette

from .helper import PillowTestCase, hopper


class TestImagePutPalette(PillowTestCase):
    def test_putpalette(self):
        def palette(mode):
            im = hopper(mode).copy()
            im.putpalette(list(range(256)) * 3)
            p = im.getpalette()
            if p:
                return im.mode, p[:10]
            return im.mode

        self.assertRaises(ValueError, palette, "1")
        for mode in ["L", "LA", "P", "PA"]:
            self.assertEqual(
                palette(mode),
                ("PA" if "A" in mode else "P", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
            )
        self.assertRaises(ValueError, palette, "I")
        self.assertRaises(ValueError, palette, "F")
        self.assertRaises(ValueError, palette, "RGB")
        self.assertRaises(ValueError, palette, "RGBA")
        self.assertRaises(ValueError, palette, "YCbCr")

    def test_imagepalette(self):
        im = hopper("P")
        im.putpalette(ImagePalette.negative())
        im.putpalette(ImagePalette.random())
        im.putpalette(ImagePalette.sepia())
        im.putpalette(ImagePalette.wedge())
