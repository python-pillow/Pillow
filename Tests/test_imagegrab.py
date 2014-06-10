from helper import unittest, PillowTestCase, tearDownModule

try:
    from PIL import ImageGrab

    class TestImageCopy(PillowTestCase):

        def test_grab(self):
            im = ImageGrab.grab()
            self.assert_image(im, im.mode, im.size)

        def test_grab2(self):
            im = ImageGrab.grab()
            self.assert_image(im, im.mode, im.size)

except ImportError:
    class TestImageCopy(PillowTestCase):
        def test_skip(self):
            self.skipTest("ImportError")


if __name__ == '__main__':
    unittest.main()

# End of file
