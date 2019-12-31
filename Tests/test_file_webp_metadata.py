from io import BytesIO

from PIL import Image

from .helper import PillowTestCase

try:
    from PIL import _webp

    HAVE_WEBP = True
except ImportError:
    HAVE_WEBP = False


class TestFileWebpMetadata(PillowTestCase):
    def setUp(self):
        if not HAVE_WEBP:
            self.skipTest("WebP support not installed")
            return

        if not _webp.HAVE_WEBPMUX:
            self.skipTest("WebPMux support not installed")

    def test_read_exif_metadata(self):

        file_path = "Tests/images/flower.webp"
        with Image.open(file_path) as image:

            self.assertEqual(image.format, "WEBP")
            exif_data = image.info.get("exif", None)
            self.assertTrue(exif_data)

            exif = image._getexif()

            # camera make
            self.assertEqual(exif[271], "Canon")

            with Image.open("Tests/images/flower.jpg") as jpeg_image:
                expected_exif = jpeg_image.info["exif"]

                self.assertEqual(exif_data, expected_exif)

    def test_write_exif_metadata(self):
        file_path = "Tests/images/flower.jpg"
        test_buffer = BytesIO()
        with Image.open(file_path) as image:
            expected_exif = image.info["exif"]

            image.save(test_buffer, "webp", exif=expected_exif)

        test_buffer.seek(0)
        with Image.open(test_buffer) as webp_image:
            webp_exif = webp_image.info.get("exif", None)
        self.assertTrue(webp_exif)
        if webp_exif:
            self.assertEqual(webp_exif, expected_exif, "WebP EXIF didn't match")

    def test_read_icc_profile(self):

        file_path = "Tests/images/flower2.webp"
        with Image.open(file_path) as image:

            self.assertEqual(image.format, "WEBP")
            self.assertTrue(image.info.get("icc_profile", None))

            icc = image.info["icc_profile"]

            with Image.open("Tests/images/flower2.jpg") as jpeg_image:
                expected_icc = jpeg_image.info["icc_profile"]

                self.assertEqual(icc, expected_icc)

    def test_write_icc_metadata(self):
        file_path = "Tests/images/flower2.jpg"
        test_buffer = BytesIO()
        with Image.open(file_path) as image:
            expected_icc_profile = image.info["icc_profile"]

            image.save(test_buffer, "webp", icc_profile=expected_icc_profile)

        test_buffer.seek(0)
        with Image.open(test_buffer) as webp_image:
            webp_icc_profile = webp_image.info.get("icc_profile", None)

        self.assertTrue(webp_icc_profile)
        if webp_icc_profile:
            self.assertEqual(
                webp_icc_profile, expected_icc_profile, "Webp ICC didn't match"
            )

    def test_read_no_exif(self):
        file_path = "Tests/images/flower.jpg"
        test_buffer = BytesIO()
        with Image.open(file_path) as image:
            self.assertIn("exif", image.info)

            image.save(test_buffer, "webp")

        test_buffer.seek(0)
        with Image.open(test_buffer) as webp_image:
            self.assertFalse(webp_image._getexif())

    def test_write_animated_metadata(self):
        if not _webp.HAVE_WEBPANIM:
            self.skipTest("WebP animation support not available")

        iccp_data = b"<iccp_data>"
        exif_data = b"<exif_data>"
        xmp_data = b"<xmp_data>"

        temp_file = self.tempfile("temp.webp")
        with Image.open("Tests/images/anim_frame1.webp") as frame1:
            with Image.open("Tests/images/anim_frame2.webp") as frame2:
                frame1.save(
                    temp_file,
                    save_all=True,
                    append_images=[frame2, frame1, frame2],
                    icc_profile=iccp_data,
                    exif=exif_data,
                    xmp=xmp_data,
                )

        with Image.open(temp_file) as image:
            self.assertIn("icc_profile", image.info)
            self.assertIn("exif", image.info)
            self.assertIn("xmp", image.info)
            self.assertEqual(iccp_data, image.info.get("icc_profile", None))
            self.assertEqual(exif_data, image.info.get("exif", None))
            self.assertEqual(xmp_data, image.info.get("xmp", None))
