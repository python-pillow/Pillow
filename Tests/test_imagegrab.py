import subprocess
import sys

import pytest

from .helper import assert_image

try:
    from PIL import ImageGrab

    class TestImageGrab:
        def test_grab(self):
            for im in [
                ImageGrab.grab(),
                ImageGrab.grab(include_layered_windows=True),
                ImageGrab.grab(all_screens=True),
            ]:
                assert_image(im, im.mode, im.size)

            im = ImageGrab.grab(bbox=(10, 20, 50, 80))
            assert_image(im, im.mode, (40, 60))

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
            assert_image(im, im.mode, im.size)


except ImportError:

    class TestImageGrab:
        @pytest.mark.skip(reason="ImageGrab ImportError")
        def test_skip(self):
            pass


class TestImageGrabImport:
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
            assert exception is None
        else:
            assert isinstance(exception, ImportError)
            assert str(exception) == "ImageGrab is macOS and Windows only"
