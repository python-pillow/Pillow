from helper import unittest, PillowTestCase, hopper

from io import BytesIO

from PIL import Image
from PIL import PngImagePlugin
import zlib

codecs = dir(Image.core)

# sample png stream

TEST_PNG_FILE = "Tests/images/hopper.png"
TEST_DATA = open(TEST_PNG_FILE, "rb").read()

# stuff to create inline PNG images

MAGIC = PngImagePlugin._MAGIC


def chunk(cid, *data):
    test_file = BytesIO()
    PngImagePlugin.putchunk(*(test_file, cid) + data)
    return test_file.getvalue()

o32 = PngImagePlugin.o32

IHDR = chunk(b"IHDR", o32(1), o32(1), b'\x08\x02', b'\0\0\0')
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

    def test_sanity(self):

        # internal version number
        self.assertRegexpMatches(
            Image.core.zlib_version, "\d+\.\d+\.\d+(\.\d+)?$")

        test_file = self.tempfile("temp.png")

        hopper("RGB").save(test_file)

        im = Image.open(test_file)
        im.load()
        self.assertEqual(im.mode, "RGB")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "PNG")

        hopper("1").save(test_file)
        im = Image.open(test_file)

        hopper("L").save(test_file)
        im = Image.open(test_file)

        hopper("P").save(test_file)
        im = Image.open(test_file)

        hopper("RGB").save(test_file)
        im = Image.open(test_file)

        hopper("I").save(test_file)
        im = Image.open(test_file)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda: PngImagePlugin.PngImageFile(invalid_file))

    def test_broken(self):
        # Check reading of totally broken files.  In this case, the test
        # file was checked into Subversion as a text file.

        test_file = "Tests/images/broken.png"
        self.assertRaises(IOError, lambda: Image.open(test_file))

    def test_bad_text(self):
        # Make sure PIL can read malformed tEXt chunks (@PIL152)

        im = load(HEAD + chunk(b'tEXt') + TAIL)
        self.assertEqual(im.info, {})

        im = load(HEAD + chunk(b'tEXt', b'spam') + TAIL)
        self.assertEqual(im.info, {'spam': ''})

        im = load(HEAD + chunk(b'tEXt', b'spam\0') + TAIL)
        self.assertEqual(im.info, {'spam': ''})

        im = load(HEAD + chunk(b'tEXt', b'spam\0egg') + TAIL)
        self.assertEqual(im.info, {'spam': 'egg'})

        im = load(HEAD + chunk(b'tEXt', b'spam\0egg\0') + TAIL)
        self.assertEqual(im.info,  {'spam': 'egg\x00'})

    def test_bad_ztxt(self):
        # Test reading malformed zTXt chunks (python-pillow/Pillow#318)

        im = load(HEAD + chunk(b'zTXt') + TAIL)
        self.assertEqual(im.info, {})

        im = load(HEAD + chunk(b'zTXt', b'spam') + TAIL)
        self.assertEqual(im.info, {'spam': ''})

        im = load(HEAD + chunk(b'zTXt', b'spam\0') + TAIL)
        self.assertEqual(im.info, {'spam': ''})

        im = load(HEAD + chunk(b'zTXt', b'spam\0\0') + TAIL)
        self.assertEqual(im.info, {'spam': ''})

        im = load(HEAD + chunk(
            b'zTXt', b'spam\0\0' + zlib.compress(b'egg')[:1]) + TAIL)
        self.assertEqual(im.info, {'spam': ''})

        im = load(
            HEAD + chunk(b'zTXt', b'spam\0\0' + zlib.compress(b'egg')) + TAIL)
        self.assertEqual(im.info,  {'spam': 'egg'})

    def test_bad_itxt(self):

        im = load(HEAD + chunk(b'iTXt') + TAIL)
        self.assertEqual(im.info, {})

        im = load(HEAD + chunk(b'iTXt', b'spam') + TAIL)
        self.assertEqual(im.info, {})

        im = load(HEAD + chunk(b'iTXt', b'spam\0') + TAIL)
        self.assertEqual(im.info, {})

        im = load(HEAD + chunk(b'iTXt', b'spam\0\x02') + TAIL)
        self.assertEqual(im.info, {})

        im = load(HEAD + chunk(b'iTXt', b'spam\0\0\0foo\0') + TAIL)
        self.assertEqual(im.info, {})

        im = load(HEAD + chunk(b'iTXt', b'spam\0\0\0en\0Spam\0egg') + TAIL)
        self.assertEqual(im.info, {"spam": "egg"})
        self.assertEqual(im.info["spam"].lang, "en")
        self.assertEqual(im.info["spam"].tkey, "Spam")

        im = load(HEAD + chunk(b'iTXt', b'spam\0\1\0en\0Spam\0' +
                               zlib.compress(b"egg")[:1]) + TAIL)
        self.assertEqual(im.info, {'spam': ''})

        im = load(HEAD + chunk(b'iTXt', b'spam\0\1\1en\0Spam\0' +
                               zlib.compress(b"egg")) + TAIL)
        self.assertEqual(im.info, {})

        im = load(HEAD + chunk(b'iTXt', b'spam\0\1\0en\0Spam\0' +
                               zlib.compress(b"egg")) + TAIL)
        self.assertEqual(im.info, {"spam": "egg"})
        self.assertEqual(im.info["spam"].lang, "en")
        self.assertEqual(im.info["spam"].tkey, "Spam")

    def test_interlace(self):

        test_file = "Tests/images/pil123p.png"
        im = Image.open(test_file)

        self.assert_image(im, "P", (162, 150))
        self.assertTrue(im.info.get("interlace"))

        im.load()

        test_file = "Tests/images/pil123rgba.png"
        im = Image.open(test_file)

        self.assert_image(im, "RGBA", (162, 150))
        self.assertTrue(im.info.get("interlace"))

        im.load()

    def test_load_transparent_p(self):
        test_file = "Tests/images/pil123p.png"
        im = Image.open(test_file)

        self.assert_image(im, "P", (162, 150))
        im = im.convert("RGBA")
        self.assert_image(im, "RGBA", (162, 150))

        # image has 124 uniqe qlpha values
        self.assertEqual(len(im.split()[3].getcolors()), 124)

    def test_load_transparent_rgb(self):
        test_file = "Tests/images/rgb_trns.png"
        im = Image.open(test_file)

        self.assert_image(im, "RGB", (64, 64))
        im = im.convert("RGBA")
        self.assert_image(im, "RGBA", (64, 64))

        # image has 876 transparent pixels
        self.assertEqual(im.split()[3].getcolors()[0][0], 876)

    def test_save_p_transparent_palette(self):
        in_file = "Tests/images/pil123p.png"
        im = Image.open(in_file)

        test_file = self.tempfile("temp.png")
        im.save(test_file)

    def test_save_p_single_transparency(self):
        in_file = "Tests/images/p_trns_single.png"
        im = Image.open(in_file)

        test_file = self.tempfile("temp.png")
        im.save(test_file)

    def test_save_l_transparency(self):
        in_file = "Tests/images/l_trns.png"
        im = Image.open(in_file)

        test_file = self.tempfile("temp.png")
        im.save(test_file)

        # There are 559 transparent pixels.
        im = im.convert('RGBA')
        self.assertEqual(im.split()[3].getcolors()[0][0], 559)

    def test_save_rgb_single_transparency(self):
        in_file = "Tests/images/caption_6_33_22.png"
        im = Image.open(in_file)

        test_file = self.tempfile("temp.png")
        im.save(test_file)

    def test_load_verify(self):
        # Check open/load/verify exception (@PIL150)

        im = Image.open(TEST_PNG_FILE)
        im.verify()

        im = Image.open(TEST_PNG_FILE)
        im.load()
        self.assertRaises(RuntimeError, im.verify)

    def test_roundtrip_dpi(self):
        # Check dpi roundtripping

        im = Image.open(TEST_PNG_FILE)

        im = roundtrip(im, dpi=(100, 100))
        self.assertEqual(im.info["dpi"], (100, 100))

    def test_roundtrip_text(self):
        # Check text roundtripping

        im = Image.open(TEST_PNG_FILE)

        info = PngImagePlugin.PngInfo()
        info.add_text("TXT", "VALUE")
        info.add_text("ZIP", "VALUE", 1)

        im = roundtrip(im, pnginfo=info)
        self.assertEqual(im.info, {'TXT': 'VALUE', 'ZIP': 'VALUE'})
        self.assertEqual(im.text, {'TXT': 'VALUE', 'ZIP': 'VALUE'})

    def test_roundtrip_itxt(self):
        # Check iTXt roundtripping

        im = Image.new("RGB", (32, 32))
        info = PngImagePlugin.PngInfo()
        info.add_itxt("spam", "Eggs", "en", "Spam")
        info.add_text("eggs", PngImagePlugin.iTXt("Spam", "en", "Eggs"),
                      zip=True)

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
        self.assertEqual(type(im.info["Text"]), str)

    def test_unicode_text(self):
        # Check preservation of non-ASCII characters on Python3
        # This cannot really be meaningfully tested on Python2,
        # since it didn't preserve charsets to begin with.

        def rt_text(value):
            im = Image.new("RGB", (32, 32))
            info = PngImagePlugin.PngInfo()
            info.add_text("Text", value)
            im = roundtrip(im, pnginfo=info)
            self.assertEqual(im.info, {"Text": value})

        if str is not bytes:
            rt_text(" Aa" + chr(0xa0) + chr(0xc4) + chr(0xff))  # Latin1
            rt_text(chr(0x400) + chr(0x472) + chr(0x4ff))       # Cyrillic
            rt_text(chr(0x4e00) + chr(0x66f0) +                 # CJK
                    chr(0x9fba) + chr(0x3042) + chr(0xac00))
            rt_text("A" + chr(0xc4) + chr(0x472) + chr(0x3042))  # Combined

    def test_scary(self):
        # Check reading of evil PNG file.  For information, see:
        # http://scary.beasts.org/security/CESA-2004-001.txt
        # The first byte is removed from pngtest_bad.png
        # to avoid classification as malware.

        with open("Tests/images/pngtest_bad.png.bin", 'rb') as fd:
            data = b'\x89' + fd.read()

        pngfile = BytesIO(data)
        self.assertRaises(IOError, lambda: Image.open(pngfile))

    def test_trns_rgb(self):
        # Check writing and reading of tRNS chunks for RGB images.
        # Independent file sample provided by Sebastian Spaeth.

        test_file = "Tests/images/caption_6_33_22.png"
        im = Image.open(test_file)
        self.assertEqual(im.info["transparency"], (248, 248, 248))

        # check saving transparency by default
        im = roundtrip(im)
        self.assertEqual(im.info["transparency"], (248, 248, 248))

        im = roundtrip(im, transparency=(0, 1, 2))
        self.assertEqual(im.info["transparency"], (0, 1, 2))

    def test_trns_p(self):
        # Check writing a transparency of 0, issue #528
        im = hopper('P')
        im.info['transparency'] = 0

        f = self.tempfile("temp.png")
        im.save(f)

        im2 = Image.open(f)
        self.assertIn('transparency', im2.info)

        self.assert_image_equal(im2.convert('RGBA'),
                                im.convert('RGBA'))

    def test_trns_null(self):
        # Check reading images with null tRNS value, issue #1239
        test_file = "Tests/images/tRNS_null_1x1.png"
        im = Image.open(test_file)

        self.assertEqual(im.info["transparency"], 0)

    def test_save_icc_profile_none(self):
        # check saving files with an ICC profile set to None (omit profile)
        in_file = "Tests/images/icc_profile_none.png"
        im = Image.open(in_file)
        self.assertEqual(im.info['icc_profile'], None)

        im = roundtrip(im)
        self.assertNotIn('icc_profile', im.info)

    def test_roundtrip_icc_profile(self):
        # check that we can roundtrip the icc profile
        im = hopper('RGB')

        jpeg_image = Image.open('Tests/images/flower2.jpg')
        expected_icc = jpeg_image.info['icc_profile']

        im.info['icc_profile'] = expected_icc
        im = roundtrip(im)
        self.assertEqual(im.info['icc_profile'], expected_icc)

    def test_repr_png(self):
        im = hopper()

        repr_png = Image.open(BytesIO(im._repr_png_()))
        self.assertEqual(repr_png.format, 'PNG')
        self.assert_image_equal(im, repr_png)


if __name__ == '__main__':
    unittest.main()

# End of file
