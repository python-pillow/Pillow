from __future__ import annotations

import pytest

from PIL import ImageWin

from .helper import hopper, is_win32


class TestImageWin:
    def test_sanity(self) -> None:
        dir(ImageWin)

    def test_hdc(self) -> None:
        # Arrange
        dc = 50

        # Act
        hdc = ImageWin.HDC(dc)
        dc2 = int(hdc)

        # Assert
        assert dc2 == 50

    def test_hwnd(self) -> None:
        # Arrange
        wnd = 50

        # Act
        hwnd = ImageWin.HWND(wnd)
        wnd2 = int(hwnd)

        # Assert
        assert wnd2 == 50


@pytest.mark.skipif(not is_win32(), reason="Windows only")
class TestImageWinDib:
    def test_dib_image(self) -> None:
        # Arrange
        im = hopper()

        # Act
        dib = ImageWin.Dib(im)

        # Assert
        assert dib.size == im.size

    def test_dib_mode_string(self) -> None:
        # Arrange
        mode = "RGBA"
        size = (128, 128)

        # Act
        dib = ImageWin.Dib(mode, size)

        # Assert
        assert dib.size == (128, 128)

        with pytest.raises(ValueError):
            ImageWin.Dib(mode)

    def test_dib_hwnd(self) -> None:
        mode = "RGBA"
        size = (128, 128)
        wnd = 0

        dib = ImageWin.Dib(mode, size)
        hwnd = ImageWin.HWND(wnd)

        dib.expose(hwnd)
        dib.draw(hwnd, (0, 0) + size)
        assert isinstance(dib.query_palette(hwnd), int)

    def test_dib_paste(self) -> None:
        # Arrange
        im = hopper()

        mode = "RGBA"
        size = (128, 128)
        dib = ImageWin.Dib(mode, size)

        # Act
        dib.paste(im)

        # Assert
        assert dib.size == (128, 128)

    def test_dib_paste_bbox(self) -> None:
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

    def test_dib_frombytes_tobytes_roundtrip(self) -> None:
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
        test_buffer: bytes | memoryview = dib1.tobytes()
        for datatype in ("bytes", "memoryview"):
            if datatype == "memoryview":
                test_buffer = memoryview(test_buffer)
            dib2.frombytes(test_buffer)

            # Assert
            # Confirm they're the same
            assert dib1.tobytes() == dib2.tobytes()
