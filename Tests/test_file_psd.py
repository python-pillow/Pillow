from helper import unittest, PillowTestCase

from PIL import Image, PsdImagePlugin

# sample ppm stream
test_file = "Tests/images/hopper.psd"


class TestImagePsd(PillowTestCase):

    def test_sanity(self):
        im = Image.open(test_file)
        im.load()
        self.assertEqual(im.mode, "RGB")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "PSD")

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda: PsdImagePlugin.PsdImageFile(invalid_file))

    def test_n_frames(self):
        im = Image.open("Tests/images/hopper_merged.psd")
        self.assertEqual(im.n_frames, 1)
        self.assertFalse(im.is_animated)

        im = Image.open(test_file)
        self.assertEqual(im.n_frames, 2)
        self.assertTrue(im.is_animated)

    def test_eoferror(self):
        im = Image.open(test_file)

        n_frames = im.n_frames
        while True:
            n_frames -= 1
            try:
                # PSD seek index starts at 1 rather than 0
                im.seek(n_frames+1)
                break
            except EOFError:
                self.assertTrue(im.tell() < n_frames)


if __name__ == '__main__':
    unittest.main()
