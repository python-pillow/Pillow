from PIL import FontFile, Image, ImageDraw, ImageFont, PcfFontFile

from .helper import PillowTestCase

codecs = dir(Image.core)

fontname = "Tests/fonts/10x20-ISO8859-1.pcf"

message = "hello, world"


class TestFontPcf(PillowTestCase):
    def setUp(self):
        if "zip_encoder" not in codecs or "zip_decoder" not in codecs:
            self.skipTest("zlib support not available")

    def save_font(self):
        with open(fontname, "rb") as test_file:
            font = PcfFontFile.PcfFontFile(test_file)
        self.assertIsInstance(font, FontFile.FontFile)
        # check the number of characters in the font
        self.assertEqual(len([_f for _f in font.glyph if _f]), 223)

        tempname = self.tempfile("temp.pil")
        self.addCleanup(self.delete_tempfile, tempname[:-4] + ".pbm")
        font.save(tempname)

        with Image.open(tempname.replace(".pil", ".pbm")) as loaded:
            with Image.open("Tests/fonts/10x20.pbm") as target:
                self.assert_image_equal(loaded, target)

        with open(tempname, "rb") as f_loaded:
            with open("Tests/fonts/10x20.pil", "rb") as f_target:
                self.assertEqual(f_loaded.read(), f_target.read())
        return tempname

    def test_sanity(self):
        self.save_font()

    def test_invalid_file(self):
        with open("Tests/images/flower.jpg", "rb") as fp:
            self.assertRaises(SyntaxError, PcfFontFile.PcfFontFile, fp)

    def test_draw(self):
        tempname = self.save_font()
        font = ImageFont.load(tempname)
        im = Image.new("L", (130, 30), "white")
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), message, "black", font=font)
        with Image.open("Tests/images/test_draw_pbm_target.png") as target:
            self.assert_image_similar(im, target, 0)

    def test_textsize(self):
        tempname = self.save_font()
        font = ImageFont.load(tempname)
        for i in range(255):
            (dx, dy) = font.getsize(chr(i))
            self.assertEqual(dy, 20)
            self.assertIn(dx, (0, 10))
        for l in range(len(message)):
            msg = message[: l + 1]
            self.assertEqual(font.getsize(msg), (len(msg) * 10, 20))

    def _test_high_characters(self, message):
        tempname = self.save_font()
        font = ImageFont.load(tempname)
        im = Image.new("L", (750, 30), "white")
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), message, "black", font=font)
        with Image.open("Tests/images/high_ascii_chars.png") as target:
            self.assert_image_similar(im, target, 0)

    def test_high_characters(self):
        message = "".join(chr(i + 1) for i in range(140, 232))
        self._test_high_characters(message)
        # accept bytes instances.
        self._test_high_characters(message.encode("latin1"))
