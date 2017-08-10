from helper import unittest, PillowTestCase, fromstring, tostring

from PIL import Image


class TestImageDraft(PillowTestCase):
    def setUp(self):
        codecs = dir(Image.core)
        if "jpeg_encoder" not in codecs or "jpeg_decoder" not in codecs:
            self.skipTest("jpeg support not available")

    def draft_roundtrip(self, in_mode, in_size, req_mode, req_size):
        im = Image.new(in_mode, in_size)
        data = tostring(im, 'JPEG')
        im = fromstring(data)
        im.draft(req_mode, req_size)
        return im

    def test_size(self):
        for in_size, req_size, out_size in [
            ((435, 361), (2048, 2048), (435, 361)),  # bigger
            ((435, 361), (435, 361), (435, 361)),  # same
            ((128, 128), (64, 64), (64, 64)),
            ((128, 128), (32, 32), (32, 32)),
            ((128, 128), (16, 16), (16, 16)),

            # large requested width
            ((435, 361), (218, 128), (435, 361)),  # almost 2x
            ((435, 361), (217, 128), (218, 181)),  # more than 2x
            ((435, 361), (109, 64), (218, 181)),  # almost 4x
            ((435, 361), (108, 64), (109, 91)),  # more than 4x
            ((435, 361), (55, 32), (109, 91)),  # almost 8x
            ((435, 361), (54, 32), (55, 46)),  # more than 8x
            ((435, 361), (27, 16), (55, 46)),  # more than 16x

            # and vice versa
            ((435, 361), (128, 181), (435, 361)),  # almost 2x
            ((435, 361), (128, 180), (218, 181)),  # more than 2x
            ((435, 361), (64, 91), (218, 181)),  # almost 4x
            ((435, 361), (64, 90), (109, 91)),  # more than 4x
            ((435, 361), (32, 46), (109, 91)),  # almost 8x
            ((435, 361), (32, 45), (55, 46)),  # more than 8x
            ((435, 361), (16, 22), (55, 46)),  # more than 16x
        ]:
            im = self.draft_roundtrip('L', in_size, None, req_size)
            im.load()
            self.assertEqual(im.size, out_size)

    def test_mode(self):
        for in_mode, req_mode, out_mode in [
            ("RGB", "1", "RGB"),
            ("RGB", "L", "L"),
            ("RGB", "RGB", "RGB"),
            ("RGB", "YCbCr", "YCbCr"),
            ("L", "1", "L"),
            ("L", "L", "L"),
            ("L", "RGB", "L"),
            ("L", "YCbCr", "L"),
            ("CMYK", "1", "CMYK"),
            ("CMYK", "L", "CMYK"),
            ("CMYK", "RGB", "CMYK"),
            ("CMYK", "YCbCr", "CMYK"),
        ]:
            im = self.draft_roundtrip(in_mode, (64, 64), req_mode, None)
            im.load()
            self.assertEqual(im.mode, out_mode)

    def test_several_drafts(self):
        im = self.draft_roundtrip('L', (128, 128), None, (64, 64))
        im.draft(None, (64, 64))
        im.load()

if __name__ == '__main__':
    unittest.main()
