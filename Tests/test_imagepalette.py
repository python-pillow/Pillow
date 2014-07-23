from helper import unittest, PillowTestCase

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

    def test_make_linear_lut(self):
        # Arrange
        from PIL.ImagePalette import make_linear_lut
        black = 0
        white = 255

        # Act
        lut = make_linear_lut(black, white)

        # Assert
        self.assertIsInstance(lut, list)
        self.assertEqual(len(lut), 256)
        # Check values
        for i in range(0, len(lut)):
            self.assertEqual(lut[i], i)

    def test_make_linear_lut_not_yet_implemented(self):
        # Update after FIXME
        # Arrange
        from PIL.ImagePalette import make_linear_lut
        black = 1
        white = 255

        # Act
        self.assertRaises(
            NotImplementedError,
            lambda: make_linear_lut(black, white))

    def test_make_gamma_lut(self):
        # Arrange
        from PIL.ImagePalette import make_gamma_lut
        exp = 5

        # Act
        lut = make_gamma_lut(exp)

        # Assert
        self.assertIsInstance(lut, list)
        self.assertEqual(len(lut), 256)
        # Check a few values
        self.assertEqual(lut[0], 0)
        self.assertEqual(lut[63], 0)
        self.assertEqual(lut[127], 8)
        self.assertEqual(lut[191], 60)
        self.assertEqual(lut[255], 255)

    def test_private_make_linear_lut_warning(self):
        # Arrange
        from PIL.ImagePalette import _make_linear_lut
        black = 0
        white = 255

        # Act / Assert
        self.assert_warning(
            DeprecationWarning,
            lambda: _make_linear_lut(black, white))

    def test_private_make_gamma_lut_warning(self):
        # Arrange
        from PIL.ImagePalette import _make_gamma_lut
        exp = 5

        # Act / Assert
        self.assert_warning(
            DeprecationWarning,
            lambda: _make_gamma_lut(exp))

    def test_rawmode_valueerrors(self):
        # Arrange
        from PIL.ImagePalette import raw
        palette = raw("RGB", list(range(256))*3)

        # Act / Assert
        self.assertRaises(ValueError, lambda: palette.tobytes())
        self.assertRaises(ValueError, lambda: palette.getcolor((1, 2, 3)))
        f = self.tempfile("temp.lut")
        self.assertRaises(ValueError, lambda: palette.save(f))

    def test_getdata(self):
        # Arrange
        data_in = list(range(256))*3
        palette = ImagePalette("RGB", data_in)

        # Act
        mode, data_out = palette.getdata()

        # Assert
        self.assertEqual(mode, "RGB;L")

    def test_rawmode_getdata(self):
        # Arrange
        from PIL.ImagePalette import raw
        data_in = list(range(256))*3
        palette = raw("RGB", data_in)

        # Act
        rawmode, data_out = palette.getdata()

        # Assert
        self.assertEqual(rawmode, "RGB")
        self.assertEqual(data_in, data_out)


if __name__ == '__main__':
    unittest.main()

# End of file
