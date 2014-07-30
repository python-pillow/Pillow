from helper import unittest, PillowTestCase, lena

from PIL import Image, IptcImagePlugin

TEST_FILE = "Tests/images/iptc.jpg"


class TestFileIptc(PillowTestCase):

    # Helpers

    def dummy_IptcImagePlugin(self):
        # Create an IptcImagePlugin object without initializing it
        class FakeImage:
            pass
        im = FakeImage()
        im.__class__ = IptcImagePlugin.IptcImageFile
        return im

    # Tests

    def test_getiptcinfo_jpg_none(self):
        # Arrange
        im = lena()

        # Act
        iptc = IptcImagePlugin.getiptcinfo(im)

        # Assert
        self.assertIsNone(iptc)

    def test_getiptcinfo_jpg_found(self):
        # Arrange
        im = Image.open(TEST_FILE)

        # Act
        iptc = IptcImagePlugin.getiptcinfo(im)

        # Assert
        self.assertIsInstance(iptc, dict)
        self.assertEqual(iptc[(2, 90)], "Budapest")
        self.assertEqual(iptc[(2, 101)], "Hungary")

    # _FIXME: is_raw() is disabled. Should we remove it?
    def test__is_raw_equal_zero(self):
        # Arrange
        im = self.dummy_IptcImagePlugin()
        offset = 0
        size = 4

        # Act
        ret = im._is_raw(offset, size)

        # Assert
        self.assertEqual(ret, 0)

    def test_i(self):
        # Arrange
        c = "a"

        # Act
        ret = IptcImagePlugin.i(c)

        # Assert
        self.assertEqual(ret, 97)


if __name__ == '__main__':
    unittest.main()

# End of file
