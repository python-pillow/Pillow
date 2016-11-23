from helper import unittest, PillowTestCase
from PIL import Image


class TestFileWmf(PillowTestCase):

    def test_load_raw(self):

        # Test basic EMF load
        im = Image.open('Tests/images/drawing.emf')
        im.load()  # should not segfault.

        # Test basic WMF load
        im = Image.open('Tests/images/drawing.wmf')
        im.load()  # should not segfault.


if __name__ == '__main__':
    unittest.main()
