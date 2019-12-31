import unittest
import zlib
from io import BytesIO

from PIL import Image, ImageFile, PngImagePlugin

from .helper import PillowLeakTestCase, PillowTestCase, hopper, is_win32

try:
    from PIL import _webp

    HAVE_WEBP = True
except ImportError:
    HAVE_WEBP = False

codecs = dir(Image.core)


# sample png stream

TEST_PNG_FILE = "Tests/images/hopper.png"

# stuff to create inline PNG images

MAGIC = PngImagePlugin._MAGIC


def chunk(cid, *data):
    test_file = BytesIO()
    PngImagePlugin.putchunk(*(test_file, cid) + data)
    return test_file.getvalue()


o32 = PngImagePlugin.o32

IHDR = chunk(b"IHDR", o32(1), o32(1), b"\x08\x02", b"\0\0\0")
IDAT = chunk(b"IDAT")
IEND = chunk(b"IEND")

HEAD = MAGIC + IHDR
TAIL = IDAT + IEND


def load(data):
    return Image.open(BytesIO(data))


def roundtrip(im, **options):
    out = BytesIO()
    im.save(out, "PNG", **options)
    out.seek(0)
    return Image.open(out)


class TestFilePng(PillowTestCase):
    def setUp(self):
        if "zip_encoder" not in codecs or "zip_decoder" not in codecs:
            self.skipTest("zip/deflate support not available")

    def get_chunks(self, filename):
        chunks = []
        with open(filename, "rb") as fp:
            fp.read(8)
            with PngImagePlugin.PngStream(fp) as png:
                while True:
                    cid, pos, length = png.read()
                    chunks.append(cid)
                    try:
                        s = png.call(cid, pos, length)
                    except EOFError:
                        break
                    png.crc(cid, s)
        return chunks

    def test_sanity(self):

        # internal version number
        self.assertRegex(Image.core.zlib_version, r"\d+\.\d+\.\d+(\.\d+)?$")

        test_file = self.tempfile("temp.png")

        hopper("RGB").save(test_file)

        with Image.open(test_file) as im:
            im.load()
            self.assertEqual(im.mode, "RGB")
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.format, "PNG")
            self.assertEqual(im.get_format_mimetype(), "image/png")

        for mode in ["1", "L", "P", "RGB", "I", "I;16"]:
            im = hopper(mode)
            im.save(test_file)
            with Image.open(test_file) as reloaded:
                if mode == "I;16":
                    reloaded = reloaded.convert(mode)
                self.assert_image_equal(reloaded, im)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError, PngImagePlugin.PngImageFile, invalid_file)

    def test_broken(self):
        # Check reading of totally broken files.  In this case, the test
        # file was checked into Subversion as a text file.

        test_file = "Tests/images/broken.png"
        self.assertRaises(IOError, Image.open, test_file)

    def test_bad_text(self):
        # Make sure PIL can read malformed tEXt chunks (@PIL152)

        im = load(HEAD + chunk(b"tEXt") + TAIL)
        self.assertEqual(im.info, {})

        im = load(HEAD + chunk(b"tEXt", b"spam") + TAIL)
        self.assertEqual(im.info, {"spam": ""})

        im = load(HEAD + chunk(b"tEXt", b"spam\0") + TAIL)
        self.assertEqual(im.info, {"spam": ""})

        im = load(HEAD + chunk(b"tEXt", b"spam\0egg") + TAIL)
        self.assertEqual(im.info, {"spam": "egg"})

        im = load(HEAD + chunk(b"tEXt", b"spam\0egg\0") + TAIL)
        self.assertEqual(im.info, {"spam": "egg\x00"})

    def test_bad_ztxt(self):
        # Test reading malformed zTXt chunks (python-pillow/Pillow#318)

        im = load(HEAD + chunk(b"zTXt") + TAIL)
        self.assertEqual(im.info, {})

        im = load(HEAD + chunk(b"zTXt", b"spam") + TAIL)
        self.assertEqual(im.info, {"spam": ""})

        im = load(HEAD + chunk(b"zTXt", b"spam\0") + TAIL)
        self.assertEqual(im.info, {"spam": ""})

        im = load(HEAD + chunk(b"zTXt", b"spam\0\0") + TAIL)
        self.assertEqual(im.info, {"spam": ""})

        im = load(HEAD + chunk(b"zTXt", b"spam\0\0" + zlib.compress(b"egg")[:1]) + TAIL)
        self.assertEqual(im.info, {"spam": ""})

        im = load(HEAD + chunk(b"zTXt", b"spam\0\0" + zlib.compress(b"egg")) + TAIL)
        self.assertEqual(im.info, {"spam": "egg"})

    def test_bad_itxt(self):

        im = load(HEAD + chunk(b"iTXt") + TAIL)
        self.assertEqual(im.info, {})

        im = load(HEAD + chunk(b"iTXt", b"spam") + TAIL)
        self.assertEqual(im.info, {})

        im = load(HEAD + chunk(b"iTXt", b"spam\0") + TAIL)
        self.assertEqual(im.info, {})

        im = load(HEAD + chunk(b"iTXt", b"spam\0\x02") + TAIL)
        self.assertEqual(im.info, {})

        im = load(HEAD + chunk(b"iTXt", b"spam\0\0\0foo\0") + TAIL)
        self.assertEqual(im.info, {})

        im = load(HEAD + chunk(b"iTXt", b"spam\0\0\0en\0Spam\0egg") + TAIL)
        self.assertEqual(im.info, {"spam": "egg"})
        self.assertEqual(im.info["spam"].lang, "en")
        self.assertEqual(im.info["spam"].tkey, "Spam")

        im = load(
            HEAD
            + chunk(b"iTXt", b"spam\0\1\0en\0Spam\0" + zlib.compress(b"egg")[:1])
            + TAIL
        )
        self.assertEqual(im.info, {"spam": ""})

        im = load(
            HEAD
            + chunk(b"iTXt", b"spam\0\1\1en\0Spam\0" + zlib.compress(b"egg"))
            + TAIL
        )
        self.assertEqual(im.info, {})

        im = load(
            HEAD
            + chunk(b"iTXt", b"spam\0\1\0en\0Spam\0" + zlib.compress(b"egg"))
            + TAIL
        )
        self.assertEqual(im.info, {"spam": "egg"})
        self.assertEqual(im.info["spam"].lang, "en")
        self.assertEqual(im.info["spam"].tkey, "Spam")

    def test_interlace(self):

        test_file = "Tests/images/pil123p.png"
        with Image.open(test_file) as im:
            self.assert_image(im, "P", (162, 150))
            self.assertTrue(im.info.get("interlace"))

            im.load()

        test_file = "Tests/images/pil123rgba.png"
        with Image.open(test_file) as im:
            self.assert_image(im, "RGBA", (162, 150))
            self.assertTrue(im.info.get("interlace"))

            im.load()

    def test_load_transparent_p(self):
        test_file = "Tests/images/pil123p.png"
        with Image.open(test_file) as im:
            self.assert_image(im, "P", (162, 150))
            im = im.convert("RGBA")
        self.assert_image(im, "RGBA", (162, 150))

        # image has 124 unique alpha values
        self.assertEqual(len(im.getchannel("A").getcolors()), 124)

    def test_load_transparent_rgb(self):
        test_file = "Tests/images/rgb_trns.png"
        with Image.open(test_file) as im:
            self.assertEqual(im.info["transparency"], (0, 255, 52))

            self.assert_image(im, "RGB", (64, 64))
            im = im.convert("RGBA")
        self.assert_image(im, "RGBA", (64, 64))

        # image has 876 transparent pixels
        self.assertEqual(im.getchannel("A").getcolors()[0][0], 876)

    def test_save_p_transparent_palette(self):
        in_file = "Tests/images/pil123p.png"
        with Image.open(in_file) as im:
            # 'transparency' contains a byte string with the opacity for
            # each palette entry
            self.assertEqual(len(im.info["transparency"]), 256)

            test_file = self.tempfile("temp.png")
            im.save(test_file)

        # check if saved image contains same transparency
        with Image.open(test_file) as im:
            self.assertEqual(len(im.info["transparency"]), 256)

            self.assert_image(im, "P", (162, 150))
            im = im.convert("RGBA")
        self.assert_image(im, "RGBA", (162, 150))

        # image has 124 unique alpha values
        self.assertEqual(len(im.getchannel("A").getcolors()), 124)

    def test_save_p_single_transparency(self):
        in_file = "Tests/images/p_trns_single.png"
        with Image.open(in_file) as im:
            # pixel value 164 is full transparent
            self.assertEqual(im.info["transparency"], 164)
            self.assertEqual(im.getpixel((31, 31)), 164)

            test_file = self.tempfile("temp.png")
            im.save(test_file)

        # check if saved image contains same transparency
        with Image.open(test_file) as im:
            self.assertEqual(im.info["transparency"], 164)
            self.assertEqual(im.getpixel((31, 31)), 164)
            self.assert_image(im, "P", (64, 64))
            im = im.convert("RGBA")
        self.assert_image(im, "RGBA", (64, 64))

        self.assertEqual(im.getpixel((31, 31)), (0, 255, 52, 0))

        # image has 876 transparent pixels
        self.assertEqual(im.getchannel("A").getcolors()[0][0], 876)

    def test_save_p_transparent_black(self):
        # check if solid black image with full transparency
        # is supported (check for #1838)
        im = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        self.assertEqual(im.getcolors(), [(100, (0, 0, 0, 0))])

        im = im.convert("P")
        test_file = self.tempfile("temp.png")
        im.save(test_file)

        # check if saved image contains same transparency
        with Image.open(test_file) as im:
            self.assertEqual(len(im.info["transparency"]), 256)
            self.assert_image(im, "P", (10, 10))
            im = im.convert("RGBA")
        self.assert_image(im, "RGBA", (10, 10))
        self.assertEqual(im.getcolors(), [(100, (0, 0, 0, 0))])

    def test_save_greyscale_transparency(self):
        for mode, num_transparent in {"1": 1994, "L": 559, "I": 559}.items():
            in_file = "Tests/images/" + mode.lower() + "_trns.png"
            with Image.open(in_file) as im:
                self.assertEqual(im.mode, mode)
                self.assertEqual(im.info["transparency"], 255)

                im_rgba = im.convert("RGBA")
            self.assertEqual(im_rgba.getchannel("A").getcolors()[0][0], num_transparent)

            test_file = self.tempfile("temp.png")
            im.save(test_file)

            with Image.open(test_file) as test_im:
                self.assertEqual(test_im.mode, mode)
                self.assertEqual(test_im.info["transparency"], 255)
                self.assert_image_equal(im, test_im)

            test_im_rgba = test_im.convert("RGBA")
            self.assertEqual(
                test_im_rgba.getchannel("A").getcolors()[0][0], num_transparent
            )

    def test_save_rgb_single_transparency(self):
        in_file = "Tests/images/caption_6_33_22.png"
        with Image.open(in_file) as im:
            test_file = self.tempfile("temp.png")
            im.save(test_file)

    def test_load_verify(self):
        # Check open/load/verify exception (@PIL150)

        with Image.open(TEST_PNG_FILE) as im:
            # Assert that there is no unclosed file warning
            self.assert_warning(None, im.verify)

        with Image.open(TEST_PNG_FILE) as im:
            im.load()
            self.assertRaises(RuntimeError, im.verify)

    def test_verify_struct_error(self):
        # Check open/load/verify exception (#1755)

        # offsets to test, -10: breaks in i32() in read. (IOError)
        #                  -13: breaks in crc, txt chunk.
        #                  -14: malformed chunk

        for offset in (-10, -13, -14):
            with open(TEST_PNG_FILE, "rb") as f:
                test_file = f.read()[:offset]

            with Image.open(BytesIO(test_file)) as im:
                self.assertIsNotNone(im.fp)
                self.assertRaises((IOError, SyntaxError), im.verify)

    def test_verify_ignores_crc_error(self):
        # check ignores crc errors in ancillary chunks

        chunk_data = chunk(b"tEXt", b"spam")
        broken_crc_chunk_data = chunk_data[:-1] + b"q"  # break CRC

        image_data = HEAD + broken_crc_chunk_data + TAIL
        self.assertRaises(SyntaxError, PngImagePlugin.PngImageFile, BytesIO(image_data))

        ImageFile.LOAD_TRUNCATED_IMAGES = True
        try:
            im = load(image_data)
            self.assertIsNotNone(im)
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = False

    def test_verify_not_ignores_crc_error_in_required_chunk(self):
        # check does not ignore crc errors in required chunks

        image_data = MAGIC + IHDR[:-1] + b"q" + TAIL

        ImageFile.LOAD_TRUNCATED_IMAGES = True
        try:
            self.assertRaises(
                SyntaxError, PngImagePlugin.PngImageFile, BytesIO(image_data)
            )
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = False

    def test_roundtrip_dpi(self):
        # Check dpi roundtripping

        with Image.open(TEST_PNG_FILE) as im:
            im = roundtrip(im, dpi=(100, 100))
        self.assertEqual(im.info["dpi"], (100, 100))

    def test_load_dpi_rounding(self):
        # Round up
        with Image.open(TEST_PNG_FILE) as im:
            self.assertEqual(im.info["dpi"], (96, 96))

        # Round down
        with Image.open("Tests/images/icc_profile_none.png") as im:
            self.assertEqual(im.info["dpi"], (72, 72))

    def test_save_dpi_rounding(self):
        with Image.open(TEST_PNG_FILE) as im:
            im = roundtrip(im, dpi=(72.2, 72.2))
        self.assertEqual(im.info["dpi"], (72, 72))

        im = roundtrip(im, dpi=(72.8, 72.8))
        self.assertEqual(im.info["dpi"], (73, 73))

    def test_roundtrip_text(self):
        # Check text roundtripping

        with Image.open(TEST_PNG_FILE) as im:
            info = PngImagePlugin.PngInfo()
            info.add_text("TXT", "VALUE")
            info.add_text("ZIP", "VALUE", zip=True)

            im = roundtrip(im, pnginfo=info)
        self.assertEqual(im.info, {"TXT": "VALUE", "ZIP": "VALUE"})
        self.assertEqual(im.text, {"TXT": "VALUE", "ZIP": "VALUE"})

    def test_roundtrip_itxt(self):
        # Check iTXt roundtripping

        im = Image.new("RGB", (32, 32))
        info = PngImagePlugin.PngInfo()
        info.add_itxt("spam", "Eggs", "en", "Spam")
        info.add_text("eggs", PngImagePlugin.iTXt("Spam", "en", "Eggs"), zip=True)

        im = roundtrip(im, pnginfo=info)
        self.assertEqual(im.info, {"spam": "Eggs", "eggs": "Spam"})
        self.assertEqual(im.text, {"spam": "Eggs", "eggs": "Spam"})
        self.assertEqual(im.text["spam"].lang, "en")
        self.assertEqual(im.text["spam"].tkey, "Spam")
        self.assertEqual(im.text["eggs"].lang, "en")
        self.assertEqual(im.text["eggs"].tkey, "Eggs")

    def test_nonunicode_text(self):
        # Check so that non-Unicode text is saved as a tEXt rather than iTXt

        im = Image.new("RGB", (32, 32))
        info = PngImagePlugin.PngInfo()
        info.add_text("Text", "Ascii")
        im = roundtrip(im, pnginfo=info)
        self.assertIsInstance(im.info["Text"], str)

    def test_unicode_text(self):
        # Check preservation of non-ASCII characters

        def rt_text(value):
            im = Image.new("RGB", (32, 32))
            info = PngImagePlugin.PngInfo()
            info.add_text("Text", value)
            im = roundtrip(im, pnginfo=info)
            self.assertEqual(im.info, {"Text": value})

        rt_text(" Aa" + chr(0xA0) + chr(0xC4) + chr(0xFF))  # Latin1
        rt_text(chr(0x400) + chr(0x472) + chr(0x4FF))  # Cyrillic
        # CJK:
        rt_text(chr(0x4E00) + chr(0x66F0) + chr(0x9FBA) + chr(0x3042) + chr(0xAC00))
        rt_text("A" + chr(0xC4) + chr(0x472) + chr(0x3042))  # Combined

    def test_scary(self):
        # Check reading of evil PNG file.  For information, see:
        # http://scary.beasts.org/security/CESA-2004-001.txt
        # The first byte is removed from pngtest_bad.png
        # to avoid classification as malware.

        with open("Tests/images/pngtest_bad.png.bin", "rb") as fd:
            data = b"\x89" + fd.read()

        pngfile = BytesIO(data)
        self.assertRaises(IOError, Image.open, pngfile)

    def test_trns_rgb(self):
        # Check writing and reading of tRNS chunks for RGB images.
        # Independent file sample provided by Sebastian Spaeth.

        test_file = "Tests/images/caption_6_33_22.png"
        with Image.open(test_file) as im:
            self.assertEqual(im.info["transparency"], (248, 248, 248))

            # check saving transparency by default
            im = roundtrip(im)
        self.assertEqual(im.info["transparency"], (248, 248, 248))

        im = roundtrip(im, transparency=(0, 1, 2))
        self.assertEqual(im.info["transparency"], (0, 1, 2))

    def test_trns_p(self):
        # Check writing a transparency of 0, issue #528
        im = hopper("P")
        im.info["transparency"] = 0

        f = self.tempfile("temp.png")
        im.save(f)

        with Image.open(f) as im2:
            self.assertIn("transparency", im2.info)

            self.assert_image_equal(im2.convert("RGBA"), im.convert("RGBA"))

    def test_trns_null(self):
        # Check reading images with null tRNS value, issue #1239
        test_file = "Tests/images/tRNS_null_1x1.png"
        with Image.open(test_file) as im:

            self.assertEqual(im.info["transparency"], 0)

    def test_save_icc_profile(self):
        with Image.open("Tests/images/icc_profile_none.png") as im:
            self.assertIsNone(im.info["icc_profile"])

            with Image.open("Tests/images/icc_profile.png") as with_icc:
                expected_icc = with_icc.info["icc_profile"]

                im = roundtrip(im, icc_profile=expected_icc)
                self.assertEqual(im.info["icc_profile"], expected_icc)

    def test_discard_icc_profile(self):
        with Image.open("Tests/images/icc_profile.png") as im:
            im = roundtrip(im, icc_profile=None)
        self.assertNotIn("icc_profile", im.info)

    def test_roundtrip_icc_profile(self):
        with Image.open("Tests/images/icc_profile.png") as im:
            expected_icc = im.info["icc_profile"]

            im = roundtrip(im)
        self.assertEqual(im.info["icc_profile"], expected_icc)

    def test_roundtrip_no_icc_profile(self):
        with Image.open("Tests/images/icc_profile_none.png") as im:
            self.assertIsNone(im.info["icc_profile"])

            im = roundtrip(im)
        self.assertNotIn("icc_profile", im.info)

    def test_repr_png(self):
        im = hopper()

        with Image.open(BytesIO(im._repr_png_())) as repr_png:
            self.assertEqual(repr_png.format, "PNG")
            self.assert_image_equal(im, repr_png)

    def test_chunk_order(self):
        with Image.open("Tests/images/icc_profile.png") as im:
            test_file = self.tempfile("temp.png")
            im.convert("P").save(test_file, dpi=(100, 100))

        chunks = self.get_chunks(test_file)

        # https://www.w3.org/TR/PNG/#5ChunkOrdering
        # IHDR - shall be first
        self.assertEqual(chunks.index(b"IHDR"), 0)
        # PLTE - before first IDAT
        self.assertLess(chunks.index(b"PLTE"), chunks.index(b"IDAT"))
        # iCCP - before PLTE and IDAT
        self.assertLess(chunks.index(b"iCCP"), chunks.index(b"PLTE"))
        self.assertLess(chunks.index(b"iCCP"), chunks.index(b"IDAT"))
        # tRNS - after PLTE, before IDAT
        self.assertGreater(chunks.index(b"tRNS"), chunks.index(b"PLTE"))
        self.assertLess(chunks.index(b"tRNS"), chunks.index(b"IDAT"))
        # pHYs - before IDAT
        self.assertLess(chunks.index(b"pHYs"), chunks.index(b"IDAT"))

    def test_getchunks(self):
        im = hopper()

        chunks = PngImagePlugin.getchunks(im)
        self.assertEqual(len(chunks), 3)

    def test_textual_chunks_after_idat(self):
        with Image.open("Tests/images/hopper.png") as im:
            self.assertIn("comment", im.text.keys())
            for k, v in {
                "date:create": "2014-09-04T09:37:08+03:00",
                "date:modify": "2014-09-04T09:37:08+03:00",
            }.items():
                self.assertEqual(im.text[k], v)

        # Raises a SyntaxError in load_end
        with Image.open("Tests/images/broken_data_stream.png") as im:
            with self.assertRaises(IOError):
                self.assertIsInstance(im.text, dict)

        # Raises a UnicodeDecodeError in load_end
        with Image.open("Tests/images/truncated_image.png") as im:
            # The file is truncated
            self.assertRaises(IOError, lambda: im.text)
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            self.assertIsInstance(im.text, dict)
            ImageFile.LOAD_TRUNCATED_IMAGES = False

        # Raises an EOFError in load_end
        with Image.open("Tests/images/hopper_idat_after_image_end.png") as im:
            self.assertEqual(im.text, {"TXT": "VALUE", "ZIP": "VALUE"})

    def test_exif(self):
        with Image.open("Tests/images/exif.png") as im:
            exif = im._getexif()
        self.assertEqual(exif[274], 1)

    def test_exif_save(self):
        with Image.open("Tests/images/exif.png") as im:
            test_file = self.tempfile("temp.png")
            im.save(test_file)

        with Image.open(test_file) as reloaded:
            exif = reloaded._getexif()
        self.assertEqual(exif[274], 1)

    def test_exif_from_jpg(self):
        with Image.open("Tests/images/pil_sample_rgb.jpg") as im:
            test_file = self.tempfile("temp.png")
            im.save(test_file)

        with Image.open(test_file) as reloaded:
            exif = reloaded._getexif()
        self.assertEqual(exif[305], "Adobe Photoshop CS Macintosh")

    def test_exif_argument(self):
        with Image.open(TEST_PNG_FILE) as im:
            test_file = self.tempfile("temp.png")
            im.save(test_file, exif=b"exifstring")

        with Image.open(test_file) as reloaded:
            self.assertEqual(reloaded.info["exif"], b"Exif\x00\x00exifstring")

    @unittest.skipUnless(
        HAVE_WEBP and _webp.HAVE_WEBPANIM, "WebP support not installed with animation"
    )
    def test_apng(self):
        with Image.open("Tests/images/iss634.apng") as im:
            self.assertEqual(im.get_format_mimetype(), "image/apng")

            # This also tests reading unknown PNG chunks (fcTL and fdAT) in load_end
            with Image.open("Tests/images/iss634.webp") as expected:
                self.assert_image_similar(im, expected, 0.23)


@unittest.skipIf(is_win32(), "requires Unix or macOS")
class TestTruncatedPngPLeaks(PillowLeakTestCase):
    mem_limit = 2 * 1024  # max increase in K
    iterations = 100  # Leak is 56k/iteration, this will leak 5.6megs

    def setUp(self):
        if "zip_encoder" not in codecs or "zip_decoder" not in codecs:
            self.skipTest("zip/deflate support not available")

    def test_leak_load(self):
        with open("Tests/images/hopper.png", "rb") as f:
            DATA = BytesIO(f.read(16 * 1024))

        ImageFile.LOAD_TRUNCATED_IMAGES = True
        with Image.open(DATA) as im:
            im.load()

        def core():
            with Image.open(DATA) as im:
                im.load()

        try:
            self._test_leak(core)
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = False
