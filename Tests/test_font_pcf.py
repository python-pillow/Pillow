from helper import unittest, PillowTestCase

from PIL import Image, FontFile, PcfFontFile
from PIL import ImageFont, ImageDraw

codecs = dir(Image.core)

fontname = "Tests/fonts/helvO18.pcf"

message = "hello, world"


class TestFontPcf(PillowTestCase):

    def setUp(self):
        if "zip_encoder" not in codecs or "zip_decoder" not in codecs:
            self.skipTest("zlib support not available")

    def save_font(self):
        test_file = open(fontname, "rb")
        font = PcfFontFile.PcfFontFile(test_file)
        self.assertIsInstance(font, FontFile.FontFile)
        self.assertEqual(len([_f for _f in font.glyph if _f]), 192)

        tempname = self.tempfile("temp.pil")
        self.addCleanup(self.delete_tempfile, tempname[:-4]+'.pbm')
        font.save(tempname)
        return tempname

    def test_sanity(self):
        self.save_font()

    def test_invalid_file(self):
        with open("Tests/images/flower.jpg", "rb") as fp:
            self.assertRaises(SyntaxError, lambda: PcfFontFile.PcfFontFile(fp))

    def xtest_draw(self):

        tempname = self.save_font()
        font = ImageFont.load(tempname)
        image = Image.new("L", font.getsize(message), "white")
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), message, font=font)
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
