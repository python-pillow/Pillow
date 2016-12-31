from helper import unittest, PillowTestCase, hopper

from PIL import Image, SgiImagePlugin


class TestFileSgi(PillowTestCase):

    def test_rgb(self):
        # Created with ImageMagick then renamed:
        # convert hopper.ppm -compress None sgi:hopper.rgb
        test_file = "Tests/images/hopper.rgb"

        im = Image.open(test_file)
        self.assert_image_equal(im, hopper())

    def test_l(self):
        # Created with ImageMagick
        # convert hopper.ppm -monochrome -compress None sgi:hopper.bw
        test_file = "Tests/images/hopper.bw"

        im = Image.open(test_file)
        self.assert_image_similar(im, hopper('L'), 2)

    def test_rgba(self):
        # Created with ImageMagick:
        # convert transparent.png -compress None transparent.sgi
        test_file = "Tests/images/transparent.sgi"
        
        im = Image.open(test_file)
        target = Image.open('Tests/images/transparent.png')
        self.assert_image_equal(im, target)

    def test_rle(self):
        # convert hopper.ppm  hopper.sgi
        # We don't support RLE compression, this should throw a value error
        test_file = "Tests/images/hopper.sgi"

        with self.assertRaises(ValueError):
            Image.open(test_file)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(ValueError,
                          lambda:
                          SgiImagePlugin.SgiImageFile(invalid_file))

    def test_write(self):
        def roundtrip(img):
            out = self.tempfile('temp.sgi')
            img.save(out, format='sgi')
            reloaded = Image.open(out)
            self.assert_image_equal(img, reloaded)

        for mode in ('L', 'RGB', 'RGBA'):
            roundtrip(hopper(mode))



if __name__ == '__main__':
    unittest.main()
