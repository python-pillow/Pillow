from helper import unittest, PillowTestCase

from PIL import Image, TarIO

codecs = dir(Image.core)

# Sample tar archive
TEST_TAR_FILE = "Tests/images/hopper.tar"


class TestFileTar(PillowTestCase):

    def setUp(self):
        if "zip_decoder" not in codecs and "jpeg_decoder" not in codecs:
            self.skipTest("neither jpeg nor zip support available")

    def test_sanity(self):
        for codec, test_path, format in [
            ['zip_decoder', 'hopper.png', 'PNG'],
            ['jpeg_decoder', 'hopper.jpg', 'JPEG']
        ]:
            if codec in codecs:
                tar = TarIO.TarIO(TEST_TAR_FILE, test_path)
                im = Image.open(tar)
                im.load()
                self.assertEqual(im.mode, "RGB")
                self.assertEqual(im.size, (128, 128))
                self.assertEqual(im.format, format)

    def test_close(self):
        tar = TarIO.TarIO(TEST_TAR_FILE, 'hopper.jpg')
        tar.close()

    def test_contextmanager(self):
        with TarIO.TarIO(TEST_TAR_FILE, 'hopper.jpg'):
            pass


if __name__ == '__main__':
    unittest.main()
