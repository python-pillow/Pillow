from helper import unittest, PillowTestCase, tearDownModule, lena

from PIL import Image
from PIL import SpiderImagePlugin

test_file = "Tests/images/lena.spider"


class TestImageSpider(PillowTestCase):

    def test_sanity(self):
        im = Image.open(test_file)
        im.load()
        self.assertEqual(im.mode, "F")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "SPIDER")

    def test_save(self):
        # Arrange
        temp = self.tempfile('temp.spider')
        im = lena()

        # Act
        im.save(temp, "SPIDER")

        # Assert
        im2 = Image.open(temp)
        self.assertEqual(im2.mode, "F")
        self.assertEqual(im2.size, (128, 128))
        self.assertEqual(im2.format, "SPIDER")

    def test_isSpiderImage(self):
        self.assertTrue(SpiderImagePlugin.isSpiderImage(test_file))


if __name__ == '__main__':
    unittest.main()

# End of file
