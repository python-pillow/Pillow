from helper import unittest, PillowTestCase, hopper
from PIL import Image
import os.path


class TestFilePdf(PillowTestCase):

    def helper_save_as_pdf(self, mode, save_all=False):
        # Arrange
        im = hopper(mode)
        outfile = self.tempfile("temp_" + mode + ".pdf")

        # Act
        if save_all:
            im.save(outfile, save_all=True)
        else:
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

    def test_unsupported_mode(self):
        im = hopper("LA")
        outfile = self.tempfile("temp_LA.pdf")

        self.assertRaises(ValueError, lambda: im.save(outfile))

    def test_save_all(self):
        # Single frame image
        self.helper_save_as_pdf("RGB", save_all=True)

        # Multiframe image
        im = Image.open("Tests/images/dispose_bgnd.gif")

        outfile = self.tempfile('temp.pdf')
        im.save(outfile, save_all=True)

        self.assertTrue(os.path.isfile(outfile))
        self.assertGreater(os.path.getsize(outfile), 0)


if __name__ == '__main__':
    unittest.main()

# End of file
