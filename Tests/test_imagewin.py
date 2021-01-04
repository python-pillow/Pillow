import pytest

from PIL import ImageWin

from .helper import hopper, is_win32


class TestImageWin:
    def test_sanity(self):
        dir(ImageWin)

    def test_hdc(self):
        # Arrange
        dc = 50

        # Act
        hdc = ImageWin.HDC(dc)
        dc2 = int(hdc)

        # Assert
        assert dc2 == 50

    def test_hwnd(self):
        # Arrange
        wnd = 50

        # Act
        hwnd = ImageWin.HWND(wnd)
        wnd2 = int(hwnd)

        # Assert
        assert wnd2 == 50


@pytest.mark.skipif(not is_win32(), reason="Windows only")
class TestImageWinDib:
    def test_dib_image(self):
        # Arrange
        im = hopper()

        # Act
        dib = ImageWin.Dib(im)

        # Assert
        assert dib.size == im.size

    def test_dib_mode_string(self):
        # Arrange
        mode = "RGBA"
        size = (128, 128)

        # Act
        dib = ImageWin.Dib(mode, size)

        # Assert
        assert dib.size == (128, 128)

    def test_dib_paste(self):
        # Arrange
        im = hopper()

        mode = "RGBA"
        size = (128, 128)
        dib = ImageWin.Dib(mode, size)

        # Act
        dib.paste(im)

        # Assert
        assert dib.size == (128, 128)

    def test_dib_paste_bbox(self):
        # Arrange
        im = hopper()
        bbox = (0, 0, 10, 10)

        mode = "RGBA"
        size = (128, 128)
        dib = ImageWin.Dib(mode, size)

        # Act
        dib.paste(im, bbox)

        # Assert
        assert dib.size == (128, 128)

    def test_dib_frombytes_tobytes_roundtrip(self):
        # Arrange
        # Make two different DIB images
        im = hopper()
        dib1 = ImageWin.Dib(im)

        mode = "RGB"
        size = (128, 128)
        dib2 = ImageWin.Dib(mode, size)

        # Confirm they're different
        assert dib1.tobytes() != dib2.tobytes()

        # Act
        # Make one the same as the using tobytes()/frombytes()
        test_buffer = dib1.tobytes()
        dib2.frombytes(test_buffer)

        # Assert
        # Confirm they're the same
        assert dib1.tobytes() == dib2.tobytes()
