import unittest

from PIL import Image, TarIO

from .helper import PillowTestCase, is_pypy

codecs = dir(Image.core)

# Sample tar archive
TEST_TAR_FILE = "Tests/images/hopper.tar"


class TestFileTar(PillowTestCase):
    def setUp(self):
        if "zip_decoder" not in codecs and "jpeg_decoder" not in codecs:
            self.skipTest("neither jpeg nor zip support available")

    def test_sanity(self):
        for codec, test_path, format in [
            ["zip_decoder", "hopper.png", "PNG"],
            ["jpeg_decoder", "hopper.jpg", "JPEG"],
        ]:
            if codec in codecs:
                with TarIO.TarIO(TEST_TAR_FILE, test_path) as tar:
                    with Image.open(tar) as im:
                        im.load()
                        self.assertEqual(im.mode, "RGB")
                        self.assertEqual(im.size, (128, 128))
                        self.assertEqual(im.format, format)

    @unittest.skipIf(is_pypy(), "Requires CPython")
    def test_unclosed_file(self):
        def open():
            TarIO.TarIO(TEST_TAR_FILE, "hopper.jpg")

        self.assert_warning(ResourceWarning, open)

    def test_close(self):
        def open():
            tar = TarIO.TarIO(TEST_TAR_FILE, "hopper.jpg")
            tar.close()

        self.assert_warning(None, open)

    def test_contextmanager(self):
        def open():
            with TarIO.TarIO(TEST_TAR_FILE, "hopper.jpg"):
                pass

        self.assert_warning(None, open)
