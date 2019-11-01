import sys
from io import StringIO

from PIL import Image, IptcImagePlugin

from .helper import PillowTestCase, hopper

TEST_FILE = "Tests/images/iptc.jpg"


class TestFileIptc(PillowTestCase):
    def test_getiptcinfo_jpg_none(self):
        # Arrange
        with hopper() as im:

            # Act
            iptc = IptcImagePlugin.getiptcinfo(im)

        # Assert
        self.assertIsNone(iptc)

    def test_getiptcinfo_jpg_found(self):
        # Arrange
        with Image.open(TEST_FILE) as im:

            # Act
            iptc = IptcImagePlugin.getiptcinfo(im)

        # Assert
        self.assertIsInstance(iptc, dict)
        self.assertEqual(iptc[(2, 90)], b"Budapest")
        self.assertEqual(iptc[(2, 101)], b"Hungary")

    def test_getiptcinfo_tiff_none(self):
        # Arrange
        with Image.open("Tests/images/hopper.tif") as im:

            # Act
            iptc = IptcImagePlugin.getiptcinfo(im)

        # Assert
        self.assertIsNone(iptc)

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
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        # Act
        IptcImagePlugin.dump(c)

        # Reset stdout
        sys.stdout = old_stdout

        # Assert
        self.assertEqual(mystdout.getvalue(), "61 62 63 \n")
