from helper import unittest, PillowTestCase, hopper

from PIL import Image, SunImagePlugin

import os

EXTRA_DIR = 'Tests/images/sunraster'

class TestFileSun(PillowTestCase):

    def test_sanity(self):
        # Arrange
        # Created with ImageMagick: convert hopper.jpg hopper.ras
        test_file = "Tests/images/hopper.ras"

        # Act
        im = Image.open(test_file)

        # Assert
        self.assertEqual(im.size, (128, 128))

        self.assert_image_similar(im, hopper(), 5) # visually verified
        
        invalid_file = "Tests/images/flower.jpg"
        self.assertRaises(SyntaxError,
                          lambda: SunImagePlugin.SunImageFile(invalid_file))

    def test_im1(self):
        im = Image.open('Tests/images/sunraster.im1')
        target = Image.open('Tests/images/sunraster.im1.png')
        self.assert_image_equal(im, target)


    @unittest.skipIf(not os.path.exists(EXTRA_DIR),
                     "Extra image files not installed")
    def test_others(self):
        files = (os.path.join(EXTRA_DIR, f) for f in
                   os.listdir(EXTRA_DIR) if os.path.splitext(f)[1]
                   in ('.sun', '.SUN', '.ras'))
        for path in files:
            with Image.open(path) as im:
                im.load()  
                self.assertIsInstance(im, SunImagePlugin.SunImageFile)
                target_path = "%s.png" % os.path.splitext(path)[0]
                #im.save(target_file)
                with Image.open(target_path) as target:
                    self.assert_image_equal(im, target)
        
if __name__ == '__main__':
    unittest.main()
