from helper import unittest, PillowTestCase, hopper, py3


class TestImageGetIm(PillowTestCase):

    def test_sanity(self):
        im = hopper()
        type_repr = repr(type(im.getim()))

        if py3:
            self.assertIn("PyCapsule", type_repr)

        self.assertIsInstance(im.im.id, int)


if __name__ == '__main__':
    unittest.main()

# End of file
