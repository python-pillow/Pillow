from PIL import Image

from .helper import PillowTestCase, unittest

TEST_FILE = "Tests/images/fli_overflow.fli"


class TestFliOverflow(PillowTestCase):
    def test_fli_overflow(self):

        # this should not crash with a malloc error or access violation
        im = Image.open(TEST_FILE)
        im.load()


if __name__ == "__main__":
    unittest.main()
