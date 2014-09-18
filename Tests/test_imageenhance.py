from helper import unittest, PillowTestCase, hopper

from PIL import Image
from PIL import ImageEnhance


class TestImageEnhance(PillowTestCase):

    def test_sanity(self):

        # FIXME: assert_image
        # Implicit asserts no exception:
        ImageEnhance.Color(hopper()).enhance(0.5)
        ImageEnhance.Contrast(hopper()).enhance(0.5)
        ImageEnhance.Brightness(hopper()).enhance(0.5)
        ImageEnhance.Sharpness(hopper()).enhance(0.5)

    def test_crash(self):

        # crashes on small images
        im = Image.new("RGB", (1, 1))
        ImageEnhance.Sharpness(im).enhance(0.5)


    def _half_transparent_image(self):
        # returns an image, half transparent, half solid
        im = hopper('RGB')
        
        transparent = Image.new('L', im.size, 0)
        solid = Image.new('L', (im.size[0]//2, im.size[1]), 255)
        transparent.paste(solid, (0,0))
        im.putalpha(transparent)

        return im

    def _check_alpha(self,im, original, op, amount):
        self.assertEqual(im.getbands(), original.getbands())
        self.assert_image_equal(im.split()[-1], original.split()[-1],
                                "Diff on %s: %s" % (op, amount))
    
    def test_alpha(self):
        # Issue https://github.com/python-pillow/Pillow/issues/899
        # Is alpha preserved through image enhancement?

        original = self._half_transparent_image()

        for op in ['Color', 'Brightness', 'Contrast', 'Sharpness']:
            for amount in [0,0.5,1.0]:
                self._check_alpha(getattr(ImageEnhance,op)(original).enhance(amount),
                                  original, op, amount)
                

if __name__ == '__main__':
    unittest.main()

# End of file
