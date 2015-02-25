from helper import unittest, PillowTestCase, fromstring, tostring

from PIL import Image

CODECS = dir(Image.core)
FILENAME = "Tests/images/hopper.webp"
DATA = tostring(Image.open(FILENAME).resize((512, 512)), "WEBP")
ALPHA_FILENAME = "Tests/images/transparent.webp"
ALPHA_DATA = tostring(Image.open(ALPHA_FILENAME).resize((512, 512)), "WEBP")


def draft(mode, size):
    im = fromstring(DATA)
    im.draft(mode, size)
    return im

def alpha_draft(mode, size):
    im = fromstring(ALPHA_DATA)
    im.draft(mode, size)
    return im



class TestImageDraft(PillowTestCase):

    def setUp(self):
        if "webp_decoder" not in CODECS:
            self.skipTest("WebP support not available")

    def test_size(self):
        # Upscaling/downscaling to any size is supported.
        self.assertEqual(draft("RGB", (1024, 1024)).size, (1024, 1024))
        self.assertEqual(draft("RGB", (512, 512)).size, (512, 512))
        self.assertEqual(draft("RGB", (256, 256)).size, (256, 256))
        self.assertEqual(draft("RGB", (128, 128)).size, (128, 128))
        self.assertEqual(draft("RGB", (64, 64)).size, (64, 64))
        self.assertEqual(draft("RGB", (32, 32)).size, (32, 32))

    def test_mode(self):
        # Decoder only support RGB/RGBA output.
        self.assertEqual(draft("1", (512, 512)).mode, "RGB")
        self.assertEqual(draft("L", (512, 512)).mode, "RGB")
        self.assertEqual(draft("RGB", (512, 512)).mode, "RGB")
        self.assertEqual(draft("RGBA", (512, 512)).mode, "RGBA")
        self.assertEqual(draft("YCbCr", (512, 512)).mode, "RGB")
        self.assertEqual(alpha_draft("1", (512, 512)).mode, "RGBA")
        self.assertEqual(alpha_draft("L", (512, 512)).mode, "RGBA")
        self.assertEqual(alpha_draft("RGB", (512, 512)).mode, "RGB")
        self.assertEqual(alpha_draft("RGBA", (512, 512)).mode, "RGBA")
        self.assertEqual(alpha_draft("YCbCr", (512, 512)).mode, "RGBA")


if __name__ == '__main__':
    unittest.main()

# End of file
