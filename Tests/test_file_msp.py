from helper import unittest, PillowTestCase, hopper

from PIL import Image, MspImagePlugin

TEST_FILE = "Tests/images/hopper.msp"


class TestFileMsp(PillowTestCase):

    def test_sanity(self):
        file = self.tempfile("temp.msp")

        hopper("1").save(file)

        im = Image.open(file)
        im.load()
        self.assertEqual(im.mode, "1")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "MSP")

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda: MspImagePlugin.MspImageFile(invalid_file))

    def test_open(self):
        # Arrange
        # Act
        im = Image.open(TEST_FILE)

        # Assert
        self.assertEqual(im.size, (128, 128))
        self.assert_image_similar(im, hopper("1"), 4)

    def test_cannot_save_wrong_mode(self):
        # Arrange
        im = hopper()
        filename = self.tempfile("temp.msp")

        # Act/Assert
        self.assertRaises(IOError, lambda: im.save(filename))


if __name__ == '__main__':
    unittest.main()

# End of file
