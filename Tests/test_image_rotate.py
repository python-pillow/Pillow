from helper import unittest, PillowTestCase, hopper
from PIL import Image


class TestImageRotate(PillowTestCase):

    def rotate(self, im, mode, angle, center=None, translate=None):
        out = im.rotate(angle, center=center, translate=translate)
        self.assertEqual(out.mode, mode)
        self.assertEqual(out.size, im.size)  # default rotate clips output
        out = im.rotate(angle, center=center, translate=translate, expand=1)
        self.assertEqual(out.mode, mode)
        if angle % 180 == 0:
            self.assertEqual(out.size, im.size)
        elif im.size == (0, 0):
            self.assertEqual(out.size, im.size)
        else:
            self.assertNotEqual(out.size, im.size)

    def test_mode(self):                
        for mode in ("1", "P", "L", "RGB", "I", "F"):
            im = hopper(mode)
            self.rotate(im, mode, 45)

    def test_angle(self):
        for angle in (0, 90, 180, 270):
            im = Image.open('Tests/images/test-card.png')
            self.rotate(im, im.mode, angle)

    def test_zero(self):
        for angle in (0, 45, 90, 180, 270):
            im = Image.new('RGB',(0,0))
            self.rotate(im, im.mode, angle)

    def test_resample(self):
        # Target image creation, inspected by eye. 
        # >>> im = Image.open('Tests/images/hopper.ppm')
        # >>> im = im.rotate(45, resample=Image.BICUBIC, expand=True)         
        # >>> im.save('Tests/images/hopper_45.png')

        target = Image.open('Tests/images/hopper_45.png')
        for (resample, epsilon) in ((Image.NEAREST, 10),
                                    (Image.BILINEAR, 5),
                                    (Image.BICUBIC, 0)):
            im = hopper()
            im = im.rotate(45, resample=resample, expand=True)
            self.assert_image_similar(im, target, epsilon)

    def test_center_0(self):
        im = hopper()
        target = Image.open('Tests/images/hopper_45.png')
        target_origin = target.size[1]/2
        target = target.crop((0, target_origin, 128, target_origin + 128))

        im = im.rotate(45, center=(0,0), resample=Image.BICUBIC)

        self.assert_image_similar(im, target, 15)

    def test_center_14(self):
        im = hopper()
        target = Image.open('Tests/images/hopper_45.png')
        target_origin = target.size[1] / 2 - 14
        target = target.crop((6, target_origin, 128 + 6, target_origin + 128))

        im = im.rotate(45, center=(14,14), resample=Image.BICUBIC)

        self.assert_image_similar(im, target, 10)

    def test_translate(self):
        im = hopper()
        target = Image.open('Tests/images/hopper_45.png')
        target_origin = (target.size[1] / 2 - 64) - 5
        target = target.crop((target_origin, target_origin,
                              target_origin + 128,  target_origin + 128))

        im = im.rotate(45, translate=(5,5), resample=Image.BICUBIC)

        self.assert_image_similar(im, target, 1)

    def test_fastpath_center(self):
        # if the center is -1,-1 and we rotate by 90<=x<=270 the
        # resulting image should be black
        for angle in (90, 180, 270):
            im = hopper().rotate(angle, center=(-1,-1))
            self.assert_image_equal(im, Image.new('RGB', im.size, 'black'))

    def test_fastpath_translate(self):
        # if we post-translate by -128
        # resulting image should be black
        for angle in (0, 90, 180, 270):
            im = hopper().rotate(angle, translate=(-128,-128))
            self.assert_image_equal(im, Image.new('RGB', im.size, 'black'))

    def test_center(self):
        im = hopper()
        self.rotate(im, im.mode, 45, center=(0, 0))
        self.rotate(im, im.mode, 45, translate=(im.size[0]/2, 0))
        self.rotate(im, im.mode, 45, center=(0, 0), translate=(im.size[0]/2, 0))

    


if __name__ == '__main__':
    unittest.main()
