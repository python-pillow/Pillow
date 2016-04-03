from helper import unittest, PillowTestCase

from PIL import Image, FliImagePlugin

# sample ppm stream
# created as an export of a palette image from Gimp2.6
# save as...-> hopper.fli, default options.
test_file = "Tests/images/hopper.fli"
data = open(test_file, "rb").read()


class TestFileFli(PillowTestCase):

    def test_sanity(self):
        im = Image.open(test_file)
        im.load()
        self.assertEqual(im.mode, "P")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "FLI")

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda: FliImagePlugin.FliImageFile(invalid_file))

    def test_n_frames(self):
        im = Image.open(test_file)
        self.assertEqual(im.n_frames, 1)
        self.assertFalse(im.is_animated)

    def test_eoferror(self):
        im = Image.open(test_file)

        n_frames = im.n_frames
        while True:
            n_frames -= 1
            try:
                im.seek(n_frames)
                break
            except EOFError:
                self.assertTrue(im.tell() < n_frames)


if __name__ == '__main__':
    unittest.main()

# End of file
