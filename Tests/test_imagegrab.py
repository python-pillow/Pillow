import subprocess
import sys

import pytest

from .helper import assert_image

from PIL import ImageGrab


class TestImageGrab:
    def test_grab(self):
        if sys.platform in ["darwin", "win32"] or ImageGrab._has_imagemagick():
            for im in [
                ImageGrab.grab(),
                ImageGrab.grab(include_layered_windows=True),
                ImageGrab.grab(all_screens=True),
            ]:
                assert_image(im, im.mode, im.size)

            im = ImageGrab.grab(bbox=(10, 20, 50, 80))
            assert_image(im, im.mode, (40, 60))
        else:
            pytest.raises(IOError, ImageGrab.grab)

    def test_grabclipboard(self):
        if sys.platform == "darwin":
            subprocess.call(["screencapture", "-cx"])
        elif sys.platform == "win32":
            p = subprocess.Popen(["powershell", "-command", "-"], stdin=subprocess.PIPE)
            p.stdin.write(
                b"""[Reflection.Assembly]::LoadWithPartialName("System.Drawing")
[Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
$bmp = New-Object Drawing.Bitmap 200, 200
[Windows.Forms.Clipboard]::SetImage($bmp)"""
            )
            p.communicate()
        else:
            self.assertRaises(NotImplementedError, ImageGrab.grabclipboard)
            return

        im = ImageGrab.grabclipboard()
        assert_image(im, im.mode, im.size)
