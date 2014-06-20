from helper import unittest, PillowTestCase, tearDownModule

from PIL import Image
from io import BytesIO

codecs = dir(Image.core)

test_card = Image.open('Tests/images/test-card.png')
test_card.load()

# OpenJPEG 2.0.0 outputs this debugging message sometimes; we should
# ignore it---it doesn't represent a test failure.
# 'Not enough memory to handle tile data'


class TestFileJpeg2k(PillowTestCase):

    def setUp(self):
        if "jpeg2k_encoder" not in codecs or "jpeg2k_decoder" not in codecs:
            self.skipTest('JPEG 2000 support not available')

    def roundtrip(self, im, **options):
        out = BytesIO()
        im.save(out, "JPEG2000", **options)
        bytes = out.tell()
        out.seek(0)
        im = Image.open(out)
        im.bytes = bytes  # for testing only
        im.load()
        return im

    def test_sanity(self):
        # Internal version number
        self.assertRegexpMatches(Image.core.jp2klib_version, '\d+\.\d+\.\d+$')

        im = Image.open('Tests/images/test-card-lossless.jp2')
        im.load()
        self.assertEqual(im.mode, 'RGB')
        self.assertEqual(im.size, (640, 480))
        self.assertEqual(im.format, 'JPEG2000')

    # These two test pre-written JPEG 2000 files that were not written with
    # PIL (they were made using Adobe Photoshop)

    def test_lossless(self):
        im = Image.open('Tests/images/test-card-lossless.jp2')
        im.load()
        im.save('/tmp/test-card.png')
        self.assert_image_similar(im, test_card, 1.0e-3)

    def test_lossy_tiled(self):
        im = Image.open('Tests/images/test-card-lossy-tiled.jp2')
        im.load()
        self.assert_image_similar(im, test_card, 2.0)

    def test_lossless_rt(self):
        im = self.roundtrip(test_card)
        self.assert_image_equal(im, test_card)

    def test_lossy_rt(self):
        im = self.roundtrip(test_card, quality_layers=[20])
        self.assert_image_similar(im, test_card, 2.0)

    def test_tiled_rt(self):
        im = self.roundtrip(test_card, tile_size=(128, 128))
        self.assert_image_equal(im, test_card)

    def test_tiled_offset_rt(self):
        im = self.roundtrip(
            test_card, tile_size=(128, 128),
            tile_offset=(0, 0), offset=(32, 32))
        self.assert_image_equal(im, test_card)

    def test_irreversible_rt(self):
        im = self.roundtrip(test_card, irreversible=True, quality_layers=[20])
        self.assert_image_similar(im, test_card, 2.0)

    def test_prog_qual_rt(self):
        im = self.roundtrip(
            test_card, quality_layers=[60, 40, 20], progression='LRCP')
        self.assert_image_similar(im, test_card, 2.0)

    def test_prog_res_rt(self):
        im = self.roundtrip(test_card, num_resolutions=8, progression='RLCP')
        self.assert_image_equal(im, test_card)

    def test_reduce(self):
        im = Image.open('Tests/images/test-card-lossless.jp2')
        im.reduce = 2
        im.load()
        self.assertEqual(im.size, (160, 120))

    def test_layers(self):
        out = BytesIO()
        test_card.save(out, 'JPEG2000', quality_layers=[100, 50, 10],
                       progression='LRCP')
        out.seek(0)

        im = Image.open(out)
        im.layers = 1
        im.load()
        self.assert_image_similar(im, test_card, 13)

        out.seek(0)
        im = Image.open(out)
        im.layers = 3
        im.load()
        self.assert_image_similar(im, test_card, 0.4)


if __name__ == '__main__':
    unittest.main()

# End of file
