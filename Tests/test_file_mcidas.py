from helper import unittest, PillowTestCase

from PIL import McIdasImagePlugin


class TestFileMcIdas(PillowTestCase):

    def test_invalid_file(self):
        self.assertRaises(SyntaxError, lambda: McIdasImagePlugin.McIdasImageFile("Tests/images/flower.jpg"))


if __name__ == '__main__':
    unittest.main()

# End of file
