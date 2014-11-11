from helper import unittest, PillowTestCase, hopper

import os.path


class TestFilePdf(PillowTestCase):

    def helper_save_as_pdf(self, mode):
        # Arrange
        im = hopper(mode)
        outfile = self.tempfile("temp_" + mode + ".pdf")

        # Act
        im.save(outfile)

        # Assert
        self.assertTrue(os.path.isfile(outfile))
        self.assertGreater(os.path.getsize(outfile), 0)

    def test_monochrome(self):
        # Arrange
        mode = "1"

        # Act / Assert
        self.helper_save_as_pdf(mode)

    def test_greyscale(self):
        # Arrange
        mode = "L"

        # Act / Assert
        self.helper_save_as_pdf(mode)

    def test_rgb(self):
        # Arrange
        mode = "RGB"

        # Act / Assert
        self.helper_save_as_pdf(mode)

    def test_p_mode(self):
        # Arrange
        mode = "P"

        # Act / Assert
        self.helper_save_as_pdf(mode)

    def test_cmyk_mode(self):
        # Arrange
        mode = "CMYK"

        # Act / Assert
        self.helper_save_as_pdf(mode)


if __name__ == '__main__':
    unittest.main()

# End of file
