from helper import unittest, PillowTestCase, tearDownModule, lena

import os.path


class TestFilePalm(PillowTestCase):

    def helper_save_as_palm(self, mode):
        # Arrange
        im = lena(mode)
        outfile = self.tempfile("temp_" + mode + ".palm")

        # Act
        im.save(outfile)

        # Assert
        self.assertTrue(os.path.isfile(outfile))
        self.assertGreater(os.path.getsize(outfile), 0)

    def test_monochrome(self):
        # Arrange
        mode = "1"

        # Act / Assert
        self.helper_save_as_palm(mode)

    def test_p_mode(self):
        # Arrange
        mode = "P"

        # Act / Assert
        self.helper_save_as_palm(mode)

    def test_rgb_ioerror(self):
        # Arrange
        mode = "RGB"

        # Act / Assert
        self.assertRaises(IOError, lambda: self.helper_save_as_palm(mode))


if __name__ == '__main__':
    unittest.main()

# End of file
