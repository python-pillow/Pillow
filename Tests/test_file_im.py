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

    def test_n_frames(self):
        im = Image.open(TEST_IM)
        self.assertEqual(im.n_frames, 1)
        self.assertFalse(im.is_animated)

    def test_eoferror(self):
        im = Image.open(TEST_IM)

        n_frames = im.n_frames
        while True:
            n_frames -= 1
            try:
                im.seek(n_frames)
                break
            except EOFError:
                self.assertTrue(im.tell() < n_frames)

    def test_roundtrip(self):
        out = self.tempfile('temp.im')
        im = hopper()
        im.save(out)
        reread = Image.open(out)

        self.assert_image_equal(reread, im)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda: ImImagePlugin.ImImageFile(invalid_file))


if __name__ == '__main__':
    unittest.main()

# End of file
