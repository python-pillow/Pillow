from helper import unittest, PillowTestCase, hopper
from test_imageqt import PillowQtTestCase

from PIL import ImageQt


if ImageQt.qt_is_installed:
    from PIL.ImageQt import QImage


class TestToQImage(PillowQtTestCase, PillowTestCase):

    def test_sanity(self):
        for mode in ('1', 'RGB', 'RGBA', 'L', 'P'):
            data = ImageQt.toqimage(hopper(mode))
            data.save('/tmp/hopper_{}_qimage.png'.format(mode))
            self.assertTrue(isinstance(data, QImage))
            self.assertFalse(data.isNull())


if __name__ == '__main__':
    unittest.main()

# End of file
