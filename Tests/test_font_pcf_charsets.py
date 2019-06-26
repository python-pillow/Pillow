# -*- coding: UTF-8 -*-
from .helper import PillowTestCase

from PIL import Image, FontFile, PcfFontFile
from PIL import ImageFont, ImageDraw

# from PIL._util import py3

codecs = dir(Image.core)

fontname = "Tests/fonts/ter-x20b.pcf"

charsets = {
    "iso8859-1": {
        "glyph_count": 223,
        "message": u"hello, world",
        "image1": "Tests/images/test_draw_pbm_ter_en_target.png",
    },
    "iso8859-2": {
        "glyph_count": 223,
        "message": u"witaj świecie",
        "image1": "Tests/images/test_draw_pbm_ter_pl_target.png",
    },
    "cp1250": {
        "glyph_count": 250,
        "message": u"witaj świecie",
        "image1": "Tests/images/test_draw_pbm_ter_pl_target.png",
    },
}


class TestFontPcf(PillowTestCase):
    def setUp(self):
        if "zip_encoder" not in codecs or "zip_decoder" not in codecs:
            self.skipTest("zlib support not available")

    def save_font(self, encoding):
        with open(fontname, "rb") as test_file:
            font = PcfFontFile.PcfFontFile(test_file, encoding)
        self.assertIsInstance(font, FontFile.FontFile)
        # check the number of characters in the font
        self.assertEqual(
            len([_f for _f in font.glyph if _f]), charsets[encoding]["glyph_count"]
        )

        tempname = self.tempfile("temp.pil")
        self.addCleanup(self.delete_tempfile, tempname[:-4] + ".pbm")
        font.save(tempname)

        with Image.open(tempname.replace(".pil", ".pbm")) as loaded:
            with Image.open("Tests/fonts/ter-x20b-%s.pbm" % encoding) as target:
                self.assert_image_equal(loaded, target)

        with open(tempname, "rb") as f_loaded:
            with open("Tests/fonts/ter-x20b-%s.pil" % encoding, "rb") as f_target:
                self.assertEqual(f_loaded.read(), f_target.read())
        return tempname

    def _test_sanity(self, encoding):
        self.save_font(encoding)

    def test_sanity_iso8859_1(self):
        self._test_sanity("iso8859-1")

    def test_sanity_iso8859_2(self):
        self._test_sanity("iso8859-2")

    def test_sanity_cp1250(self):
        self._test_sanity("cp1250")

    # def test_invalid_file(self):
    #     with open("Tests/images/flower.jpg", "rb") as fp:
    #         self.assertRaises(SyntaxError, PcfFontFile.PcfFontFile, fp)

    def _test_draw(self, encoding):
        tempname = self.save_font(encoding)
        font = ImageFont.load(tempname)
        im = Image.new("L", (150, 30), "white")
        draw = ImageDraw.Draw(im)
        message = charsets[encoding]["message"].encode(encoding)
        draw.text((0, 0), message, "black", font=font)
        with Image.open(charsets[encoding]["image1"]) as target:
            self.assert_image_similar(im, target, 0)

    def test_draw_iso8859_1(self):
        self._test_draw("iso8859-1")

    def test_draw_iso8859_2(self):
        self._test_draw("iso8859-2")

    def test_draw_cp1250(self):
        self._test_draw("cp1250")

    def _test_textsize(self, encoding):
        tempname = self.save_font(encoding)
        font = ImageFont.load(tempname)
        for i in range(255):
            (dx, dy) = font.getsize(bytearray([i]))
            self.assertEqual(dy, 20)
            self.assertIn(dx, (0, 10))
        message = charsets[encoding]["message"].encode(encoding)
        for l in range(len(message)):
            msg = message[: l + 1]
            self.assertEqual(font.getsize(msg), (len(msg) * 10, 20))

    def test_textsize_iso8859_1(self):
        self._test_textsize("iso8859-1")

    def test_textsize_iso8859_2(self):
        self._test_textsize("iso8859-2")

    def test_textsize_cp1250(self):
        self._test_textsize("cp1250")

    # def _test_high_characters(self, message, encoding):
    #     tempname = self.save_font(encoding)
    #     font = ImageFont.load(tempname)
    #     im = Image.new("L", (750, 30), "white")
    #     draw = ImageDraw.Draw(im)
    #     draw.text((0, 0), message, "black", font=font)
    #     with Image.open("Tests/images/high_ascii_chars.png") as target:
    #         self.assert_image_similar(im, target, 0)
    #
    # def test_high_characters(self):
    #     message = "".join(chr(i + 1) for i in range(140, 232))
    #     self._test_high_characters(message)
    #     # accept bytes instances in Py3.
    #     if py3:
    #         self._test_high_characters(message.encode("latin1"))
