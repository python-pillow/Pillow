import os
import shutil
import subprocess
import sys

import pytest

from PIL import Image, ImageGrab

from .helper import assert_image_equal_tofile, skip_unless_feature


class TestImageGrab:
    @pytest.mark.skipif(
        sys.platform not in ("win32", "darwin"), reason="requires Windows or macOS"
    )
    def test_grab(self):
        ImageGrab.grab()
        ImageGrab.grab(include_layered_windows=True)
        ImageGrab.grab(all_screens=True)

        im = ImageGrab.grab(bbox=(10, 20, 50, 80))
        assert im.size == (40, 60)

    @skip_unless_feature("xcb")
    def test_grab_x11(self):
        try:
            if sys.platform not in ("win32", "darwin"):
                ImageGrab.grab()

            ImageGrab.grab(xdisplay="")
        except OSError as e:
            pytest.skip(str(e))

    @pytest.mark.skipif(Image.core.HAVE_XCB, reason="tests missing XCB")
    def test_grab_no_xcb(self):
        if sys.platform not in ("win32", "darwin") and not shutil.which(
            "gnome-screenshot"
        ):
            with pytest.raises(OSError) as e:
                ImageGrab.grab()
            assert str(e.value).startswith("Pillow was built without XCB support")

        with pytest.raises(OSError) as e:
            ImageGrab.grab(xdisplay="")
        assert str(e.value).startswith("Pillow was built without XCB support")

    @skip_unless_feature("xcb")
    def test_grab_invalid_xdisplay(self):
        with pytest.raises(OSError) as e:
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
            if not shutil.which("wl-paste") and not shutil.which("xclip"):
                with pytest.raises(
                    NotImplementedError,
                    match="wl-paste or xclip is required for"
                    r" ImageGrab.grabclipboard\(\) on Linux",
                ):
                    ImageGrab.grabclipboard()
            return

        ImageGrab.grabclipboard()

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows only")
    def test_grabclipboard_file(self):
        p = subprocess.Popen(["powershell", "-command", "-"], stdin=subprocess.PIPE)
        p.stdin.write(rb'Set-Clipboard -Path "Tests\images\hopper.gif"')
        p.communicate()

        im = ImageGrab.grabclipboard()
        assert len(im) == 1
        assert os.path.samefile(im[0], "Tests/images/hopper.gif")

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows only")
    def test_grabclipboard_png(self):
        p = subprocess.Popen(["powershell", "-command", "-"], stdin=subprocess.PIPE)
        p.stdin.write(
            rb"""$bytes = [System.IO.File]::ReadAllBytes("Tests\images\hopper.png")
$ms = new-object System.IO.MemoryStream(, $bytes)
[Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
[Windows.Forms.Clipboard]::SetData("PNG", $ms)"""
        )
        p.communicate()

        im = ImageGrab.grabclipboard()
        assert_image_equal_tofile(im, "Tests/images/hopper.png")

    @pytest.mark.skipif(
        (
            sys.platform != "linux"
            or not all(shutil.which(cmd) for cmd in ("wl-paste", "wl-copy"))
        ),
        reason="Linux with wl-clipboard only",
    )
    @pytest.mark.parametrize("ext", ("gif", "png", "ico"))
    def test_grabclipboard_wl_clipboard(self, ext):
        image_path = "Tests/images/hopper." + ext
        with open(image_path, "rb") as fp:
            subprocess.call(["wl-copy"], stdin=fp)
        im = ImageGrab.grabclipboard()
        assert_image_equal_tofile(im, image_path)
