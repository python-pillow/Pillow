from helper import unittest, PillowTestCase, hopper, imagemagick_available

import os.path


class TestFilePalm(PillowTestCase):
    _roundtrip = imagemagick_available()

    def helper_save_as_palm(self, mode):
        # Arrange
        im = hopper(mode)
        outfile = self.tempfile("temp_" + mode + ".palm")

        # Act
        im.save(outfile)

        # Assert
        self.assertTrue(os.path.isfile(outfile))
        self.assertGreater(os.path.getsize(outfile), 0)

    def roundtrip(self, mode):
        if not self._roundtrip:
            return

        im = hopper(mode)
        outfile = self.tempfile("temp.palm")

        im.save(outfile)
        converted = self.open_withImagemagick(outfile)
        self.assert_image_equal(converted, im)

    def test_monochrome(self):
        # Arrange
        mode = "1"

        # Act / Assert
        self.helper_save_as_palm(mode)
        self.roundtrip(mode)

    def test_p_mode(self):
        # Arrange
        mode = "P"

        # Act / Assert
        self.helper_save_as_palm(mode)
        self.skipKnownBadTest("Palm P image is wrong")
        self.roundtrip(mode)

    def test_rgb_ioerror(self):
        # Arrange
        mode = "RGB"

        # Act / Assert
        self.assertRaises(IOError, lambda: self.helper_save_as_palm(mode))


if __name__ == '__main__':
    unittest.main()

# End of file
