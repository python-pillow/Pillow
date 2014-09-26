from helper import unittest, PillowTestCase, hopper


class TestImageCopy(PillowTestCase):

    def test_copy(self):
        def copy(mode):
            im = hopper(mode)
            out = im.copy()
            self.assertEqual(out.mode, mode)
            self.assertEqual(out.size, im.size)
        for mode in "1", "P", "L", "RGB", "I", "F":
            copy(mode)

if __name__ == '__main__':
    unittest.main()

# End of file
