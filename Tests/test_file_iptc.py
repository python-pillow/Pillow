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
        self.assertEqual(iptc[(2, 90)], b"Budapest")
        self.assertEqual(iptc[(2, 101)], b"Hungary")

    def test_i(self):
        # Arrange
        c = b"a"

        # Act
        ret = IptcImagePlugin.i(c)

        # Assert
        self.assertEqual(ret, 97)


if __name__ == '__main__':
    unittest.main()

# End of file
