from helper import unittest, PillowTestCase, hopper

from PIL import Image, MicImagePlugin

TEST_FILE = "Tests/images/hopper.mic"


class TestFileMic(PillowTestCase):

    def test_sanity(self):
        im = Image.open(TEST_FILE)
        im.load()
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "MIC")

        im2 = hopper("RGBA")
        self.assert_image_similar(im, im2, 123.5)

    def test_n_frames(self):
        im = Image.open(TEST_FILE)

        self.assertEqual(im.n_frames, 1)

    def test_is_animated(self):
        im = Image.open(TEST_FILE)

        self.assertFalse(im.is_animated)

    def test_tell(self):
        im = Image.open(TEST_FILE)

        self.assertEqual(im.tell(), 0)

    def test_seek(self):
        im = Image.open(TEST_FILE)

        im.seek(0)
        self.assertEqual(im.tell(), 0)

        self.assertRaises(EOFError, lambda: im.seek(99))
        self.assertEqual(im.tell(), 0)

    def test_invalid_file(self):
        # Test an invalid OLE file
        invalid_file = "Tests/images/flower.jpg"
        self.assertRaises(SyntaxError,
                          lambda: MicImagePlugin.MicImageFile(invalid_file))

        # Test a valid OLE file, but not a MIC file
        ole_file = "Tests/images/test-ole-file.doc"
        self.assertRaises(SyntaxError,
                          lambda: MicImagePlugin.MicImageFile(ole_file))


if __name__ == '__main__':
    unittest.main()
