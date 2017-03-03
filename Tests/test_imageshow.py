from helper import unittest, PillowTestCase

from PIL import Image
from PIL import ImageShow


class TestImageShow(PillowTestCase):

    def test_sanity(self):
        dir(Image)
        dir(ImageShow)

    def test_viewer(self):
        viewer = ImageShow.Viewer()

        self.assertIsNone(viewer.get_format(None))

        self.assertRaises(NotImplementedError, lambda: viewer.get_command(None))


if __name__ == '__main__':
    unittest.main()
