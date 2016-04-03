from helper import unittest, PillowTestCase

from PIL import FontFile, BdfFontFile

filename = "Tests/images/courB08.bdf"


class TestFontBdf(PillowTestCase):

    def test_sanity(self):

        test_file = open(filename, "rb")
        font = BdfFontFile.BdfFontFile(test_file)

        self.assertIsInstance(font, FontFile.FontFile)
        self.assertEqual(len([_f for _f in font.glyph if _f]), 190)

    def test_invalid_file(self):
        with open("Tests/images/flower.jpg", "rb") as fp:
            self.assertRaises(SyntaxError, lambda: BdfFontFile.BdfFontFile(fp))


if __name__ == '__main__':
    unittest.main()

# End of file
