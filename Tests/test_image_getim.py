from helper import unittest, PillowTestCase, hopper, py3


class TestImageGetIm(PillowTestCase):

    def test_sanity(self):
        im = hopper()
        type_repr = repr(type(im.getim()))

        if py3:
            self.assertIn("PyCapsule", type_repr)


        try:
            #py2.6
            target_types = (int, long)
        except:
            target_types = (int)

        self.assertIsInstance(im.im.id, target_types)


if __name__ == '__main__':
    unittest.main()

# End of file
