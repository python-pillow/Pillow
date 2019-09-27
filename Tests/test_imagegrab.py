import subprocess
import sys

from .helper import PillowTestCase

try:
    from PIL import ImageGrab

    class TestImageGrab(PillowTestCase):
        def test_grab(self):
            for im in [
                ImageGrab.grab(),
                ImageGrab.grab(include_layered_windows=True),
                ImageGrab.grab(all_screens=True),
            ]:
                self.assert_image(im, im.mode, im.size)

        def test_grabclipboard(self):
            if sys.platform == "darwin":
                subprocess.call(["screencapture", "-cx"])
            else:
                p = subprocess.Popen(
                    ["powershell", "-command", "-"], stdin=subprocess.PIPE
                )
                p.stdin.write(
                    b"""[Reflection.Assembly]::LoadWithPartialName("System.Drawing")
[Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
$bmp = New-Object Drawing.Bitmap 200, 200
[Windows.Forms.Clipboard]::SetImage($bmp)"""
                )
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
            self.assertEqual(str(exception), "ImageGrab is macOS and Windows only")
