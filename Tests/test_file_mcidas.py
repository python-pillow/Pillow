from PIL import Image, McIdasImagePlugin

from .helper import PillowTestCase


class TestFileMcIdas(PillowTestCase):
    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError, McIdasImagePlugin.McIdasImageFile, invalid_file)

    def test_valid_file(self):
        # Arrange
        # https://ghrc.nsstc.nasa.gov/hydro/details/cmx3g8
        # https://ghrc.nsstc.nasa.gov/pub/fieldCampaigns/camex3/cmx3g8/browse/
        test_file = "Tests/images/cmx3g8_wv_1998.260_0745_mcidas.ara"
        saved_file = "Tests/images/cmx3g8_wv_1998.260_0745_mcidas.png"

        # Act
        with Image.open(test_file) as im:
            im.load()

            # Assert
            self.assertEqual(im.format, "MCIDAS")
            self.assertEqual(im.mode, "I")
            self.assertEqual(im.size, (1800, 400))
            with Image.open(saved_file) as im2:
                self.assert_image_equal(im, im2)
