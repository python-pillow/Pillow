from PIL import McIdasImagePlugin
from PIL.exceptions import InvalidFileType
from helper import unittest, PillowTestCase


class TestFileMcIdas(PillowTestCase):

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(InvalidFileType,
                          lambda:
                          McIdasImagePlugin.McIdasImageFile(invalid_file))


if __name__ == '__main__':
    unittest.main()
