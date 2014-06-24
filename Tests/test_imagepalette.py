from helper import unittest, PillowTestCase, tearDownModule

from PIL import ImagePalette

ImagePalette = ImagePalette.ImagePalette


class TestImagePalette(PillowTestCase):

    def test_sanity(self):

        ImagePalette("RGB", list(range(256))*3)
        self.assertRaises(
            ValueError, lambda: ImagePalette("RGB", list(range(256))*2))

    def test_getcolor(self):

        palette = ImagePalette()

        map = {}
        for i in range(256):
            map[palette.getcolor((i, i, i))] = i

        self.assertEqual(len(map), 256)
        self.assertRaises(ValueError, lambda: palette.getcolor((1, 2, 3)))

    def test_file(self):

        palette = ImagePalette("RGB", list(range(256))*3)

        f = self.tempfile("temp.lut")

        palette.save(f)

        from PIL.ImagePalette import load, raw

        p = load(f)

        # load returns raw palette information
        self.assertEqual(len(p[0]), 768)
        self.assertEqual(p[1], "RGB")

        p = raw(p[1], p[0])
        self.assertIsInstance(p, ImagePalette)
        self.assertEqual(p.palette, palette.tobytes())

if __name__ == '__main__':
    unittest.main()

# End of file
