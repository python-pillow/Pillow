from helper import unittest, PillowTestCase, hopper


class TestImageRotate(PillowTestCase):

    def test_rotate(self):
        def rotate(mode):
            im = hopper(mode)
            out = im.rotate(45)
            self.assertEqual(out.mode, mode)
            self.assertEqual(out.size, im.size)  # default rotate clips output
            out = im.rotate(45, expand=1)
            self.assertEqual(out.mode, mode)
            self.assertNotEqual(out.size, im.size)
        for mode in "1", "P", "L", "RGB", "I", "F":
            rotate(mode)


if __name__ == '__main__':
    unittest.main()

# End of file
