from helper import unittest, PillowTestCase, hopper, py3
import sys

class TestImageGetIm(PillowTestCase):

    def test_sanity(self):
        im = hopper()
        type_repr = repr(type(im.getim()))

        if py3:
            self.assertIn("PyCapsule", type_repr)


        if sys.hexversion < 0x2070000:
            # py2.6 x64, windows
            target_types = (int, long)
        else:
            target_types = (int)

        self.assertIsInstance(im.im.id, target_types)


if __name__ == '__main__':
    unittest.main()

# End of file
