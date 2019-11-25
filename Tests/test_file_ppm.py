from PIL import Image

from .helper import PillowTestCase, hopper

# sample ppm stream
test_file = "Tests/images/hopper.ppm"


class TestFilePpm(PillowTestCase):
    def test_sanity(self):
        with Image.open(test_file) as im:
            im.load()
            self.assertEqual(im.mode, "RGB")
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.format, "PPM")
            self.assertEqual(im.get_format_mimetype(), "image/x-portable-pixmap")

    def test_16bit_pgm(self):
        with Image.open("Tests/images/16_bit_binary.pgm") as im:
            im.load()
            self.assertEqual(im.mode, "I")
            self.assertEqual(im.size, (20, 100))
            self.assertEqual(im.get_format_mimetype(), "image/x-portable-graymap")

            with Image.open("Tests/images/16_bit_binary_pgm.png") as tgt:
                self.assert_image_equal(im, tgt)

    def test_16bit_pgm_write(self):
        with Image.open("Tests/images/16_bit_binary.pgm") as im:
            im.load()

            f = self.tempfile("temp.pgm")
            im.save(f, "PPM")

            with Image.open(f) as reloaded:
                self.assert_image_equal(im, reloaded)

    def test_pnm(self):
        with Image.open("Tests/images/hopper.pnm") as im:
            self.assert_image_similar(im, hopper(), 0.0001)

            f = self.tempfile("temp.pnm")
            im.save(f)

            with Image.open(f) as reloaded:
                self.assert_image_equal(im, reloaded)

    def test_truncated_file(self):
        path = self.tempfile("temp.pgm")
        with open(path, "w") as f:
            f.write("P6")

        self.assertRaises(ValueError, Image.open, path)

    def test_neg_ppm(self):
        # Storage.c accepted negative values for xsize, ysize.  the
        # internal open_ppm function didn't check for sanity but it
        # has been removed. The default opener doesn't accept negative
        # sizes.

        with self.assertRaises(IOError):
            Image.open("Tests/images/negative_size.ppm")

    def test_mimetypes(self):
        path = self.tempfile("temp.pgm")

        with open(path, "w") as f:
            f.write("P4\n128 128\n255")
        with Image.open(path) as im:
            self.assertEqual(im.get_format_mimetype(), "image/x-portable-bitmap")

        with open(path, "w") as f:
            f.write("PyCMYK\n128 128\n255")
        with Image.open(path) as im:
            self.assertEqual(im.get_format_mimetype(), "image/x-portable-anymap")
