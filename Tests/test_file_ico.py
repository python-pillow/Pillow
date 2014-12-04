from helper import unittest, PillowTestCase, hopper

import io
from PIL import Image

# sample ppm stream
TEST_ICO_FILE = "Tests/images/hopper.ico"
TEST_DATA = open(TEST_ICO_FILE, "rb").read()


class TestFileIco(PillowTestCase):

    def test_sanity(self):
        im = Image.open(TEST_ICO_FILE)
        im.load()
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (16, 16))
        self.assertEqual(im.format, "ICO")

    def test_save_to_bytes(self):
        output = io.BytesIO()
        im = hopper()
        im.save(output, "ico", sizes=[(32, 32), (64, 64)])

        # the default image
        output.seek(0)
        reloaded = Image.open(output)
        self.assertEqual(reloaded.info['sizes'],set([(32, 32), (64, 64)]))

        self.assertEqual(im.mode, reloaded.mode)
        self.assertEqual((64, 64), reloaded.size)
        self.assertEqual(reloaded.format, "ICO")
        self.assert_image_equal(reloaded, hopper().resize((64,64), Image.LANCZOS))

        # the other one
        output.seek(0)
        reloaded = Image.open(output)
        reloaded.size = (32,32)

        self.assertEqual(im.mode, reloaded.mode)
        self.assertEqual((32, 32), reloaded.size)
        self.assertEqual(reloaded.format, "ICO")
        self.assert_image_equal(reloaded, hopper().resize((32,32), Image.LANCZOS))



if __name__ == '__main__':
    unittest.main()

# End of file
