import tempfile
import unittest
from io import BytesIO

from PIL import Image, ImageSequence, SpiderImagePlugin

from .helper import PillowTestCase, hopper, is_pypy

TEST_FILE = "Tests/images/hopper.spider"


class TestImageSpider(PillowTestCase):
    def test_sanity(self):
        with Image.open(TEST_FILE) as im:
            im.load()
            self.assertEqual(im.mode, "F")
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.format, "SPIDER")

    @unittest.skipIf(is_pypy(), "Requires CPython")
    def test_unclosed_file(self):
        def open():
            im = Image.open(TEST_FILE)
            im.load()

        self.assert_warning(ResourceWarning, open)

    def test_closed_file(self):
        def open():
            im = Image.open(TEST_FILE)
            im.load()
            im.close()

        self.assert_warning(None, open)

    def test_context_manager(self):
        def open():
            with Image.open(TEST_FILE) as im:
                im.load()

        self.assert_warning(None, open)

    def test_save(self):
        # Arrange
        temp = self.tempfile("temp.spider")
        im = hopper()

        # Act
        im.save(temp, "SPIDER")

        # Assert
        with Image.open(temp) as im2:
            self.assertEqual(im2.mode, "F")
            self.assertEqual(im2.size, (128, 128))
            self.assertEqual(im2.format, "SPIDER")

    def test_tempfile(self):
        # Arrange
        im = hopper()

        # Act
        with tempfile.TemporaryFile() as fp:
            im.save(fp, "SPIDER")

            # Assert
            fp.seek(0)
            with Image.open(fp) as reloaded:
                self.assertEqual(reloaded.mode, "F")
                self.assertEqual(reloaded.size, (128, 128))
                self.assertEqual(reloaded.format, "SPIDER")

    def test_isSpiderImage(self):
        self.assertTrue(SpiderImagePlugin.isSpiderImage(TEST_FILE))

    def test_tell(self):
        # Arrange
        with Image.open(TEST_FILE) as im:

            # Act
            index = im.tell()

            # Assert
            self.assertEqual(index, 0)

    def test_n_frames(self):
        with Image.open(TEST_FILE) as im:
            self.assertEqual(im.n_frames, 1)
            self.assertFalse(im.is_animated)

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
        self.assertIsNone(img_list)

    def test_isInt_not_a_number(self):
        # Arrange
        not_a_number = "a"

        # Act
        ret = SpiderImagePlugin.isInt(not_a_number)

        # Assert
        self.assertEqual(ret, 0)

    def test_invalid_file(self):
        invalid_file = "Tests/images/invalid.spider"

        self.assertRaises(IOError, Image.open, invalid_file)

    def test_nonstack_file(self):
        with Image.open(TEST_FILE) as im:
            self.assertRaises(EOFError, im.seek, 0)

    def test_nonstack_dos(self):
        with Image.open(TEST_FILE) as im:
            for i, frame in enumerate(ImageSequence.Iterator(im)):
                if i > 1:
                    self.fail("Non-stack DOS file test failed")

    # for issue #4093
    def test_odd_size(self):
        data = BytesIO()
        width = 100
        im = Image.new("F", (width, 64))
        im.save(data, format="SPIDER")

        data.seek(0)
        with Image.open(data) as im2:
            self.assert_image_equal(im, im2)
