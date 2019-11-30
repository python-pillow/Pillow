import unittest

from PIL import Image

from .helper import PillowTestCase

TEST_FILE = "Tests/images/libtiff_segfault.tif"


class TestLibtiffSegfault(PillowTestCase):
    def test_segfault(self):
        """ This test should not segfault. It will on Pillow <= 3.1.0 and
            libtiff >= 4.0.0
            """

        with self.assertRaises(IOError):
            with Image.open(TEST_FILE) as im:
                im.load()


if __name__ == "__main__":
    unittest.main()
