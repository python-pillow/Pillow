from helper import unittest, PillowTestCase

from PIL import Image, TarIO

codecs = dir(Image.core)

# Sample tar archive
TEST_TAR_FILE = "Tests/images/hopper.tar"


class TestFileTar(PillowTestCase):

    def setUp(self):
        if "zip_decoder" not in codecs and "jpeg_decoder" not in codecs:
            self.skipTest("neither jpeg nor zip support not available")

    def test_sanity(self):
        if "zip_decoder" in codecs:
            tar = TarIO.TarIO(TEST_TAR_FILE, 'hopper.png')
            im = Image.open(tar)
            im.load()
            self.assertEqual(im.mode, "RGB")
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.format, "PNG")

        if "jpeg_decoder" in codecs:
            tar = TarIO.TarIO(TEST_TAR_FILE, 'hopper.jpg')
            im = Image.open(tar)
            im.load()
            self.assertEqual(im.mode, "RGB")
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.format, "JPEG")


if __name__ == '__main__':
    unittest.main()
