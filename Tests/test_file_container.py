from helper import unittest, PillowTestCase, hopper

from PIL import Image
from PIL import ContainerIO


class TestFileContainer(PillowTestCase):

    def test_sanity(self):
        dir(Image)
        dir(ContainerIO)

    def test_isatty(self):
        im = hopper()
        container = ContainerIO.ContainerIO(im, 0, 0)

        self.assertEqual(container.isatty(), 0)


if __name__ == '__main__':
    unittest.main()
