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

    def test_id_field_rle(self):
        # tga file with id field
        test_file = "Tests/images/rgb32rle.tga"

        # Act
        im = Image.open(test_file)

        # Assert
        self.assertEqual(im.size, (199, 199))

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

    def test_save_rle(self):
        test_file = "Tests/images/rgb32rle.tga"
        im = Image.open(test_file)

        test_file = self.tempfile("temp.tga")

        # Save
        im.save(test_file)
        test_im = Image.open(test_file)
        self.assertEqual(test_im.size, (199, 199))

        # RGBA save
        im.convert("RGBA").save(test_file)
        test_im = Image.open(test_file)
        self.assertEqual(test_im.size, (199, 199))

    def test_save_l_transparency(self):
        # There are 559 transparent pixels in la.tga.
        num_transparent = 559

        in_file = "Tests/images/la.tga"
        im = Image.open(in_file)
        self.assertEqual(im.mode, "LA")
        self.assertEqual(
            im.getchannel("A").getcolors()[0][0], num_transparent)

        test_file = self.tempfile("temp.tga")
        im.save(test_file)

        test_im = Image.open(test_file)
        self.assertEqual(test_im.mode, "LA")
        self.assertEqual(
            test_im.getchannel("A").getcolors()[0][0], num_transparent)

        self.assert_image_equal(im, test_im)


if __name__ == '__main__':
    unittest.main()
