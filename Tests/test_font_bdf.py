from helper import unittest, PillowTestCase

from PIL import FontFile, BdfFontFile

filename = "Tests/images/courB08.bdf"


class TestFontBdf(PillowTestCase):

    def test_sanity(self):

        file = open(filename, "rb")
        font = BdfFontFile.BdfFontFile(file)

        self.assertIsInstance(font, FontFile.FontFile)
        self.assertEqual(len([_f for _f in font.glyph if _f]), 190)


if __name__ == '__main__':
    unittest.main()

# End of file
