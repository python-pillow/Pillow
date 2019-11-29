from PIL import BdfFontFile, FontFile

from .helper import PillowTestCase

filename = "Tests/images/courB08.bdf"


class TestFontBdf(PillowTestCase):
    def test_sanity(self):

        with open(filename, "rb") as test_file:
            font = BdfFontFile.BdfFontFile(test_file)

        self.assertIsInstance(font, FontFile.FontFile)
        self.assertEqual(len([_f for _f in font.glyph if _f]), 190)

    def test_invalid_file(self):
        with open("Tests/images/flower.jpg", "rb") as fp:
            self.assertRaises(SyntaxError, BdfFontFile.BdfFontFile, fp)
