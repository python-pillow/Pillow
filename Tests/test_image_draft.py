from helper import unittest, PillowTestCase, fromstring, tostring

from PIL import Image

CODECS = dir(Image.core)
FILENAME = "Tests/images/hopper.jpg"
DATA = tostring(Image.open(FILENAME).resize((512, 512)), "JPEG")


def draft(mode, size):
    im = fromstring(DATA)
    im.draft(mode, size)
    return im


class TestImageDraft(PillowTestCase):

    def setUp(self):
        if "jpeg_encoder" not in CODECS or "jpeg_decoder" not in CODECS:
            self.skipTest("jpeg support not available")

    def test_size(self):
        self.assertEqual(draft("RGB", (512, 512)).size, (512, 512))
        self.assertEqual(draft("RGB", (256, 256)).size, (256, 256))
        self.assertEqual(draft("RGB", (128, 128)).size, (128, 128))
        self.assertEqual(draft("RGB", (64, 64)).size, (64, 64))
        self.assertEqual(draft("RGB", (32, 32)).size, (64, 64))

    def test_mode(self):
        self.assertEqual(draft("1", (512, 512)).mode, "RGB")
        self.assertEqual(draft("L", (512, 512)).mode, "L")
        self.assertEqual(draft("RGB", (512, 512)).mode, "RGB")
        self.assertEqual(draft("YCbCr", (512, 512)).mode, "YCbCr")


if __name__ == '__main__':
    unittest.main()

# End of file
