from helper import unittest, PillowTestCase

from PIL import Image


class TestFileWebpMetadata(PillowTestCase):

    def setUp(self):
        try:
            from PIL import _webp
        except ImportError:
            self.skipTest('WebP support not installed')
            return

        if not _webp.HAVE_WEBPMUX:
            self.skipTest('WebPMux support not installed')

    def test_read_exif_metadata(self):

        file_path = "Tests/images/flower.webp"
        image = Image.open(file_path)

        self.assertEqual(image.format, "WEBP")
        exif_data = image.info.get("exif", None)
        self.assertTrue(exif_data)

        exif = image._getexif()

        # camera make
        self.assertEqual(exif[271], "Canon")

        jpeg_image = Image.open('Tests/images/flower.jpg')
        expected_exif = jpeg_image.info['exif']

        self.assertEqual(exif_data, expected_exif)

    def test_write_exif_metadata(self):
        from io import BytesIO

        file_path = "Tests/images/flower.jpg"
        image = Image.open(file_path)
        expected_exif = image.info['exif']

        test_buffer = BytesIO()

        image.save(test_buffer, "webp", exif=expected_exif)

        test_buffer.seek(0)
        webp_image = Image.open(test_buffer)

        webp_exif = webp_image.info.get('exif', None)
        self.assertTrue(webp_exif)
        if webp_exif:
            self.assertEqual(
                webp_exif, expected_exif, "WebP EXIF didn't match")

    def test_read_icc_profile(self):

        file_path = "Tests/images/flower2.webp"
        image = Image.open(file_path)

        self.assertEqual(image.format, "WEBP")
        self.assertTrue(image.info.get("icc_profile", None))

        icc = image.info['icc_profile']

        jpeg_image = Image.open('Tests/images/flower2.jpg')
        expected_icc = jpeg_image.info['icc_profile']

        self.assertEqual(icc, expected_icc)

    def test_write_icc_metadata(self):
        from io import BytesIO

        file_path = "Tests/images/flower2.jpg"
        image = Image.open(file_path)
        expected_icc_profile = image.info['icc_profile']

        test_buffer = BytesIO()

        image.save(test_buffer, "webp", icc_profile=expected_icc_profile)

        test_buffer.seek(0)
        webp_image = Image.open(test_buffer)

        webp_icc_profile = webp_image.info.get('icc_profile', None)

        self.assertTrue(webp_icc_profile)
        if webp_icc_profile:
            self.assertEqual(
                webp_icc_profile, expected_icc_profile,
                "Webp ICC didn't match")

    def test_read_no_exif(self):
        from io import BytesIO

        file_path = "Tests/images/flower.jpg"
        image = Image.open(file_path)
        self.assertTrue('exif' in image.info)

        test_buffer = BytesIO()

        image.save(test_buffer, "webp")

        test_buffer.seek(0)
        webp_image = Image.open(test_buffer)

        self.assertFalse(webp_image._getexif())


if __name__ == '__main__':
    unittest.main()
