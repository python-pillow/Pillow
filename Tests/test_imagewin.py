from helper import unittest, PillowTestCase

from PIL import Image
from PIL import ImageWin


class TestImageWin(PillowTestCase):

    def test_sanity(self):
        dir(Image)
        dir(ImageWin)
        pass


if __name__ == '__main__':
    unittest.main()

# End of file
