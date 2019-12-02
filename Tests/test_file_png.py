import unittest
import zlib
from io import BytesIO

import pytest
from PIL import Image, ImageFile, ImageSequence, PngImagePlugin

from .helper import (
    PillowLeakTestCase,
    PillowTestCase,
    assert_image,
    assert_image_equal,
    assert_image_similar,
    hopper,
    is_big_endian,
    is_win32,
    on_ci,
    skip_unless_feature,
)


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


@skip_unless_feature("zlib")
class TestFilePng(PillowTestCase):
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

    @pytest.mark.xfail(is_big_endian() and on_ci(), reason="Fails on big-endian")
    def test_sanity(self):

        # internal version number
        self.assertRegex(Image.core.zlib_version, r"\d+\.\d+\.\d+(\.\d+)?$")

        test_file = self.tempfile("temp.png")

        hopper("RGB").save(test_file)

        with Image.open(test_file) as im:
            im.load()
            assert im.mode == "RGB"
            assert im.size == (128, 128)
            assert im.format == "PNG"
            assert im.get_format_mimetype() == "image/png"

        for mode in ["1", "L", "P", "RGB", "I", "I;16"]:
            im = hopper(mode)
            im.save(test_file)
            with Image.open(test_file) as reloaded:
                if mode == "I;16":
                    reloaded = reloaded.convert(mode)
                assert_image_equal(reloaded, im)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        with pytest.raises(SyntaxError):
            PngImagePlugin.PngImageFile(invalid_file)

    def test_broken(self):
        # Check reading of totally broken files.  In this case, the test
        # file was checked into Subversion as a text file.

        test_file = "Tests/images/broken.png"
        with pytest.raises(IOError):
            Image.open(test_file)

    def test_bad_text(self):
        # Make sure PIL can read malformed tEXt chunks (@PIL152)

        im = load(HEAD + chunk(b"tEXt") + TAIL)
        assert im.info == {}

        im = load(HEAD + chunk(b"tEXt", b"spam") + TAIL)
        assert im.info == {"spam": ""}

        im = load(HEAD + chunk(b"tEXt", b"spam\0") + TAIL)
        assert im.info == {"spam": ""}

        im = load(HEAD + chunk(b"tEXt", b"spam\0egg") + TAIL)
        assert im.info == {"spam": "egg"}

        im = load(HEAD + chunk(b"tEXt", b"spam\0egg\0") + TAIL)
        assert im.info == {"spam": "egg\x00"}

    def test_bad_ztxt(self):
        # Test reading malformed zTXt chunks (python-pillow/Pillow#318)

        im = load(HEAD + chunk(b"zTXt") + TAIL)
        assert im.info == {}

        im = load(HEAD + chunk(b"zTXt", b"spam") + TAIL)
        assert im.info == {"spam": ""}

        im = load(HEAD + chunk(b"zTXt", b"spam\0") + TAIL)
        assert im.info == {"spam": ""}

        im = load(HEAD + chunk(b"zTXt", b"spam\0\0") + TAIL)
        assert im.info == {"spam": ""}

        im = load(HEAD + chunk(b"zTXt", b"spam\0\0" + zlib.compress(b"egg")[:1]) + TAIL)
        assert im.info == {"spam": ""}

        im = load(HEAD + chunk(b"zTXt", b"spam\0\0" + zlib.compress(b"egg")) + TAIL)
        assert im.info == {"spam": "egg"}

    def test_bad_itxt(self):

        im = load(HEAD + chunk(b"iTXt") + TAIL)
        assert im.info == {}

        im = load(HEAD + chunk(b"iTXt", b"spam") + TAIL)
        assert im.info == {}

        im = load(HEAD + chunk(b"iTXt", b"spam\0") + TAIL)
        assert im.info == {}

        im = load(HEAD + chunk(b"iTXt", b"spam\0\x02") + TAIL)
        assert im.info == {}

        im = load(HEAD + chunk(b"iTXt", b"spam\0\0\0foo\0") + TAIL)
        assert im.info == {}

        im = load(HEAD + chunk(b"iTXt", b"spam\0\0\0en\0Spam\0egg") + TAIL)
        assert im.info == {"spam": "egg"}
        assert im.info["spam"].lang == "en"
        assert im.info["spam"].tkey == "Spam"

        im = load(
            HEAD
            + chunk(b"iTXt", b"spam\0\1\0en\0Spam\0" + zlib.compress(b"egg")[:1])
            + TAIL
        )
        assert im.info == {"spam": ""}

        im = load(
            HEAD
            + chunk(b"iTXt", b"spam\0\1\1en\0Spam\0" + zlib.compress(b"egg"))
            + TAIL
        )
        assert im.info == {}

        im = load(
            HEAD
            + chunk(b"iTXt", b"spam\0\1\0en\0Spam\0" + zlib.compress(b"egg"))
            + TAIL
        )
        assert im.info == {"spam": "egg"}
        assert im.info["spam"].lang == "en"
        assert im.info["spam"].tkey == "Spam"

    def test_interlace(self):

        test_file = "Tests/images/pil123p.png"
        with Image.open(test_file) as im:
            assert_image(im, "P", (162, 150))
            assert im.info.get("interlace")

            im.load()

        test_file = "Tests/images/pil123rgba.png"
        with Image.open(test_file) as im:
            assert_image(im, "RGBA", (162, 150))
            assert im.info.get("interlace")

            im.load()

    def test_load_transparent_p(self):
        test_file = "Tests/images/pil123p.png"
        with Image.open(test_file) as im:
            assert_image(im, "P", (162, 150))
            im = im.convert("RGBA")
        assert_image(im, "RGBA", (162, 150))

        # image has 124 unique alpha values
        assert len(im.getchannel("A").getcolors()) == 124

    def test_load_transparent_rgb(self):
        test_file = "Tests/images/rgb_trns.png"
        with Image.open(test_file) as im:
            assert im.info["transparency"] == (0, 255, 52)

            assert_image(im, "RGB", (64, 64))
            im = im.convert("RGBA")
        assert_image(im, "RGBA", (64, 64))

        # image has 876 transparent pixels
        assert im.getchannel("A").getcolors()[0][0] == 876

    def test_save_p_transparent_palette(self):
        in_file = "Tests/images/pil123p.png"
        with Image.open(in_file) as im:
            # 'transparency' contains a byte string with the opacity for
            # each palette entry
            assert len(im.info["transparency"]) == 256

            test_file = self.tempfile("temp.png")
            im.save(test_file)

        # check if saved image contains same transparency
        with Image.open(test_file) as im:
            assert len(im.info["transparency"]) == 256

            assert_image(im, "P", (162, 150))
            im = im.convert("RGBA")
        assert_image(im, "RGBA", (162, 150))

        # image has 124 unique alpha values
        assert len(im.getchannel("A").getcolors()) == 124

    def test_save_p_single_transparency(self):
        in_file = "Tests/images/p_trns_single.png"
        with Image.open(in_file) as im:
            # pixel value 164 is full transparent
            assert im.info["transparency"] == 164
            assert im.getpixel((31, 31)) == 164

            test_file = self.tempfile("temp.png")
            im.save(test_file)

        # check if saved image contains same transparency
        with Image.open(test_file) as im:
            assert im.info["transparency"] == 164
            assert im.getpixel((31, 31)) == 164
            assert_image(im, "P", (64, 64))
            im = im.convert("RGBA")
        assert_image(im, "RGBA", (64, 64))

        assert im.getpixel((31, 31)) == (0, 255, 52, 0)

        # image has 876 transparent pixels
        assert im.getchannel("A").getcolors()[0][0] == 876

    def test_save_p_transparent_black(self):
        # check if solid black image with full transparency
        # is supported (check for #1838)
        im = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        assert im.getcolors() == [(100, (0, 0, 0, 0))]

        im = im.convert("P")
        test_file = self.tempfile("temp.png")
        im.save(test_file)

        # check if saved image contains same transparency
        with Image.open(test_file) as im:
            assert len(im.info["transparency"]) == 256
            assert_image(im, "P", (10, 10))
            im = im.convert("RGBA")
        assert_image(im, "RGBA", (10, 10))
        assert im.getcolors() == [(100, (0, 0, 0, 0))]

    def test_save_greyscale_transparency(self):
        for mode, num_transparent in {"1": 1994, "L": 559, "I": 559}.items():
            in_file = "Tests/images/" + mode.lower() + "_trns.png"
            with Image.open(in_file) as im:
                assert im.mode == mode
                assert im.info["transparency"] == 255

                im_rgba = im.convert("RGBA")
            assert im_rgba.getchannel("A").getcolors()[0][0] == num_transparent

            test_file = self.tempfile("temp.png")
            im.save(test_file)

            with Image.open(test_file) as test_im:
                assert test_im.mode == mode
                assert test_im.info["transparency"] == 255
                assert_image_equal(im, test_im)

            test_im_rgba = test_im.convert("RGBA")
            assert test_im_rgba.getchannel("A").getcolors()[0][0] == num_transparent

    def test_save_rgb_single_transparency(self):
        in_file = "Tests/images/caption_6_33_22.png"
        with Image.open(in_file) as im:
            test_file = self.tempfile("temp.png")
            im.save(test_file)

    def test_load_verify(self):
        # Check open/load/verify exception (@PIL150)

        with Image.open(TEST_PNG_FILE) as im:
            # Assert that there is no unclosed file warning
            pytest.warns(None, im.verify)

        with Image.open(TEST_PNG_FILE) as im:
            im.load()
            with pytest.raises(RuntimeError):
                im.verify()

    def test_verify_struct_error(self):
        # Check open/load/verify exception (#1755)

        # offsets to test, -10: breaks in i32() in read. (IOError)
        #                  -13: breaks in crc, txt chunk.
        #                  -14: malformed chunk

        for offset in (-10, -13, -14):
            with open(TEST_PNG_FILE, "rb") as f:
                test_file = f.read()[:offset]

            with Image.open(BytesIO(test_file)) as im:
                assert im.fp is not None
                with pytest.raises((IOError, SyntaxError)):
                    im.verify()

    def test_verify_ignores_crc_error(self):
        # check ignores crc errors in ancillary chunks

        chunk_data = chunk(b"tEXt", b"spam")
        broken_crc_chunk_data = chunk_data[:-1] + b"q"  # break CRC

        image_data = HEAD + broken_crc_chunk_data + TAIL
        with pytest.raises(SyntaxError):
            PngImagePlugin.PngImageFile(BytesIO(image_data))

        ImageFile.LOAD_TRUNCATED_IMAGES = True
        try:
            im = load(image_data)
            assert im is not None
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = False

    def test_verify_not_ignores_crc_error_in_required_chunk(self):
        # check does not ignore crc errors in required chunks

        image_data = MAGIC + IHDR[:-1] + b"q" + TAIL

        ImageFile.LOAD_TRUNCATED_IMAGES = True
        try:
            with pytest.raises(SyntaxError):
                PngImagePlugin.PngImageFile(BytesIO(image_data))
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = False

    def test_roundtrip_dpi(self):
        # Check dpi roundtripping

        with Image.open(TEST_PNG_FILE) as im:
            im = roundtrip(im, dpi=(100, 100))
        assert im.info["dpi"] == (100, 100)

    def test_load_dpi_rounding(self):
        # Round up
        with Image.open(TEST_PNG_FILE) as im:
            assert im.info["dpi"] == (96, 96)

        # Round down
        with Image.open("Tests/images/icc_profile_none.png") as im:
            assert im.info["dpi"] == (72, 72)

    def test_save_dpi_rounding(self):
        with Image.open(TEST_PNG_FILE) as im:
            im = roundtrip(im, dpi=(72.2, 72.2))
        assert im.info["dpi"] == (72, 72)

        im = roundtrip(im, dpi=(72.8, 72.8))
        assert im.info["dpi"] == (73, 73)

    def test_roundtrip_text(self):
        # Check text roundtripping

        with Image.open(TEST_PNG_FILE) as im:
            info = PngImagePlugin.PngInfo()
            info.add_text("TXT", "VALUE")
            info.add_text("ZIP", "VALUE", zip=True)

            im = roundtrip(im, pnginfo=info)
        assert im.info == {"TXT": "VALUE", "ZIP": "VALUE"}
        assert im.text == {"TXT": "VALUE", "ZIP": "VALUE"}

    def test_roundtrip_itxt(self):
        # Check iTXt roundtripping

        im = Image.new("RGB", (32, 32))
        info = PngImagePlugin.PngInfo()
        info.add_itxt("spam", "Eggs", "en", "Spam")
        info.add_text("eggs", PngImagePlugin.iTXt("Spam", "en", "Eggs"), zip=True)

        im = roundtrip(im, pnginfo=info)
        assert im.info == {"spam": "Eggs", "eggs": "Spam"}
        assert im.text == {"spam": "Eggs", "eggs": "Spam"}
        assert im.text["spam"].lang == "en"
        assert im.text["spam"].tkey == "Spam"
        assert im.text["eggs"].lang == "en"
        assert im.text["eggs"].tkey == "Eggs"

    def test_nonunicode_text(self):
        # Check so that non-Unicode text is saved as a tEXt rather than iTXt

        im = Image.new("RGB", (32, 32))
        info = PngImagePlugin.PngInfo()
        info.add_text("Text", "Ascii")
        im = roundtrip(im, pnginfo=info)
        assert isinstance(im.info["Text"], str)

    def test_unicode_text(self):
        # Check preservation of non-ASCII characters

        def rt_text(value):
            im = Image.new("RGB", (32, 32))
            info = PngImagePlugin.PngInfo()
            info.add_text("Text", value)
            im = roundtrip(im, pnginfo=info)
            assert im.info == {"Text": value}

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
        with pytest.raises(IOError):
            Image.open(pngfile)

    def test_trns_rgb(self):
        # Check writing and reading of tRNS chunks for RGB images.
        # Independent file sample provided by Sebastian Spaeth.

        test_file = "Tests/images/caption_6_33_22.png"
        with Image.open(test_file) as im:
            assert im.info["transparency"] == (248, 248, 248)

            # check saving transparency by default
            im = roundtrip(im)
        assert im.info["transparency"] == (248, 248, 248)

        im = roundtrip(im, transparency=(0, 1, 2))
        assert im.info["transparency"] == (0, 1, 2)

    def test_trns_p(self):
        # Check writing a transparency of 0, issue #528
        im = hopper("P")
        im.info["transparency"] = 0

        f = self.tempfile("temp.png")
        im.save(f)

        with Image.open(f) as im2:
            assert "transparency" in im2.info

            assert_image_equal(im2.convert("RGBA"), im.convert("RGBA"))

    def test_trns_null(self):
        # Check reading images with null tRNS value, issue #1239
        test_file = "Tests/images/tRNS_null_1x1.png"
        with Image.open(test_file) as im:

            assert im.info["transparency"] == 0

    def test_save_icc_profile(self):
        with Image.open("Tests/images/icc_profile_none.png") as im:
            assert im.info["icc_profile"] is None

            with Image.open("Tests/images/icc_profile.png") as with_icc:
                expected_icc = with_icc.info["icc_profile"]

                im = roundtrip(im, icc_profile=expected_icc)
                assert im.info["icc_profile"] == expected_icc

    def test_discard_icc_profile(self):
        with Image.open("Tests/images/icc_profile.png") as im:
            im = roundtrip(im, icc_profile=None)
        assert "icc_profile" not in im.info

    def test_roundtrip_icc_profile(self):
        with Image.open("Tests/images/icc_profile.png") as im:
            expected_icc = im.info["icc_profile"]

            im = roundtrip(im)
        assert im.info["icc_profile"] == expected_icc

    def test_roundtrip_no_icc_profile(self):
        with Image.open("Tests/images/icc_profile_none.png") as im:
            assert im.info["icc_profile"] is None

            im = roundtrip(im)
        assert "icc_profile" not in im.info

    def test_repr_png(self):
        im = hopper()

        with Image.open(BytesIO(im._repr_png_())) as repr_png:
            assert repr_png.format == "PNG"
            assert_image_equal(im, repr_png)

    def test_chunk_order(self):
        with Image.open("Tests/images/icc_profile.png") as im:
            test_file = self.tempfile("temp.png")
            im.convert("P").save(test_file, dpi=(100, 100))

        chunks = self.get_chunks(test_file)

        # https://www.w3.org/TR/PNG/#5ChunkOrdering
        # IHDR - shall be first
        assert chunks.index(b"IHDR") == 0
        # PLTE - before first IDAT
        assert chunks.index(b"PLTE") < chunks.index(b"IDAT")
        # iCCP - before PLTE and IDAT
        assert chunks.index(b"iCCP") < chunks.index(b"PLTE")
        assert chunks.index(b"iCCP") < chunks.index(b"IDAT")
        # tRNS - after PLTE, before IDAT
        assert chunks.index(b"tRNS") > chunks.index(b"PLTE")
        assert chunks.index(b"tRNS") < chunks.index(b"IDAT")
        # pHYs - before IDAT
        assert chunks.index(b"pHYs") < chunks.index(b"IDAT")

    def test_getchunks(self):
        im = hopper()

        chunks = PngImagePlugin.getchunks(im)
        assert len(chunks) == 3

    def test_textual_chunks_after_idat(self):
        with Image.open("Tests/images/hopper.png") as im:
            assert "comment" in im.text.keys()
            for k, v in {
                "date:create": "2014-09-04T09:37:08+03:00",
                "date:modify": "2014-09-04T09:37:08+03:00",
            }.items():
                assert im.text[k] == v

        # Raises a SyntaxError in load_end
        with Image.open("Tests/images/broken_data_stream.png") as im:
            with pytest.raises(IOError):
                assert isinstance(im.text, dict)

        # Raises a UnicodeDecodeError in load_end
        with Image.open("Tests/images/truncated_image.png") as im:
            # The file is truncated
            with pytest.raises(IOError):
                im.text()
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            assert isinstance(im.text, dict)
            ImageFile.LOAD_TRUNCATED_IMAGES = False

        # Raises an EOFError in load_end
        with Image.open("Tests/images/hopper_idat_after_image_end.png") as im:
            assert im.text == {"TXT": "VALUE", "ZIP": "VALUE"}

    def test_exif(self):
        with Image.open("Tests/images/exif.png") as im:
            exif = im._getexif()
        assert exif[274] == 1

    def test_exif_save(self):
        with Image.open("Tests/images/exif.png") as im:
            test_file = self.tempfile("temp.png")
            im.save(test_file)

        with Image.open(test_file) as reloaded:
            exif = reloaded._getexif()
        assert exif[274] == 1

    def test_exif_from_jpg(self):
        with Image.open("Tests/images/pil_sample_rgb.jpg") as im:
            test_file = self.tempfile("temp.png")
            im.save(test_file)

        with Image.open(test_file) as reloaded:
            exif = reloaded._getexif()
        assert exif[305] == "Adobe Photoshop CS Macintosh"

    def test_exif_argument(self):
        with Image.open(TEST_PNG_FILE) as im:
            test_file = self.tempfile("temp.png")
            im.save(test_file, exif=b"exifstring")

        with Image.open(test_file) as reloaded:
            assert reloaded.info["exif"] == b"Exif\x00\x00exifstring"

    # APNG browser support tests and fixtures via:
    # https://philip.html5.org/tests/apng/tests.html
    # (referenced from https://wiki.mozilla.org/APNG_Specification)
    def test_apng_basic(self):
        im = Image.open("Tests/images/apng/single_frame.png")
        self.assertTrue(im.is_animated)
        self.assertEqual(im.get_format_mimetype(), "image/apng")
        self.assertIsNone(im.info.get("default_image"))
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        im = Image.open("Tests/images/apng/single_frame_default.png")
        self.assertTrue(im.is_animated)
        self.assertEqual(im.get_format_mimetype(), "image/apng")
        self.assertTrue(im.info.get("default_image"))
        self.assertEqual(im.getpixel((0, 0)), (255, 0, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (255, 0, 0, 255))
        im.seek(1)
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        # test out of bounds seek
        with self.assertRaises(EOFError):
            im.seek(2)

        # test rewind support
        im.seek(0)
        self.assertEqual(im.getpixel((0, 0)), (255, 0, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (255, 0, 0, 255))
        im.seek(1)
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

    def test_apng_fdat(self):
        im = Image.open("Tests/images/apng/split_fdat.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        im = Image.open("Tests/images/apng/split_fdat_zero_chunk.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

    def test_apng_dispose(self):
        im = Image.open("Tests/images/apng/dispose_op_none.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        im = Image.open("Tests/images/apng/dispose_op_background.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 0, 0, 0))
        self.assertEqual(im.getpixel((64, 32)), (0, 0, 0, 0))

        im = Image.open("Tests/images/apng/dispose_op_background_final.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        im = Image.open("Tests/images/apng/dispose_op_previous.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        im = Image.open("Tests/images/apng/dispose_op_previous_final.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        im = Image.open("Tests/images/apng/dispose_op_previous_first.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 0, 0, 0))
        self.assertEqual(im.getpixel((64, 32)), (0, 0, 0, 0))

    def test_apng_dispose_region(self):
        im = Image.open("Tests/images/apng/dispose_op_none_region.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        im = Image.open("Tests/images/apng/dispose_op_background_before_region.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 0, 0, 0))
        self.assertEqual(im.getpixel((64, 32)), (0, 0, 0, 0))

        im = Image.open("Tests/images/apng/dispose_op_background_region.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 0, 255, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 0, 0, 0))

        im = Image.open("Tests/images/apng/dispose_op_previous_region.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

    def test_apng_blend(self):
        im = Image.open("Tests/images/apng/blend_op_source_solid.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        im = Image.open("Tests/images/apng/blend_op_source_transparent.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 0, 0, 0))
        self.assertEqual(im.getpixel((64, 32)), (0, 0, 0, 0))

        im = Image.open("Tests/images/apng/blend_op_source_near_transparent.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 2))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 2))

        im = Image.open("Tests/images/apng/blend_op_over.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        im = Image.open("Tests/images/apng/blend_op_over_near_transparent.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 97))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

    def test_apng_chunk_order(self):
        im = Image.open("Tests/images/apng/fctl_actl.png")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

    def test_apng_delay(self):
        im = Image.open("Tests/images/apng/delay.png")
        im.seek(1)
        self.assertEqual(im.info.get("duration"), 500.0)
        im.seek(2)
        self.assertEqual(im.info.get("duration"), 1000.0)
        im.seek(3)
        self.assertEqual(im.info.get("duration"), 500.0)
        im.seek(4)
        self.assertEqual(im.info.get("duration"), 1000.0)

        im = Image.open("Tests/images/apng/delay_round.png")
        im.seek(1)
        self.assertEqual(im.info.get("duration"), 500.0)
        im.seek(2)
        self.assertEqual(im.info.get("duration"), 1000.0)

        im = Image.open("Tests/images/apng/delay_short_max.png")
        im.seek(1)
        self.assertEqual(im.info.get("duration"), 500.0)
        im.seek(2)
        self.assertEqual(im.info.get("duration"), 1000.0)

        im = Image.open("Tests/images/apng/delay_zero_denom.png")
        im.seek(1)
        self.assertEqual(im.info.get("duration"), 500.0)
        im.seek(2)
        self.assertEqual(im.info.get("duration"), 1000.0)

        im = Image.open("Tests/images/apng/delay_zero_numer.png")
        im.seek(1)
        self.assertEqual(im.info.get("duration"), 0.0)
        im.seek(2)
        self.assertEqual(im.info.get("duration"), 0.0)
        im.seek(3)
        self.assertEqual(im.info.get("duration"), 500.0)
        im.seek(4)
        self.assertEqual(im.info.get("duration"), 1000.0)

    def test_apng_num_plays(self):
        im = Image.open("Tests/images/apng/num_plays.png")
        self.assertEqual(im.info.get("loop"), 0)

        im = Image.open("Tests/images/apng/num_plays_1.png")
        self.assertEqual(im.info.get("loop"), 1)

    def test_apng_mode(self):
        im = Image.open("Tests/images/apng/mode_16bit.png")
        self.assertEqual(im.mode, "RGBA")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (0, 0, 128, 191))
        self.assertEqual(im.getpixel((64, 32)), (0, 0, 128, 191))

        im = Image.open("Tests/images/apng/mode_greyscale.png")
        self.assertEqual(im.mode, "L")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), 128)
        self.assertEqual(im.getpixel((64, 32)), 255)

        im = Image.open("Tests/images/apng/mode_greyscale_alpha.png")
        self.assertEqual(im.mode, "LA")
        im.seek(im.n_frames - 1)
        self.assertEqual(im.getpixel((0, 0)), (128, 191))
        self.assertEqual(im.getpixel((64, 32)), (128, 191))

        im = Image.open("Tests/images/apng/mode_palette.png")
        self.assertEqual(im.mode, "P")
        im.seek(im.n_frames - 1)
        im = im.convert("RGB")
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0))

        im = Image.open("Tests/images/apng/mode_palette_alpha.png")
        self.assertEqual(im.mode, "P")
        im.seek(im.n_frames - 1)
        im = im.convert("RGBA")
        self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        im = Image.open("Tests/images/apng/mode_palette_1bit_alpha.png")
        self.assertEqual(im.mode, "P")
        im.seek(im.n_frames - 1)
        im = im.convert("RGBA")
        self.assertEqual(im.getpixel((0, 0)), (0, 0, 255, 128))
        self.assertEqual(im.getpixel((64, 32)), (0, 0, 255, 128))

    def test_apng_chunk_errors(self):
        im = Image.open("Tests/images/apng/chunk_no_actl.png")
        self.assertFalse(im.is_animated)

        def open():
            im = Image.open("Tests/images/apng/chunk_multi_actl.png")
            im.load()

        pytest.warns(UserWarning, open)
        self.assertFalse(im.is_animated)

        im = Image.open("Tests/images/apng/chunk_actl_after_idat.png")
        self.assertFalse(im.is_animated)

        im = Image.open("Tests/images/apng/chunk_no_fctl.png")
        with self.assertRaises(SyntaxError):
            im.seek(im.n_frames - 1)

        im = Image.open("Tests/images/apng/chunk_repeat_fctl.png")
        with self.assertRaises(SyntaxError):
            im.seek(im.n_frames - 1)

        im = Image.open("Tests/images/apng/chunk_no_fdat.png")
        with self.assertRaises(SyntaxError):
            im.seek(im.n_frames - 1)

    def test_apng_syntax_errors(self):
        def open():
            im = Image.open("Tests/images/apng/syntax_num_frames_zero.png")
            self.assertFalse(im.is_animated)
            with self.assertRaises(OSError):
                im.load()

        pytest.warns(UserWarning, open)

        def open():
            im = Image.open("Tests/images/apng/syntax_num_frames_zero_default.png")
            self.assertFalse(im.is_animated)
            im.load()

        pytest.warns(UserWarning, open)

        # we can handle this case gracefully
        exception = None
        im = Image.open("Tests/images/apng/syntax_num_frames_low.png")
        try:
            im.seek(im.n_frames - 1)
        except Exception as e:
            exception = e
        self.assertIsNone(exception)

        with self.assertRaises(SyntaxError):
            im = Image.open("Tests/images/apng/syntax_num_frames_high.png")
            im.seek(im.n_frames - 1)
            im.load()

        def open():
            im = Image.open("Tests/images/apng/syntax_num_frames_invalid.png")
            self.assertFalse(im.is_animated)
            im.load()

        pytest.warns(UserWarning, open)

    def test_apng_sequence_errors(self):
        test_files = [
            "sequence_start.png",
            "sequence_gap.png",
            "sequence_repeat.png",
            "sequence_repeat_chunk.png",
            "sequence_reorder.png",
            "sequence_reorder_chunk.png",
            "sequence_fdat_fctl.png",
        ]
        for f in test_files:
            with self.assertRaises(SyntaxError):
                im = Image.open("Tests/images/apng/{0}".format(f))
                im.seek(im.n_frames - 1)
                im.load()

    def test_apng_save(self):
        im = Image.open("Tests/images/apng/single_frame.png")
        test_file = self.tempfile("temp.png")
        im.save(test_file, save_all=True)

        with Image.open(test_file) as im:
            im.load()
            self.assertTrue(im.is_animated)
            self.assertEqual(im.get_format_mimetype(), "image/apng")
            self.assertIsNone(im.info.get("default_image"))
            self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
            self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        im = Image.open("Tests/images/apng/single_frame_default.png")
        frames = []
        for im in ImageSequence.Iterator(im):
            frames.append(im.copy())
        frames[0].save(
            test_file, save_all=True, default_image=True, append_images=frames[1:]
        )

        with Image.open(test_file) as im:
            im.load()
            self.assertTrue(im.is_animated)
            self.assertEqual(im.get_format_mimetype(), "image/apng")
            self.assertTrue(im.info.get("default_image"))
            im.seek(1)
            self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
            self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

    def test_apng_save_split_fdat(self):
        # test to make sure we do not generate sequence errors when writing
        # frames with image data spanning multiple fdAT chunks (in this case
        # both the default image and first animation frame will span multiple
        # data chunks)
        test_file = self.tempfile("temp.png")
        with Image.open("Tests/images/old-style-jpeg-compression.png") as im:
            frames = [im.copy(), Image.new("RGBA", im.size, (255, 0, 0, 255))]
            im.save(
                test_file,
                save_all=True,
                default_image=True,
                append_images=frames,
            )
        with Image.open(test_file) as im:
            exception = None
            try:
                im.seek(im.n_frames - 1)
                im.load()
            except Exception as e:
                exception = e
            self.assertIsNone(exception)

    def test_apng_save_duration_loop(self):
        test_file = self.tempfile("temp.png")
        im = Image.open("Tests/images/apng/delay.png")
        frames = []
        durations = []
        loop = im.info.get("loop")
        default_image = im.info.get("default_image")
        for i, im in enumerate(ImageSequence.Iterator(im)):
            frames.append(im.copy())
            if i != 0 or not default_image:
                durations.append(im.info.get("duration", 0))
        frames[0].save(
            test_file,
            save_all=True,
            default_image=default_image,
            append_images=frames[1:],
            duration=durations,
            loop=loop,
        )
        with Image.open(test_file) as im:
            im.load()
            self.assertEqual(im.info.get("loop"), loop)
            im.seek(1)
            self.assertEqual(im.info.get("duration"), 500.0)
            im.seek(2)
            self.assertEqual(im.info.get("duration"), 1000.0)
            im.seek(3)
            self.assertEqual(im.info.get("duration"), 500.0)
            im.seek(4)
            self.assertEqual(im.info.get("duration"), 1000.0)

        # test removal of duplicated frames
        frame = Image.new("RGBA", (128, 64), (255, 0, 0, 255))
        frame.save(test_file, save_all=True, append_images=[frame], duration=[500, 250])
        with Image.open(test_file) as im:
            im.load()
            self.assertEqual(im.n_frames, 1)
            self.assertEqual(im.info.get("duration"), 750)

            # This also tests reading unknown PNG chunks (fcTL and fdAT) in load_end
            with Image.open("Tests/images/iss634.webp") as expected:
                assert_image_similar(im, expected, 0.23)

    def test_apng_save_disposal(self):
        test_file = self.tempfile("temp.png")
        size = (128, 64)
        red = Image.new("RGBA", size, (255, 0, 0, 255))
        green = Image.new("RGBA", size, (0, 255, 0, 255))
        transparent = Image.new("RGBA", size, (0, 0, 0, 0))

        # test APNG_DISPOSE_OP_NONE
        red.save(
            test_file,
            save_all=True,
            append_images=[green, transparent],
            disposal=PngImagePlugin.APNG_DISPOSE_OP_NONE,
            blend=PngImagePlugin.APNG_BLEND_OP_OVER,
        )
        with Image.open(test_file) as im:
            im.seek(2)
            self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
            self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        # test APNG_DISPOSE_OP_BACKGROUND
        disposal = [
            PngImagePlugin.APNG_DISPOSE_OP_NONE,
            PngImagePlugin.APNG_DISPOSE_OP_BACKGROUND,
            PngImagePlugin.APNG_DISPOSE_OP_NONE,
        ]
        red.save(
            test_file,
            save_all=True,
            append_images=[red, transparent],
            disposal=disposal,
            blend=PngImagePlugin.APNG_BLEND_OP_OVER,
        )
        with Image.open(test_file) as im:
            im.seek(2)
            self.assertEqual(im.getpixel((0, 0)), (0, 0, 0, 0))
            self.assertEqual(im.getpixel((64, 32)), (0, 0, 0, 0))

        disposal = [
            PngImagePlugin.APNG_DISPOSE_OP_NONE,
            PngImagePlugin.APNG_DISPOSE_OP_BACKGROUND,
        ]
        red.save(
            test_file,
            save_all=True,
            append_images=[green],
            disposal=disposal,
            blend=PngImagePlugin.APNG_BLEND_OP_OVER,
        )
        with Image.open(test_file) as im:
            im.seek(1)
            self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
            self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        # test APNG_DISPOSE_OP_PREVIOUS
        disposal = [
            PngImagePlugin.APNG_DISPOSE_OP_NONE,
            PngImagePlugin.APNG_DISPOSE_OP_PREVIOUS,
            PngImagePlugin.APNG_DISPOSE_OP_NONE,
        ]
        red.save(
            test_file,
            save_all=True,
            append_images=[green, red, transparent],
            default_image=True,
            disposal=disposal,
            blend=PngImagePlugin.APNG_BLEND_OP_OVER,
        )
        with Image.open(test_file) as im:
            im.seek(3)
            self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
            self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        disposal = [
            PngImagePlugin.APNG_DISPOSE_OP_NONE,
            PngImagePlugin.APNG_DISPOSE_OP_PREVIOUS,
        ]
        red.save(
            test_file,
            save_all=True,
            append_images=[green],
            disposal=disposal,
            blend=PngImagePlugin.APNG_BLEND_OP_OVER,
        )
        with Image.open(test_file) as im:
            im.seek(1)
            self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
            self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

    def test_apng_save_blend(self):
        test_file = self.tempfile("temp.png")
        size = (128, 64)
        red = Image.new("RGBA", size, (255, 0, 0, 255))
        green = Image.new("RGBA", size, (0, 255, 0, 255))
        transparent = Image.new("RGBA", size, (0, 0, 0, 0))

        # test APNG_BLEND_OP_SOURCE on solid color
        blend = [
            PngImagePlugin.APNG_BLEND_OP_OVER,
            PngImagePlugin.APNG_BLEND_OP_SOURCE,
        ]
        red.save(
            test_file,
            save_all=True,
            append_images=[red, green],
            default_image=True,
            disposal=PngImagePlugin.APNG_DISPOSE_OP_NONE,
            blend=blend,
        )
        with Image.open(test_file) as im:
            im.seek(2)
            self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
            self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))

        # test APNG_BLEND_OP_SOURCE on transparent color
        blend = [
            PngImagePlugin.APNG_BLEND_OP_OVER,
            PngImagePlugin.APNG_BLEND_OP_SOURCE,
        ]
        red.save(
            test_file,
            save_all=True,
            append_images=[red, transparent],
            default_image=True,
            disposal=PngImagePlugin.APNG_DISPOSE_OP_NONE,
            blend=blend,
        )
        with Image.open(test_file) as im:
            im.seek(2)
            self.assertEqual(im.getpixel((0, 0)), (0, 0, 0, 0))
            self.assertEqual(im.getpixel((64, 32)), (0, 0, 0, 0))

        # test APNG_BLEND_OP_OVER
        red.save(
            test_file,
            save_all=True,
            append_images=[green, transparent],
            default_image=True,
            disposal=PngImagePlugin.APNG_DISPOSE_OP_NONE,
            blend=PngImagePlugin.APNG_BLEND_OP_OVER,
        )
        with Image.open(test_file) as im:
            im.seek(1)
            self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
            self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))
            im.seek(2)
            self.assertEqual(im.getpixel((0, 0)), (0, 255, 0, 255))
            self.assertEqual(im.getpixel((64, 32)), (0, 255, 0, 255))


@unittest.skipIf(is_win32(), "requires Unix or macOS")
@skip_unless_feature("zlib")
class TestTruncatedPngPLeaks(PillowLeakTestCase):
    mem_limit = 2 * 1024  # max increase in K
    iterations = 100  # Leak is 56k/iteration, this will leak 5.6megs

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
