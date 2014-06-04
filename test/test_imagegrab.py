from helper import unittest, PillowTestCase

try:
    from PIL import ImageGrab

    class TestImageCopy(PillowTestCase):

        def test_grab(self):
            im = ImageGrab.grab()
            self.assert_image(im, im.mode, im.size)

        def test_grab2(self):
            im = ImageGrab.grab()
            self.assert_image(im, im.mode, im.size)

except ImportError as v:
    class TestImageCopy(PillowTestCase):
        def test_skip(self):
            self.skipTest(v)


if __name__ == '__main__':
    unittest.main()

# End of file
