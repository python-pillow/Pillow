from PIL import Image, SgiImagePlugin

from .helper import PillowTestCase, hopper


class TestFileSgi(PillowTestCase):
    def test_rgb(self):
        # Created with ImageMagick then renamed:
        # convert hopper.ppm -compress None sgi:hopper.rgb
        test_file = "Tests/images/hopper.rgb"

        with Image.open(test_file) as im:
            self.assert_image_equal(im, hopper())
            self.assertEqual(im.get_format_mimetype(), "image/rgb")

    def test_rgb16(self):
        test_file = "Tests/images/hopper16.rgb"

        with Image.open(test_file) as im:
            self.assert_image_equal(im, hopper())

    def test_l(self):
        # Created with ImageMagick
        # convert hopper.ppm -monochrome -compress None sgi:hopper.bw
        test_file = "Tests/images/hopper.bw"

        with Image.open(test_file) as im:
            self.assert_image_similar(im, hopper("L"), 2)
            self.assertEqual(im.get_format_mimetype(), "image/sgi")

    def test_rgba(self):
        # Created with ImageMagick:
        # convert transparent.png -compress None transparent.sgi
        test_file = "Tests/images/transparent.sgi"

        with Image.open(test_file) as im:
            with Image.open("Tests/images/transparent.png") as target:
                self.assert_image_equal(im, target)
            self.assertEqual(im.get_format_mimetype(), "image/sgi")

    def test_rle(self):
        # Created with ImageMagick:
        # convert hopper.ppm  hopper.sgi
        test_file = "Tests/images/hopper.sgi"

        with Image.open(test_file) as im:
            with Image.open("Tests/images/hopper.rgb") as target:
                self.assert_image_equal(im, target)

    def test_rle16(self):
        test_file = "Tests/images/tv16.sgi"

        with Image.open(test_file) as im:
            with Image.open("Tests/images/tv.rgb") as target:
                self.assert_image_equal(im, target)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(ValueError, SgiImagePlugin.SgiImageFile, invalid_file)

    def test_write(self):
        def roundtrip(img):
            out = self.tempfile("temp.sgi")
            img.save(out, format="sgi")
            with Image.open(out) as reloaded:
                self.assert_image_equal(img, reloaded)

        for mode in ("L", "RGB", "RGBA"):
            roundtrip(hopper(mode))

        # Test 1 dimension for an L mode image
        roundtrip(Image.new("L", (10, 1)))

    def test_write16(self):
        test_file = "Tests/images/hopper16.rgb"

        with Image.open(test_file) as im:
            out = self.tempfile("temp.sgi")
            im.save(out, format="sgi", bpc=2)

            with Image.open(out) as reloaded:
                self.assert_image_equal(im, reloaded)

    def test_unsupported_mode(self):
        im = hopper("LA")
        out = self.tempfile("temp.sgi")

        self.assertRaises(ValueError, im.save, out, format="sgi")
