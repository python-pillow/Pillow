from helper import unittest, PillowTestCase, hopper

try:
    from PIL import ImageQt
    from PyQt5.QtGui import QImage, qRgb, qRgba
except:
    try:
        from PyQt4.QtGui import QImage, qRgb, qRgba
    except:
        try:
            from PySide.QtGui import QImage, qRgb, qRgba
        except:
            # Will be skipped in setUp
            pass


class TestImageQt(PillowTestCase):

    def setUp(self):
        try:
            from PyQt5.QtGui import QImage, qRgb, qRgba
        except:
            try:
                from PyQt4.QtGui import QImage, qRgb, qRgba
            except:
                try:
                    from PySide.QtGui import QImage, qRgb, qRgba
                except:
                    self.skipTest('PyQt4 or 5 or PySide not installed')

    def test_rgb(self):
        # from https://qt-project.org/doc/qt-4.8/qcolor.html
        # typedef QRgb
        # An ARGB quadruplet on the format #AARRGGBB,
        # equivalent to an unsigned int.

        self.assertEqual(qRgb(0, 0, 0), qRgba(0, 0, 0, 255))

        def checkrgb(r, g, b):
            val = ImageQt.rgb(r, g, b)
            val = val % 2**24  # drop the alpha
            self.assertEqual(val >> 16, r)
            self.assertEqual(((val >> 8) % 2**8), g)
            self.assertEqual(val % 2**8, b)

        checkrgb(0, 0, 0)
        checkrgb(255, 0, 0)
        checkrgb(0, 255, 0)
        checkrgb(0, 0, 255)

    def test_image(self):
        for mode in ('1', 'RGB', 'RGBA', 'L', 'P'):
            ImageQt.ImageQt(hopper(mode))


if __name__ == '__main__':
    unittest.main()

# End of file
