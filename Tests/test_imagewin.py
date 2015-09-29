from helper import unittest, PillowTestCase, hopper

from PIL import ImageWin
import sys


class TestImageWin(PillowTestCase):

    def test_sanity(self):
        dir(ImageWin)

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


@unittest.skipUnless(sys.platform.startswith('win32'), "Windows only")
class TestImageWinDib(PillowTestCase):

    def test_dib_image(self):
        # Arrange
        im = hopper()

        # Act
        dib = ImageWin.Dib(im)

        # Assert
        self.assertEqual(dib.size, im.size)

    def test_dib_mode_string(self):
        # Arrange
        mode = "RGBA"
        size = (128, 128)

        # Act
        dib = ImageWin.Dib(mode, size)

        # Assert
        self.assertEqual(dib.size, (128, 128))

    def test_dib_paste(self):
        # Arrange
        im = hopper()

        mode = "RGBA"
        size = (128, 128)
        dib = ImageWin.Dib(mode, size)

        # Act
        dib.paste(im)

        # Assert
        self.assertEqual(dib.size, (128, 128))

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
        self.assertEqual(dib.size, (128, 128))

    def test_dib_frombytes_tobytes_roundtrip(self):
        # Arrange
        # Make two different DIB images
        im = hopper()
        dib1 = ImageWin.Dib(im)

        mode = "RGB"
        size = (128, 128)
        dib2 = ImageWin.Dib(mode, size)

        # Confirm they're different
        self.assertNotEqual(dib1.tobytes(), dib2.tobytes())

        # Act
        # Make one the same as the using tobytes()/frombytes()
        test_buffer = dib1.tobytes()
        dib2.frombytes(test_buffer)

        # Assert
        # Confirm they're the same
        self.assertEqual(dib1.tobytes(), dib2.tobytes())

    def test_removed_methods(self):
        # Arrange
        im = hopper()
        dib = ImageWin.Dib(im)

        # Act/Assert
        self.assertRaises(Exception, dib.tostring)
        self.assertRaises(Exception, lambda: dib.fromstring(test_buffer))


if __name__ == '__main__':
    unittest.main()

# End of file
