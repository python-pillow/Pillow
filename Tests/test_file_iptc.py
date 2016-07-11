from helper import unittest, PillowTestCase, hopper

from PIL import Image, IptcImagePlugin

TEST_FILE = "Tests/images/iptc.jpg"


class TestFileIptc(PillowTestCase):

    def test_getiptcinfo_jpg_none(self):
        # Arrange
        im = hopper()

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

    def test_dump(self):
        # Arrange
        c = b"abc"
        # Temporarily redirect stdout
        try:
            from cStringIO import StringIO
        except ImportError:
            from io import StringIO
        import sys
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        # Act
        IptcImagePlugin.dump(c)

        # Reset stdout
        sys.stdout = old_stdout

        # Assert
        self.assertEqual(mystdout.getvalue(), "61 62 63 \n")


if __name__ == '__main__':
    unittest.main()
