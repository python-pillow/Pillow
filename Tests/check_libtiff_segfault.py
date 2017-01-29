from helper import unittest, PillowTestCase
from PIL import Image

TEST_FILE = "Tests/images/libtiff_segfault.tif"


class TestLibtiffSegfault(PillowTestCase):
    def test_segfault(self):
        """ This test should not segfault. It will on Pillow <= 3.1.0 and
            libtiff >= 4.0.0
            """

        with self.assertRaises(IOError):
            im = Image.open(TEST_FILE)
            im.load()


if __name__ == '__main__':
    unittest.main()
