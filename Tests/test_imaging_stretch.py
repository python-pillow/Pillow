"""
Tests for ImagingCore.stretch functionality.
"""

from helper import unittest, PillowTestCase

from PIL import Image


im = Image.open("Tests/images/hopper.ppm").copy()


class TestImagingStretch(PillowTestCase):

    def test_modes(self):
        self.assertRaises(ValueError, im.convert("1").im.stretch,
                          (15, 12), Image.ANTIALIAS)
        self.assertRaises(ValueError, im.convert("P").im.stretch,
                          (15, 12), Image.ANTIALIAS)
        for mode in ["L", "I", "F", "RGB", "RGBA", "CMYK", "YCbCr"]:
            s = im.convert(mode).im
            r = s.stretch((15, 12), Image.ANTIALIAS)
            self.assertEqual(r.mode, mode)
            self.assertEqual(r.size, (15, 12))
            self.assertEqual(r.bands, s.bands)

    def test_reduce_filters(self):
        # There is no Image.NEAREST because im.stretch implementation
        # is not NEAREST for reduction. It should be removed
        # or renamed to supersampling.
        for f in [Image.BILINEAR, Image.BICUBIC, Image.ANTIALIAS]:
            r = im.im.stretch((15, 12), f)
            self.assertEqual(r.mode, "RGB")
            self.assertEqual(r.size, (15, 12))

    def test_enlarge_filters(self):
        for f in [Image.BILINEAR, Image.BICUBIC, Image.ANTIALIAS]:
            r = im.im.stretch((764, 414), f)
            self.assertEqual(r.mode, "RGB")
            self.assertEqual(r.size, (764, 414))

    def test_endianess(self):
        # Make an image with one colored pixel, in one channel.
        # When stretched, that channel should be the same as a GS image.
        # Other channels should be unaffected.
        # The R and A channels should not swap, which is indicitive of
        # an endianess issues

        im = Image.new('L', (2,2), 0)
        im.putpixel((1,1),128)

        blank = Image.new('L', (4,4), 0)
        alpha = Image.new('L', (4,4), 255)

        for f in [Image.BILINEAR, Image.BICUBIC, Image.ANTIALIAS]:

            im_r = Image.new('RGBA', (2,2), (0,0,0,255))
            im_r.putpixel((1,1),(128,0,0,255))

            target = im._new(im.im.stretch((4,4), f))
            stretched = im_r._new(im_r.im.stretch((4,4),f))

            self.assert_image_equal(stretched.split()[0],target)
            self.assert_image_equal(stretched.split()[1],blank)
            self.assert_image_equal(stretched.split()[2],blank)
            self.assert_image_equal(stretched.split()[3],alpha)


            im_r = Image.new('RGB', (2,2), (0,0,0))
            im_r.putpixel((1,1),(128,0,0))

            target = im._new(im.im.stretch((4,4), f))
            stretched = im_r._new(im_r.im.stretch((4,4),f))

            #print " ".join(hex(ord(s)) for s in stretched.split()[0].tobytes())
            #print " ".join(hex(ord(s)) for s in stretched.split()[1].tobytes())
            #print " ".join(hex(ord(s)) for s in stretched.split()[2].tobytes())

            #print " ".join(hex(ord(s)) for s in target.tobytes())

            #print

            self.assert_image_equal(stretched.split()[0],target, 'rxRGB R channel fail')
            self.assert_image_equal(stretched.split()[1],blank, 'rxRGB G channel fail')
            self.assert_image_equal(stretched.split()[2],blank, 'rxRGB B channel fail')


            im_g = Image.new('RGBA', (2,2), (0,0,0,255))
            im_g.putpixel((1,1),(0,128,0,255))

            stretched = im_g._new(im_g.im.stretch((4,4),f))

            self.assert_image_equal(stretched.split()[0],blank)
            self.assert_image_equal(stretched.split()[1],target)
            self.assert_image_equal(stretched.split()[2],blank)
            self.assert_image_equal(stretched.split()[3],alpha)


            im_g = Image.new('RGB', (2,2), (0,0,0))
            im_g.putpixel((1,1),(0,128,0))

            target = im._new(im.im.stretch((4,4), f))
            stretched = im_g._new(im_g.im.stretch((4,4),f))

            self.assert_image_equal(stretched.split()[0],blank, 'gxRGB R channel fail')
            self.assert_image_equal(stretched.split()[1],target, 'gxRGB G channel fail')
            self.assert_image_equal(stretched.split()[2],blank, 'gxRGB B channel fail')


if __name__ == '__main__':
    unittest.main()

# End of file
