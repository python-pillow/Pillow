from helper import unittest, PillowTestCase

import sys
import subprocess

try:
    from PIL import ImageGrab

    class TestImageGrab(PillowTestCase):

        def test_grab(self):
            im = ImageGrab.grab()
            self.assert_image(im, im.mode, im.size)

        def test_grabclipboard(self):
            if sys.platform == "darwin":
                subprocess.call(['screencapture', '-cx'])
            else:
                p = subprocess.Popen(['powershell', '-command', '-'],
                                     stdin=subprocess.PIPE)
                p.stdin.write(b'''[Reflection.Assembly]::LoadWithPartialName("System.Drawing")
[Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
$bmp = New-Object Drawing.Bitmap 200, 200
[Windows.Forms.Clipboard]::SetImage($bmp)''')
                p.communicate()

            im = ImageGrab.grabclipboard()
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
            self.assertIsNone(exception)
        else:
            self.assertIsInstance(exception, ImportError)
            self.assertEqual(str(exception),
                             "ImageGrab is macOS and Windows only")


if __name__ == '__main__':
    unittest.main()
