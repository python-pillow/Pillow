from helper import unittest, PillowTestCase, hopper

from PIL import Image

# sample im
TEST_IM = "Tests/images/hopper.im"


class TestFileIm(PillowTestCase):

    def test_sanity(self):
        im = Image.open(TEST_IM)
        im.load()
        self.assertEqual(im.mode, "RGB")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "IM")

    def test_n_frames(self):
        im = Image.open(TEST_IM)
        self.assertEqual(im.n_frames, 1)

    def test_roundtrip(self):
        out = self.tempfile('temp.im')
        im = hopper()
        im.save(out)
        reread = Image.open(out)

        self.assert_image_equal(reread, im)

if __name__ == '__main__':
    unittest.main()

# End of file
