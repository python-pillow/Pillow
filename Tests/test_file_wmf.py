from helper import unittest, PillowTestCase
from PIL import Image


class TestFileWmf(PillowTestCase):

    def test_load_raw(self):

        # Test basic EMF open
        im = Image.open('Tests/images/drawing.emf')

        # Test basic WMF open
        im = Image.open('Tests/images/drawing.wmf')


if __name__ == '__main__':
    unittest.main()
