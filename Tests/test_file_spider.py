from helper import unittest, PillowTestCase, hopper

from PIL import Image
from PIL import SpiderImagePlugin

TEST_FILE = "Tests/images/hopper.spider"


class TestImageSpider(PillowTestCase):

    def test_sanity(self):
        im = Image.open(TEST_FILE)
        im.load()
        self.assertEqual(im.mode, "F")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "SPIDER")

    def test_save(self):
        # Arrange
        temp = self.tempfile('temp.spider')
        im = hopper()

        # Act
        im.save(temp, "SPIDER")

        # Assert
        im2 = Image.open(temp)
        self.assertEqual(im2.mode, "F")
        self.assertEqual(im2.size, (128, 128))
        self.assertEqual(im2.format, "SPIDER")

    def test_isSpiderImage(self):
        self.assertTrue(SpiderImagePlugin.isSpiderImage(TEST_FILE))

    def test_tell(self):
        # Arrange
        im = Image.open(TEST_FILE)

        # Act
        index = im.tell()

        # Assert
        self.assertEqual(index, 0)

    def test_loadImageSeries(self):
        # Arrange
        not_spider_file = "Tests/images/hopper.ppm"
        file_list = [TEST_FILE, not_spider_file, "path/not_found.ext"]

        # Act
        img_list = SpiderImagePlugin.loadImageSeries(file_list)

        # Assert
        self.assertEqual(len(img_list), 1)
        self.assertIsInstance(img_list[0], Image.Image)
        self.assertEqual(img_list[0].size, (128, 128))

    def test_loadImageSeries_no_input(self):
        # Arrange
        file_list = None

        # Act
        img_list = SpiderImagePlugin.loadImageSeries(file_list)

        # Assert
        self.assertEqual(img_list, None)

    def test_isInt_not_a_number(self):
        # Arrange
        not_a_number = "a"

        # Act
        ret = SpiderImagePlugin.isInt(not_a_number)

        # Assert
        self.assertEqual(ret, 0)


if __name__ == '__main__':
    unittest.main()

# End of file
