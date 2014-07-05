from helper import unittest, PillowTestCase, tearDownModule

from PIL import Image, FontFile, PcfFontFile
from PIL import ImageFont, ImageDraw

CODECS = dir(Image.core)

FONTNAME = "Tests/fonts/helvO18.pcf"

MESSAGE = "hello, world"


class TestFontPcf(PillowTestCase):

    def setUp(self):
        if "zip_encoder" not in CODECS or "zip_decoder" not in CODECS:
            self.skipTest("zlib support not available")

    def open_font(self):
        file = open(FONTNAME, "rb")
        font = PcfFontFile.PcfFontFile(file)
        self.assertIsInstance(font, FontFile.FontFile)
        self.assertEqual(len([_f for _f in font.glyph if _f]), 192)
        return font

    def get_tempname(self):
        tempname = self.tempfile("temp.pil")
        self.addCleanup(self.delete_tempfile, tempname[:-4]+'.pbm')
        return tempname

    def save_font(self):
        font = self.open_font()
        tempname = self.get_tempname()
        font.save(tempname)
        return tempname

    def save_font2(self):
        font = self.open_font()
        tempname = self.get_tempname()
        font.save2(tempname)

    def test_sanity(self):
        self.save_font()
        self.save_font2()

    def xtest_draw(self):

        tempname = self.save_font()
        font = ImageFont.load(tempname)
        image = Image.new("L", font.getsize(MESSAGE), "white")
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), MESSAGE, font=font)
        # assert_signature(image, "7216c60f988dea43a46bb68321e3c1b03ec62aee")

    def _test_high_characters(self, message):

        tempname = self.save_font()
        font = ImageFont.load(tempname)
        image = Image.new("L", font.getsize(message), "white")
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), message, font=font)

        compare = Image.open('Tests/images/high_ascii_chars.png')
        self.assert_image_equal(image, compare)

    def test_high_characters(self):
        message = "".join([chr(i+1) for i in range(140, 232)])
        self._test_high_characters(message)
        # accept bytes instances in Py3.
        if bytes is not str:
            self._test_high_characters(message.encode('latin1'))


if __name__ == '__main__':
    unittest.main()

# End of file
