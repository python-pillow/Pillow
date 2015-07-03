from helper import unittest, PillowTestCase

from PIL import Image


class TestFileTga(PillowTestCase):

    def test_id_field(self):
        # tga file with id field
        test_file = "Tests/images/tga_id_field.tga"

        # Act
        im = Image.open(test_file)

        # Assert
        self.assertEqual(im.size, (100, 100))

    def test_save(self):
        test_file = "Tests/images/tga_id_field.tga"
        im = Image.open(test_file)

        test_file = self.tempfile("temp.tga")

        # Save
        im.save(test_file)
        test_im = Image.open(test_file)
        self.assertEqual(test_im.size, (100, 100))

        # RGBA save
        im.convert("RGBA").save(test_file)
        test_im = Image.open(test_file)
        self.assertEqual(test_im.size, (100, 100))

        # Unsupported mode save
        self.assertRaises(IOError, lambda: im.convert("LA").save(test_file))


if __name__ == '__main__':
    unittest.main()
