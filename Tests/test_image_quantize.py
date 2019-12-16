from PIL import Image

from .helper import PillowTestCase, hopper


class TestImageQuantize(PillowTestCase):
    def test_sanity(self):
        image = hopper()
        converted = image.quantize()
        self.assert_image(converted, "P", converted.size)
        self.assert_image_similar(converted.convert("RGB"), image, 10)

        image = hopper()
        converted = image.quantize(palette=hopper("P"))
        self.assert_image(converted, "P", converted.size)
        self.assert_image_similar(converted.convert("RGB"), image, 60)

    def test_libimagequant_quantize(self):
        image = hopper()
        try:
            converted = image.quantize(100, Image.LIBIMAGEQUANT)
        except ValueError as ex:
            if "dependency" in str(ex).lower():
                self.skipTest("libimagequant support not available")
            else:
                raise
        self.assert_image(converted, "P", converted.size)
        self.assert_image_similar(converted.convert("RGB"), image, 15)
        self.assertEqual(len(converted.getcolors()), 100)

    def test_octree_quantize(self):
        image = hopper()
        converted = image.quantize(100, Image.FASTOCTREE)
        self.assert_image(converted, "P", converted.size)
        self.assert_image_similar(converted.convert("RGB"), image, 20)
        self.assertEqual(len(converted.getcolors()), 100)

    def test_rgba_quantize(self):
        image = hopper("RGBA")
        self.assertRaises(ValueError, image.quantize, method=0)

        self.assertEqual(image.quantize().convert().mode, "RGBA")

    def test_quantize(self):
        with Image.open("Tests/images/caption_6_33_22.png") as image:
            image = image.convert("RGB")
        converted = image.quantize()
        self.assert_image(converted, "P", converted.size)
        self.assert_image_similar(converted.convert("RGB"), image, 1)

    def test_quantize_no_dither(self):
        image = hopper()
        with Image.open("Tests/images/caption_6_33_22.png") as palette:
            palette = palette.convert("P")

        converted = image.quantize(dither=0, palette=palette)
        self.assert_image(converted, "P", converted.size)

    def test_quantize_dither_diff(self):
        image = hopper()
        with Image.open("Tests/images/caption_6_33_22.png") as palette:
            palette = palette.convert("P")

        dither = image.quantize(dither=1, palette=palette)
        nodither = image.quantize(dither=0, palette=palette)

        self.assertNotEqual(dither.tobytes(), nodither.tobytes())
