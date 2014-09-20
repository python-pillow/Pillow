from helper import unittest, PillowTestCase, hopper


class TestImageResize(PillowTestCase):

    def test_resize(self):
        def resize(mode, size):
            out = hopper(mode).resize(size)
            self.assertEqual(out.mode, mode)
            self.assertEqual(out.size, size)
        for mode in "1", "P", "L", "RGB", "I", "F":
            resize(mode, (100, 100))
            resize(mode, (200, 200))


if __name__ == '__main__':
    unittest.main()

# End of file
