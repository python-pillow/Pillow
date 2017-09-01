from helper import unittest, PillowTestCase

from PIL import Image, McIdasImagePlugin


class TestFileMcIdas(PillowTestCase):

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          McIdasImagePlugin.McIdasImageFile, invalid_file)

    def test_valid_file(self):
        # Arrange
        # https://ghrc.nsstc.nasa.gov/hydro/details/cmx3g8
        # https://ghrc.nsstc.nasa.gov/pub/fieldCampaigns/camex3/cmx3g8/browse/
        test_file = "Tests/images/cmx3g8_wv_1998.260_0745_mcidas.ara"
        saved_file = "Tests/images/cmx3g8_wv_1998.260_0745_mcidas.png"

        # Act
        im = Image.open(test_file)
        im.load()

        # Assert
        self.assertEqual(im.format, "MCIDAS")
        self.assertEqual(im.mode, "I")
        self.assertEqual(im.size, (1800, 400))
        im2 = Image.open(saved_file)
        self.assert_image_equal(im, im2)


if __name__ == '__main__':
    unittest.main()
