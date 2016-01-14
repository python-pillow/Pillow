from helper import unittest, PillowTestCase
from PIL import Image

TEST_FILE = "Tests/images/libtiff_segfault.tif"

class TestLibtiffSegfault(PillowTestCase):
    def test_segfault(self):
        """ This test should not segfault. It will on Pillow <= 3.1.0 and
            libtiff >= 4.0.0
            """

        try:
            im = Image.open(TEST_FILE)
            im.load()
        except IOError:
            self.assertTrue(True, "Got expected IOError")
        except Exception:
            self.fail("Should have returned IOError")



if __name__ == '__main__':
    unittest.main()
