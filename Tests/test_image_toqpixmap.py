from helper import unittest, PillowTestCase, hopper
from test_imageqt import PillowQtTestCase, PillowQPixmapTestCase

from PIL import ImageQt

if ImageQt.qt_is_installed:
    from PIL.ImageQt import QPixmap


class TestToQPixmap(PillowQPixmapTestCase, PillowTestCase):

    def test_sanity(self):
        PillowQtTestCase.setUp(self)

        for mode in ('1', 'RGB', 'RGBA', 'L', 'P'):
            data = ImageQt.toqpixmap(hopper(mode))

            self.assertIsInstance(data, QPixmap)
            self.assertFalse(data.isNull())

            # Test saving the file
            tempfile = self.tempfile('temp_{0}.png'.format(mode))
            data.save(tempfile)


if __name__ == '__main__':
    unittest.main()

# End of file
