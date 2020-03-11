import subprocess
import sys

import pytest
from PIL import Image, ImageGrab

from .helper import assert_image


class TestImageGrab:
    @pytest.mark.skipif(
        sys.platform not in ("win32", "darwin"), reason="requires Windows or macOS"
    )
    def test_grab(self):
        for im in [
            ImageGrab.grab(),
            ImageGrab.grab(include_layered_windows=True),
            ImageGrab.grab(all_screens=True),
        ]:
            assert_image(im, im.mode, im.size)

        im = ImageGrab.grab(bbox=(10, 20, 50, 80))
        assert_image(im, im.mode, (40, 60))

    @pytest.mark.skipif(not Image.core.HAVE_XCB, reason="requires XCB")
    def test_grab_x11(self):
        try:
            if sys.platform not in ("win32", "darwin"):
                im = ImageGrab.grab()
                assert_image(im, im.mode, im.size)

            im2 = ImageGrab.grab(xdisplay="")
            assert_image(im2, im2.mode, im2.size)
        except IOError as e:
            pytest.skip(str(e))

    @pytest.mark.skipif(Image.core.HAVE_XCB, reason="tests missing XCB")
    def test_grab_no_xcb(self):
        if sys.platform not in ("win32", "darwin"):
            with pytest.raises(IOError) as e:
                ImageGrab.grab()
            assert str(e.value).startswith("Pillow was built without XCB support")

        with pytest.raises(IOError) as e:
            ImageGrab.grab(xdisplay="")
        assert str(e.value).startswith("Pillow was built without XCB support")

    @pytest.mark.skipif(not Image.core.HAVE_XCB, reason="requires XCB")
    def test_grab_invalid_xdisplay(self):
        with pytest.raises(IOError) as e:
            ImageGrab.grab(xdisplay="error.test:0.0")
        assert str(e.value).startswith("X connection failed")

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
            with pytest.raises(NotImplementedError) as e:
                ImageGrab.grabclipboard()
            assert str(e.value) == "ImageGrab.grabclipboard() is macOS and Windows only"
            return

        im = ImageGrab.grabclipboard()
        assert_image(im, im.mode, im.size)
