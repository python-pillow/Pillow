from helper import unittest, PillowTestCase, tearDownModule, lena

import os.path


class TestFilePalm(PillowTestCase):

    def test_save_palm_p(self):
        # Arrange
        im = lena("P")
        outfile = self.tempfile('temp_p.palm')

        # Act
        im.save(outfile)

        # Assert
        self.assertTrue(os.path.isfile(outfile))
        self.assertGreater(os.path.getsize(outfile), 0)


if __name__ == '__main__':
    unittest.main()

# End of file
