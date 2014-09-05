from helper import unittest, PillowTestCase, hopper

from PIL import Image


class TestFileMsp(PillowTestCase):

    def test_sanity(self):

        file = self.tempfile("temp.msp")

        hopper("1").save(file)

        im = Image.open(file)
        im.load()
        self.assertEqual(im.mode, "1")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "MSP")


if __name__ == '__main__':
    unittest.main()

# End of file
