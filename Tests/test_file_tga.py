import os
from glob import glob
from itertools import product

from PIL import Image

from .helper import PillowTestCase

_TGA_DIR = os.path.join("Tests", "images", "tga")
_TGA_DIR_COMMON = os.path.join(_TGA_DIR, "common")


class TestFileTga(PillowTestCase):

    _MODES = ("L", "LA", "P", "RGB", "RGBA")
    _ORIGINS = ("tl", "bl")

    _ORIGIN_TO_ORIENTATION = {"tl": 1, "bl": -1}

    def test_sanity(self):
        for mode in self._MODES:
            png_paths = glob(
                os.path.join(_TGA_DIR_COMMON, "*x*_{}.png".format(mode.lower()))
            )

            for png_path in png_paths:
                with Image.open(png_path) as reference_im:
                    self.assertEqual(reference_im.mode, mode)

                    path_no_ext = os.path.splitext(png_path)[0]
                    for origin, rle in product(self._ORIGINS, (True, False)):
                        tga_path = "{}_{}_{}.tga".format(
                            path_no_ext, origin, "rle" if rle else "raw"
                        )

                        with Image.open(tga_path) as original_im:
                            self.assertEqual(original_im.format, "TGA")
                            self.assertEqual(
                                original_im.get_format_mimetype(), "image/x-tga"
                            )
                            if rle:
                                self.assertEqual(
                                    original_im.info["compression"], "tga_rle"
                                )
                            self.assertEqual(
                                original_im.info["orientation"],
                                self._ORIGIN_TO_ORIENTATION[origin],
                            )
                            if mode == "P":
                                self.assertEqual(
                                    original_im.getpalette(), reference_im.getpalette()
                                )

                            self.assert_image_equal(original_im, reference_im)

                            # Generate a new test name every time so the
                            # test will not fail with permission error
                            # on Windows.
                            out = self.tempfile("temp.tga")

                            original_im.save(out, rle=rle)
                            with Image.open(out) as saved_im:
                                if rle:
                                    self.assertEqual(
                                        saved_im.info["compression"],
                                        original_im.info["compression"],
                                    )
                                self.assertEqual(
                                    saved_im.info["orientation"],
                                    original_im.info["orientation"],
                                )
                                if mode == "P":
                                    self.assertEqual(
                                        saved_im.getpalette(), original_im.getpalette()
                                    )

                                self.assert_image_equal(saved_im, original_im)

    def test_id_field(self):
        # tga file with id field
        test_file = "Tests/images/tga_id_field.tga"

        # Act
        with Image.open(test_file) as im:

            # Assert
            self.assertEqual(im.size, (100, 100))

    def test_id_field_rle(self):
        # tga file with id field
        test_file = "Tests/images/rgb32rle.tga"

        # Act
        with Image.open(test_file) as im:

            # Assert
            self.assertEqual(im.size, (199, 199))

    def test_save(self):
        test_file = "Tests/images/tga_id_field.tga"
        with Image.open(test_file) as im:
            out = self.tempfile("temp.tga")

            # Save
            im.save(out)
            with Image.open(out) as test_im:
                self.assertEqual(test_im.size, (100, 100))
                self.assertEqual(test_im.info["id_section"], im.info["id_section"])

            # RGBA save
            im.convert("RGBA").save(out)
        with Image.open(out) as test_im:
            self.assertEqual(test_im.size, (100, 100))

    def test_save_id_section(self):
        test_file = "Tests/images/rgb32rle.tga"
        with Image.open(test_file) as im:
            out = self.tempfile("temp.tga")

            # Check there is no id section
            im.save(out)
        with Image.open(out) as test_im:
            self.assertNotIn("id_section", test_im.info)

        # Save with custom id section
        im.save(out, id_section=b"Test content")
        with Image.open(out) as test_im:
            self.assertEqual(test_im.info["id_section"], b"Test content")

        # Save with custom id section greater than 255 characters
        id_section = b"Test content" * 25
        self.assert_warning(UserWarning, lambda: im.save(out, id_section=id_section))
        with Image.open(out) as test_im:
            self.assertEqual(test_im.info["id_section"], id_section[:255])

        test_file = "Tests/images/tga_id_field.tga"
        with Image.open(test_file) as im:

            # Save with no id section
            im.save(out, id_section="")
        with Image.open(out) as test_im:
            self.assertNotIn("id_section", test_im.info)

    def test_save_orientation(self):
        test_file = "Tests/images/rgb32rle.tga"
        out = self.tempfile("temp.tga")
        with Image.open(test_file) as im:
            self.assertEqual(im.info["orientation"], -1)

            im.save(out, orientation=1)
        with Image.open(out) as test_im:
            self.assertEqual(test_im.info["orientation"], 1)

    def test_save_rle(self):
        test_file = "Tests/images/rgb32rle.tga"
        with Image.open(test_file) as im:
            self.assertEqual(im.info["compression"], "tga_rle")

            out = self.tempfile("temp.tga")

            # Save
            im.save(out)
        with Image.open(out) as test_im:
            self.assertEqual(test_im.size, (199, 199))
            self.assertEqual(test_im.info["compression"], "tga_rle")

        # Save without compression
        im.save(out, compression=None)
        with Image.open(out) as test_im:
            self.assertNotIn("compression", test_im.info)

        # RGBA save
        im.convert("RGBA").save(out)
        with Image.open(out) as test_im:
            self.assertEqual(test_im.size, (199, 199))

        test_file = "Tests/images/tga_id_field.tga"
        with Image.open(test_file) as im:
            self.assertNotIn("compression", im.info)

            # Save with compression
            im.save(out, compression="tga_rle")
        with Image.open(out) as test_im:
            self.assertEqual(test_im.info["compression"], "tga_rle")

    def test_save_l_transparency(self):
        # There are 559 transparent pixels in la.tga.
        num_transparent = 559

        in_file = "Tests/images/la.tga"
        with Image.open(in_file) as im:
            self.assertEqual(im.mode, "LA")
            self.assertEqual(im.getchannel("A").getcolors()[0][0], num_transparent)

            out = self.tempfile("temp.tga")
            im.save(out)

        with Image.open(out) as test_im:
            self.assertEqual(test_im.mode, "LA")
            self.assertEqual(test_im.getchannel("A").getcolors()[0][0], num_transparent)

            self.assert_image_equal(im, test_im)
