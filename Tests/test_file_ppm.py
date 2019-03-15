from .helper import PillowTestCase, hopper

from PIL import Image

# sample ppm stream
test_file = "Tests/images/hopper.ppm"


class TestFilePpm(PillowTestCase):

    def test_sanity(self):
        im = Image.open(test_file)
        im.load()
        self.assertEqual(im.mode, "RGB")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "PPM")
        self.assertEqual(im.get_format_mimetype(), "image/x-portable-pixmap")

    def test_16bit_pgm(self):
        im = Image.open('Tests/images/16_bit_binary.pgm')
        im.load()
        self.assertEqual(im.mode, 'I')
        self.assertEqual(im.size, (20, 100))
        self.assertEqual(im.get_format_mimetype(), "image/x-portable-graymap")

        tgt = Image.open('Tests/images/16_bit_binary_pgm.png')
        self.assert_image_equal(im, tgt)

    def test_16bit_pgm_write(self):
        im = Image.open('Tests/images/16_bit_binary.pgm')
        im.load()

        f = self.tempfile('temp.pgm')
        im.save(f, 'PPM')

        reloaded = Image.open(f)
        self.assert_image_equal(im, reloaded)

    def test_pnm(self):
        im = Image.open('Tests/images/hopper.pnm')
        self.assert_image_similar(im, hopper(), 0.0001)

        f = self.tempfile('temp.pnm')
        im.save(f)

        reloaded = Image.open(f)
        self.assert_image_equal(im, reloaded)

    def test_truncated_file(self):
        path = self.tempfile('temp.pgm')
        with open(path, 'w') as f:
            f.write('P6')

        self.assertRaises(ValueError, Image.open, path)

    def test_neg_ppm(self):
        # Storage.c accepted negative values for xsize, ysize.  the
        # internal open_ppm function didn't check for sanity but it
        # has been removed. The default opener doesn't accept negative
        # sizes.

        with self.assertRaises(IOError):
            Image.open('Tests/images/negative_size.ppm')

    def test_mimetypes(self):
        path = self.tempfile('temp.pgm')

        with open(path, 'w') as f:
            f.write("P4\n128 128\n255")
        im = Image.open(path)
        self.assertEqual(im.get_format_mimetype(), "image/x-portable-bitmap")

        with open(path, 'w') as f:
            f.write("PyCMYK\n128 128\n255")
        im = Image.open(path)
        self.assertEqual(im.get_format_mimetype(), "image/x-portable-anymap")
