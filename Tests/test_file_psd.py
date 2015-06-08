from helper import unittest, PillowTestCase

from PIL import Image

# sample ppm stream
test_file = "Tests/images/hopper.psd"
data = open(test_file, "rb").read()


class TestImagePsd(PillowTestCase):

    def test_sanity(self):
        im = Image.open(test_file)
        im.load()
        self.assertEqual(im.mode, "RGB")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "PSD")

    def test_n_frames(self):
        im = Image.open("Tests/images/hopper_merged.psd")
        self.assertEqual(im.n_frames, 1)

        im = Image.open(test_file)
        self.assertEqual(im.n_frames, 2)


if __name__ == '__main__':
    unittest.main()

# End of file
