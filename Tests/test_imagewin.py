from helper import unittest, PillowTestCase, tearDownModule

from PIL import ImageWin


class TestImageWin(PillowTestCase):

    def test_sanity(self):
        dir(ImageWin)
        pass

    def test_hdc(self):
        # Arrange
        dc = 50

        # Act
        hdc = ImageWin.HDC(dc)
        dc2 = int(hdc)

        # Assert
        self.assertEqual(dc2, 50)

    def test_hwnd(self):
        # Arrange
        wnd = 50

        # Act
        hwnd = ImageWin.HWND(wnd)
        wnd2 = int(hwnd)

        # Assert
        self.assertEqual(wnd2, 50)


if __name__ == '__main__':
    unittest.main()

# End of file
