from helper import unittest, PillowTestCase, on_appveyor

import sys

try:
    from PIL import ImageGrab

    class TestImageGrab(PillowTestCase):

        @unittest.skipIf(on_appveyor(), "Test fails on appveyor")
        def test_grab(self):
            im = ImageGrab.grab()
            self.assert_image(im, im.mode, im.size)

        @unittest.skipIf(on_appveyor(), "Test fails on appveyor")
        def test_grab2(self):
            im = ImageGrab.grab()
            self.assert_image(im, im.mode, im.size)

except ImportError:
    class TestImageGrab(PillowTestCase):
        def test_skip(self):
            self.skipTest("ImportError")


class TestImageGrabImport(PillowTestCase):

    def test_import(self):
        # Arrange
        exception = None

        # Act
        try:
            from PIL import ImageGrab
            ImageGrab.__name__  # dummy to prevent Pyflakes warning
        except Exception as e:
            exception = e

        # Assert
        if sys.platform in ["win32", "darwin"]:
            self.assertIsNone(exception, None)
        else:
            self.assertIsInstance(exception, ImportError)
            self.assertEqual(str(exception),
                             "ImageGrab is OS X and Windows only")


if __name__ == '__main__':
    unittest.main()

# End of file
