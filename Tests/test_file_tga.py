from helper import unittest, PillowTestCase

from PIL import Image


class TestFileSun(PillowTestCase):

    def test_sanity(self):
        # tga file with id field
        test_file = "Tests/images/tga_id_field.tga"

        # Act
        im = Image.open(test_file)

        # Assert
        self.assertEqual(im.size, (100, 100))


if __name__ == '__main__':
    unittest.main()

# End of file
