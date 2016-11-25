from helper import unittest, PillowTestCase, py3

from PIL import Image


class TestBGRa(PillowTestCase):

    def test_bgra(self):
        RGBA_RED_50 = b'\xff\x00\x00\x80'  # 50% red 
        BGRa_RED_50 = b'\x00\x00\x80\x80'  # 50% red 
        RGBa_RED_50 = b'\x80\x00\x00\x80'  # 50% red 

        im = Image.frombuffer("BGRa", (1, 1), BGRa_RED_50, 'raw', "BGRa", 0, 1)
        self.assertEqual(im.tobytes(), BGRa_RED_50)
        self.assertEqual(im.tobytes('raw', 'RGBa'), RGBa_RED_50)

        im = Image.frombuffer("RGBA", (1, 1), BGRa_RED_50, "raw", "BGRa", 4, 1)
        self.assertEqual(im.tobytes(), RGBA_RED_50)

        im = im.convert('BGRa')
        self.assertEqual(im.tobytes(), BGRa_RED_50)
        self.assertEqual(im.load()[0, 0], (0x00, 0x00, 0x80, 0x80))

        im = im.convert('RGBA')
        self.assertEqual(im.tobytes(), RGBA_RED_50)
        self.assertEqual(im.load()[0, 0], (0xff, 0x00, 0x00, 0x80))

if __name__ == '__main__':
    unittest.main()
