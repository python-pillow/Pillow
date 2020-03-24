import subprocess
import sys

import pytest
from PIL import ImageGrab

from .helper import assert_image


class TestImageGrab:
    def test_grab(self):
        native_support = sys.platform in ["darwin", "win32"]
        if native_support or ImageGrab._has_imagemagick():
            for args in [
                {},
                {"include_layered_windows": True},
                {"all_screens": True},
                {"bbox": (10, 20, 50, 80)},
            ]:
                try:
                    im = ImageGrab.grab(**args)
                except IOError as e:
                    if not native_support and str(e) == "Unable to open X server":
                        continue
                    else:
                        raise
                assert_image(im, im.mode, (40, 60) if "bbox" in args else im.size)
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
            pytest.raises(NotImplementedError, ImageGrab.grabclipboard)
            return

        im = ImageGrab.grabclipboard()
        assert_image(im, im.mode, im.size)
