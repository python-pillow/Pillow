from helper import unittest, PillowTestCase

from PIL import Image, Jpeg2KImagePlugin
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
        test_bytes = out.tell()
        out.seek(0)
        im = Image.open(out)
        im.bytes = test_bytes  # for testing only
        im.load()
        return im

    def test_sanity(self):
        # Internal version number
        self.assertRegexpMatches(Image.core.jp2klib_version, r'\d+\.\d+\.\d+$')

        im = Image.open('Tests/images/test-card-lossless.jp2')
        px = im.load()
        self.assertEqual(px[0, 0], (0, 0, 0))
        self.assertEqual(im.mode, 'RGB')
        self.assertEqual(im.size, (640, 480))
        self.assertEqual(im.format, 'JPEG2000')

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda:
                          Jpeg2KImagePlugin.Jpeg2KImageFile(invalid_file))

    def test_bytesio(self):
        with open('Tests/images/test-card-lossless.jp2', 'rb') as f:
            data = BytesIO(f.read())
        im = Image.open(data)
        im.load()
        self.assert_image_similar(im, test_card, 1.0e-3)

    # These two test pre-written JPEG 2000 files that were not written with
    # PIL (they were made using Adobe Photoshop)

    def test_lossless(self):
        im = Image.open('Tests/images/test-card-lossless.jp2')
        im.load()
        outfile = self.tempfile('temp_test-card.png')
        im.save(outfile)
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

    def test_rgba(self):
        # Arrange
        j2k = Image.open('Tests/images/rgb_trns_ycbc.j2k')
        jp2 = Image.open('Tests/images/rgb_trns_ycbc.jp2')

        # Act
        j2k.load()
        jp2.load()

        # Assert
        self.assertEqual(j2k.mode, 'RGBA')
        self.assertEqual(jp2.mode, 'RGBA')

    def test_16bit_monochrome_has_correct_mode(self):

        j2k = Image.open('Tests/images/16bit.cropped.j2k')
        jp2 = Image.open('Tests/images/16bit.cropped.jp2')

        j2k.load()
        jp2.load()

        self.assertEqual(j2k.mode, 'I;16')
        self.assertEqual(jp2.mode, 'I;16')

    def test_16bit_monchrome_jp2_like_tiff(self):

        tiff_16bit = Image.open('Tests/images/16bit.cropped.tif')
        jp2 = Image.open('Tests/images/16bit.cropped.jp2')
        self.assert_image_similar(jp2, tiff_16bit, 1e-3)

    def test_16bit_monchrome_j2k_like_tiff(self):

        tiff_16bit = Image.open('Tests/images/16bit.cropped.tif')
        j2k = Image.open('Tests/images/16bit.cropped.j2k')
        self.assert_image_similar(j2k, tiff_16bit, 1e-3)

    def test_16bit_j2k_roundtrips(self):

        j2k = Image.open('Tests/images/16bit.cropped.j2k')
        im = self.roundtrip(j2k)
        self.assert_image_equal(im, j2k)

    def test_16bit_jp2_roundtrips(self):

        jp2 = Image.open('Tests/images/16bit.cropped.jp2')
        im = self.roundtrip(jp2)
        self.assert_image_equal(im, jp2)

    def test_unbound_local(self):
        # prepatch, a malformed jp2 file could cause an UnboundLocalError
        # exception.
        with self.assertRaises(IOError):
            Image.open('Tests/images/unbound_variable.jp2')

if __name__ == '__main__':
    unittest.main()
