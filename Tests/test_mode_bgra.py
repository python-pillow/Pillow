from helper import unittest, PillowTestCase

from PIL import Image


class TestBGRa(PillowTestCase):

    def test_bgra(self):
        RGBA_RED_50 = b'\xff\x00\x00\x80'  # 50% red RGBA
        BGRa_RED_50 = b'\x00\x00\x80\x80'  # 50% red BGRa
        RGBa_RED_50 = b'\x80\x00\x00\x80'  # 50% red RGBa

        im = Image.frombuffer("RGBA", (1, 1), BGRa_RED_50, "raw", "BGRa", 4, 1)
        self.assertEqual(im.tobytes(), RGBA_RED_50)
        self.assertEqual(im.tobytes('raw', 'BGRa'), BGRa_RED_50)

        im = Image.frombuffer("RGBa", (1, 1), BGRa_RED_50, "raw", "BGRa", 4, 1)
        self.assertEqual(im.tobytes(), RGBa_RED_50)
        self.assertEqual(im.tobytes('raw', 'BGRa'), BGRa_RED_50)


if __name__ == '__main__':
    unittest.main()
