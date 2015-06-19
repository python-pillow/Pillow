from helper import unittest, PillowTestCase, hopper
from test_imageqt import PillowQtTestCase, PillowQPixmapTestCase

from PIL import ImageQt

if ImageQt.qt_is_installed:
    from PIL.ImageQt import QPixmap


class TestToQPixmap(PillowQPixmapTestCase, PillowTestCase):

    def test_sanity(self):
        PillowQtTestCase.setUp(self)
        QPixmap('Tests/images/hopper.ppm').save(
            '/tmp/hopper_RGB_qpixmap_file.png')
        for mode in ('1', 'RGB', 'RGBA', 'L', 'P'):
            data = ImageQt.toqpixmap(hopper(mode))
            data.save('/tmp/hopper_{}_qpixmap.png'.format(mode))
            self.assertTrue(isinstance(data, QPixmap))
            self.assertFalse(data.isNull())


if __name__ == '__main__':
    unittest.main()

# End of file
