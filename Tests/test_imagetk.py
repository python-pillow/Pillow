from helper import unittest, PillowTestCase


class TestImageTk(PillowTestCase):

    def test_import(self):
        try:
            from PIL import ImageTk
            dir(ImageTk)
        except (OSError, ImportError) as v:
            self.skipTest(v)


if __name__ == '__main__':
    unittest.main()

# End of file
