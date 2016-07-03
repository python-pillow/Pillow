from helper import unittest, PillowTestCase

import PIL
import PIL.Image


class TestSanity(PillowTestCase):

    def test_sanity(self):

        # Make sure we have the binary extension
        im = PIL.Image.core.new("L", (100, 100))

        self.assertEqual(PIL.Image.VERSION[:3], '1.1')

        # Create an image and do stuff with it.
        im = PIL.Image.new("1", (100, 100))
        self.assertEqual((im.mode, im.size), ('1', (100, 100)))
        self.assertEqual(len(im.tobytes()), 1300)

        # Create images in all remaining major modes.
        im = PIL.Image.new("L", (100, 100))
        im = PIL.Image.new("P", (100, 100))
        im = PIL.Image.new("RGB", (100, 100))
        im = PIL.Image.new("I", (100, 100))
        im = PIL.Image.new("F", (100, 100))


if __name__ == '__main__':
    unittest.main()
