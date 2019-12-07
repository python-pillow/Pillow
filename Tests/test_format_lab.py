from PIL import Image

from .helper import PillowTestCase


class TestFormatLab(PillowTestCase):
    def test_white(self):
        with Image.open("Tests/images/lab.tif") as i:
            i.load()

            self.assertEqual(i.mode, "LAB")

            self.assertEqual(i.getbands(), ("L", "A", "B"))

            k = i.getpixel((0, 0))

            L = i.getdata(0)
            a = i.getdata(1)
            b = i.getdata(2)

        self.assertEqual(k, (255, 128, 128))

        self.assertEqual(list(L), [255] * 100)
        self.assertEqual(list(a), [128] * 100)
        self.assertEqual(list(b), [128] * 100)

    def test_green(self):
        # l= 50 (/100), a = -100 (-128 .. 128) b=0 in PS
        # == RGB: 0, 152, 117
        with Image.open("Tests/images/lab-green.tif") as i:
            k = i.getpixel((0, 0))
        self.assertEqual(k, (128, 28, 128))

    def test_red(self):
        # l= 50 (/100), a = 100 (-128 .. 128) b=0 in PS
        # == RGB: 255, 0, 124
        with Image.open("Tests/images/lab-red.tif") as i:
            k = i.getpixel((0, 0))
        self.assertEqual(k, (128, 228, 128))
