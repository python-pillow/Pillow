import unittest

from PIL import Image

from .helper import PillowTestCase

TEST_FILE = "Tests/images/fli_overflow.fli"


class TestFliOverflow(PillowTestCase):
    def test_fli_overflow(self):

        # this should not crash with a malloc error or access violation
        with Image.open(TEST_FILE) as im:
            im.load()


if __name__ == "__main__":
    unittest.main()
