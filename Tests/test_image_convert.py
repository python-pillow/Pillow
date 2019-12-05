from PIL import Image

from .helper import PillowTestCase, hopper


class TestImageConvert(PillowTestCase):
    def test_sanity(self):
        def convert(im, mode):
            out = im.convert(mode)
            self.assertEqual(out.mode, mode)
            self.assertEqual(out.size, im.size)

        modes = (
            "1",
            "L",
            "LA",
            "P",
            "PA",
            "I",
            "F",
            "RGB",
            "RGBA",
            "RGBX",
            "CMYK",
            "YCbCr",
            "HSV",
        )

        for mode in modes:
            im = hopper(mode)
            for mode in modes:
                convert(im, mode)

            # Check 0
            im = Image.new(mode, (0, 0))
            for mode in modes:
                convert(im, mode)

    def test_default(self):

        im = hopper("P")
        self.assert_image(im, "P", im.size)
        im = im.convert()
        self.assert_image(im, "RGB", im.size)
        im = im.convert()
        self.assert_image(im, "RGB", im.size)

    # ref https://github.com/python-pillow/Pillow/issues/274

    def _test_float_conversion(self, im):
        orig = im.getpixel((5, 5))
        converted = im.convert("F").getpixel((5, 5))
        self.assertEqual(orig, converted)

    def test_8bit(self):
        with Image.open("Tests/images/hopper.jpg") as im:
            self._test_float_conversion(im.convert("L"))

    def test_16bit(self):
        with Image.open("Tests/images/16bit.cropped.tif") as im:
            self._test_float_conversion(im)

    def test_16bit_workaround(self):
        with Image.open("Tests/images/16bit.cropped.tif") as im:
            self._test_float_conversion(im.convert("I"))

    def test_rgba_p(self):
        im = hopper("RGBA")
        im.putalpha(hopper("L"))

        converted = im.convert("P")
        comparable = converted.convert("RGBA")

        self.assert_image_similar(im, comparable, 20)

    def test_trns_p(self):
        im = hopper("P")
        im.info["transparency"] = 0

        f = self.tempfile("temp.png")

        im_l = im.convert("L")
        self.assertEqual(im_l.info["transparency"], 0)  # undone
        im_l.save(f)

        im_rgb = im.convert("RGB")
        self.assertEqual(im_rgb.info["transparency"], (0, 0, 0))  # undone
        im_rgb.save(f)

    # ref https://github.com/python-pillow/Pillow/issues/664

    def test_trns_p_rgba(self):
        # Arrange
        im = hopper("P")
        im.info["transparency"] = 128

        # Act
        im_rgba = im.convert("RGBA")

        # Assert
        self.assertNotIn("transparency", im_rgba.info)
        # https://github.com/python-pillow/Pillow/issues/2702
        self.assertIsNone(im_rgba.palette)

    def test_trns_l(self):
        im = hopper("L")
        im.info["transparency"] = 128

        f = self.tempfile("temp.png")

        im_rgb = im.convert("RGB")
        self.assertEqual(im_rgb.info["transparency"], (128, 128, 128))  # undone
        im_rgb.save(f)

        im_p = im.convert("P")
        self.assertIn("transparency", im_p.info)
        im_p.save(f)

        im_p = self.assert_warning(UserWarning, im.convert, "P", palette=Image.ADAPTIVE)
        self.assertNotIn("transparency", im_p.info)
        im_p.save(f)

    def test_trns_RGB(self):
        im = hopper("RGB")
        im.info["transparency"] = im.getpixel((0, 0))

        f = self.tempfile("temp.png")

        im_l = im.convert("L")
        self.assertEqual(im_l.info["transparency"], im_l.getpixel((0, 0)))  # undone
        im_l.save(f)

        im_p = im.convert("P")
        self.assertIn("transparency", im_p.info)
        im_p.save(f)

        im_rgba = im.convert("RGBA")
        self.assertNotIn("transparency", im_rgba.info)
        im_rgba.save(f)

        im_p = self.assert_warning(UserWarning, im.convert, "P", palette=Image.ADAPTIVE)
        self.assertNotIn("transparency", im_p.info)
        im_p.save(f)

    def test_gif_with_rgba_palette_to_p(self):
        # See https://github.com/python-pillow/Pillow/issues/2433
        with Image.open("Tests/images/hopper.gif") as im:
            im.info["transparency"] = 255
            im.load()
            self.assertEqual(im.palette.mode, "RGBA")
            im_p = im.convert("P")

        # Should not raise ValueError: unrecognized raw mode
        im_p.load()

    def test_p_la(self):
        im = hopper("RGBA")
        alpha = hopper("L")
        im.putalpha(alpha)

        comparable = im.convert("P").convert("LA").getchannel("A")

        self.assert_image_similar(alpha, comparable, 5)

    def test_matrix_illegal_conversion(self):
        # Arrange
        im = hopper("CMYK")
        # fmt: off
        matrix = (
            0.412453, 0.357580, 0.180423, 0,
            0.212671, 0.715160, 0.072169, 0,
            0.019334, 0.119193, 0.950227, 0)
        # fmt: on
        self.assertNotEqual(im.mode, "RGB")

        # Act / Assert
        self.assertRaises(ValueError, im.convert, mode="CMYK", matrix=matrix)

    def test_matrix_wrong_mode(self):
        # Arrange
        im = hopper("L")
        # fmt: off
        matrix = (
            0.412453, 0.357580, 0.180423, 0,
            0.212671, 0.715160, 0.072169, 0,
            0.019334, 0.119193, 0.950227, 0)
        # fmt: on
        self.assertEqual(im.mode, "L")

        # Act / Assert
        self.assertRaises(ValueError, im.convert, mode="L", matrix=matrix)

    def test_matrix_xyz(self):
        def matrix_convert(mode):
            # Arrange
            im = hopper("RGB")
            im.info["transparency"] = (255, 0, 0)
            # fmt: off
            matrix = (
                0.412453, 0.357580, 0.180423, 0,
                0.212671, 0.715160, 0.072169, 0,
                0.019334, 0.119193, 0.950227, 0)
            # fmt: on
            self.assertEqual(im.mode, "RGB")

            # Act
            # Convert an RGB image to the CIE XYZ colour space
            converted_im = im.convert(mode=mode, matrix=matrix)

            # Assert
            self.assertEqual(converted_im.mode, mode)
            self.assertEqual(converted_im.size, im.size)
            with Image.open("Tests/images/hopper-XYZ.png") as target:
                if converted_im.mode == "RGB":
                    self.assert_image_similar(converted_im, target, 3)
                    self.assertEqual(converted_im.info["transparency"], (105, 54, 4))
                else:
                    self.assert_image_similar(converted_im, target.getchannel(0), 1)
                    self.assertEqual(converted_im.info["transparency"], 105)

        matrix_convert("RGB")
        matrix_convert("L")

    def test_matrix_identity(self):
        # Arrange
        im = hopper("RGB")
        # fmt: off
        identity_matrix = (
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0)
        # fmt: on
        self.assertEqual(im.mode, "RGB")

        # Act
        # Convert with an identity matrix
        converted_im = im.convert(mode="RGB", matrix=identity_matrix)

        # Assert
        # No change
        self.assert_image_equal(converted_im, im)
