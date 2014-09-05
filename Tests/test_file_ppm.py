from helper import unittest, PillowTestCase

from PIL import Image

# sample ppm stream
file = "Tests/images/hopper.ppm"
data = open(file, "rb").read()


class TestFilePpm(PillowTestCase):

    def test_sanity(self):
        im = Image.open(file)
        im.load()
        self.assertEqual(im.mode, "RGB")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "PPM")

    def test_16bit_pgm(self):
        im = Image.open('Tests/images/16_bit_binary.pgm')
        im.load()
        self.assertEqual(im.mode, 'I')
        self.assertEqual(im.size, (20, 100))

        tgt = Image.open('Tests/images/16_bit_binary_pgm.png')
        self.assert_image_equal(im, tgt)

    def test_16bit_pgm_write(self):
        im = Image.open('Tests/images/16_bit_binary.pgm')
        im.load()

        f = self.tempfile('temp.pgm')
        im.save(f, 'PPM')

        reloaded = Image.open(f)
        self.assert_image_equal(im, reloaded)


if __name__ == '__main__':
    unittest.main()

# End of file
