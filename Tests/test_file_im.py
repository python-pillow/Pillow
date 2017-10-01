from helper import unittest, PillowTestCase, hopper

from PIL import Image, ImImagePlugin

# sample im
TEST_IM = "Tests/images/hopper.im"


class TestFileIm(PillowTestCase):

    def test_sanity(self):
        im = Image.open(TEST_IM)
        im.load()
        self.assertEqual(im.mode, "RGB")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "IM")

    def test_tell(self):
        # Arrange
        im = Image.open(TEST_IM)

        # Act
        frame = im.tell()

        # Assert
        self.assertEqual(frame, 0)

    def test_n_frames(self):
        im = Image.open(TEST_IM)
        self.assertEqual(im.n_frames, 1)
        self.assertFalse(im.is_animated)

    def test_eoferror(self):
        im = Image.open(TEST_IM)
        n_frames = im.n_frames

        # Test seeking past the last frame
        self.assertRaises(EOFError, im.seek, n_frames)
        self.assertLess(im.tell(), n_frames)

        # Test that seeking to the last frame does not raise an error
        im.seek(n_frames-1)

    def test_roundtrip(self):
        for mode in ["RGB", "P"]:
            out = self.tempfile('temp.im')
            im = hopper(mode)
            im.save(out)
            reread = Image.open(out)

            self.assert_image_equal(reread, im)

    def test_save_unsupported_mode(self):
        out = self.tempfile('temp.im')
        im = hopper("HSV")
        self.assertRaises(ValueError, im.save, out)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          ImImagePlugin.ImImageFile, invalid_file)

    def test_number(self):
        self.assertEqual(1.2, ImImagePlugin.number("1.2"))


if __name__ == '__main__':
    unittest.main()
