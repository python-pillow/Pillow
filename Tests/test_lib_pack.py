import sys

from helper import unittest, PillowTestCase, py3

from PIL import Image


X = 255


class TestLibPack(PillowTestCase):

    def pack(self):
        pass  # not yet

    def test_pack(self):

        def pack(mode, rawmode, in_data=(1, 2, 3, 4)):
            if len(mode) == 1:
                im = Image.new(mode, (1, 1), in_data[0])
            else:
                im = Image.new(mode, (1, 1), in_data[:len(mode)])

            if py3:
                return list(im.tobytes("raw", rawmode))
            else:
                return [ord(c) for c in im.tobytes("raw", rawmode)]

        order = 1 if Image._ENDIAN == '<' else -1

        self.assertEqual(pack("1", "1"), [128])
        self.assertEqual(pack("1", "1;I"), [0])
        self.assertEqual(pack("1", "1;R"), [1])
        self.assertEqual(pack("1", "1;IR"), [0])

        self.assertEqual(pack("L", "L"), [1])

        self.assertEqual(pack("I", "I"), [1, 0, 0, 0][::order])

        self.assertEqual(pack("F", "F"), [0, 0, 128, 63][::order])

        self.assertEqual(pack("LA", "LA"), [1, 2])

        self.assertEqual(pack("RGB", "RGB"), [1, 2, 3])
        self.assertEqual(pack("RGB", "RGB;L"), [1, 2, 3])
        self.assertEqual(pack("RGB", "BGR"), [3, 2, 1])
        self.assertEqual(pack("RGB", "RGBX"), [1, 2, 3, 255])  # 255?
        self.assertEqual(pack("RGB", "BGRX"), [3, 2, 1, 0])
        self.assertEqual(pack("RGB", "XRGB"), [0, 1, 2, 3])
        self.assertEqual(pack("RGB", "XBGR"), [0, 3, 2, 1])

        self.assertEqual(pack("RGBX", "RGBX"), [1, 2, 3, 4])  # 4->255?

        self.assertEqual(pack("RGBA", "RGBA"), [1, 2, 3, 4])
        self.assertEqual(pack("RGBA", "BGRa"), [0, 0, 0, 4])
        self.assertEqual(pack("RGBA", "BGRa", in_data=(20, 30, 40, 50)), [8, 6, 4, 50])

        self.assertEqual(pack("RGBa", "RGBa"), [1, 2, 3, 4])
        self.assertEqual(pack("RGBa", "BGRa"), [3, 2, 1, 4])
        self.assertEqual(pack("RGBa", "aBGR"), [4, 3, 2, 1])

        self.assertEqual(pack("CMYK", "CMYK"), [1, 2, 3, 4])
        self.assertEqual(pack("YCbCr", "YCbCr"), [1, 2, 3])


class TestLibUnpack(PillowTestCase):
    def assert_unpack(self, mode, rawmode, data, *pixels):
        """
        data - eather raw bytes with data or just number of bytes in rawmode.
        """
        if isinstance(data, (int)):
            data_len = data * len(pixels)
            data = bytes(bytearray(range(1, data_len + 1)))

        im = Image.frombytes(mode, (len(pixels), 1), data, "raw", rawmode, 0, 1)

        for x, pixel in enumerate(pixels):
            self.assertEqual(pixel, im.getpixel((x, 0)))

    def test_1(self):
        self.assert_unpack("1", "1", b'\x01', 0, 0, 0, 0, 0, 0, 0, X)
        self.assert_unpack("1", "1;I", b'\x01', X, X, X, X, X, X, X, 0)
        self.assert_unpack("1", "1;R", b'\x01', X, 0, 0, 0, 0, 0, 0, 0)
        self.assert_unpack("1", "1;IR", b'\x01', 0, X, X, X, X, X, X, X)

        self.assert_unpack("1", "1", b'\xaa', X, 0, X, 0, X, 0, X, 0)
        self.assert_unpack("1", "1;I", b'\xaa', 0, X, 0, X, 0, X, 0, X)
        self.assert_unpack("1", "1;R", b'\xaa', 0, X, 0, X, 0, X, 0, X)
        self.assert_unpack("1", "1;IR", b'\xaa', X, 0, X, 0, X, 0, X, 0)

        self.assert_unpack("1", "1;8", b'\x00\x01\x02\xff', 0, X, X, X)

    def test_L(self):
        self.assert_unpack("L", "L;2", b'\xe4', 255, 170, 85, 0)
        self.assert_unpack("L", "L;2I", b'\xe4', 0, 85, 170, 255)
        self.assert_unpack("L", "L;2R", b'\xe4', 0, 170, 85, 255)
        self.assert_unpack("L", "L;2IR", b'\xe4', 255, 85, 170, 0)

        self.assert_unpack("L", "L;4", b'\x02\xef', 0, 34, 238, 255)
        self.assert_unpack("L", "L;4I", b'\x02\xef', 255, 221, 17, 0)
        self.assert_unpack("L", "L;4R", b'\x02\xef', 68, 0, 255, 119)
        self.assert_unpack("L", "L;4IR", b'\x02\xef', 187, 255, 0, 136)

        self.assert_unpack("L", "L", 1, 1, 2, 3, 4)
        self.assert_unpack("L", "L;I", 1, 254, 253, 252, 251)
        self.assert_unpack("L", "L;R", 1, 128, 64, 192, 32)
        self.assert_unpack("L", "L;16", 2, 2, 4, 6, 8)
        self.assert_unpack("L", "L;16B", 2, 1, 3, 5, 7)

    def test_LA(self):
        self.assert_unpack("LA", "LA", 2, (1, 2), (3, 4), (5, 6))
        self.assert_unpack("LA", "LA;L", 2, (1, 4), (2, 5), (3, 6))

    def test_P(self):
        self.assert_unpack("P", "P;1", b'\xe4', 1, 1, 1, 0, 0, 1, 0, 0)
        self.assert_unpack("P", "P;2", b'\xe4', 3, 2, 1, 0)
        # self.assert_unpack("P", "P;2L", b'\xe4', 1, 1, 1, 0)  # erroneous?
        self.assert_unpack("P", "P;4", b'\x02\xef', 0, 2, 14, 15)
        # self.assert_unpack("P", "P;4L", b'\x02\xef', 2, 10, 10, 0)  # erroneous?
        self.assert_unpack("P", "P", 1, 1, 2, 3, 4)
        self.assert_unpack("P", "P;R", 1, 128, 64, 192, 32)

    def test_PA(self):
        self.assert_unpack("PA", "PA", 2, (1, 2), (3, 4), (5, 6))
        self.assert_unpack("PA", "PA;L", 2, (1, 4), (2, 5), (3, 6))

    def test_RGB(self):
        self.assert_unpack("RGB", "RGB", 3, (1,2,3), (4,5,6), (7,8,9))
        self.assert_unpack("RGB", "RGB;L", 3, (1,4,7), (2,5,8), (3,6,9))
        self.assert_unpack("RGB", "RGB;R", 3, (128,64,192), (32,160,96))
        self.assert_unpack("RGB", "RGB;16B", 6, (1,3,5), (7,9,11))
        self.assert_unpack("RGB", "BGR", 3, (3,2,1), (6,5,4), (9,8,7))
        self.assert_unpack("RGB", "RGB;15", 2, (8,131,0), (24,0,8))
        self.assert_unpack("RGB", "BGR;15", 2, (0,131,8), (8,0,24))
        self.assert_unpack("RGB", "RGB;16", 2, (8,64,0), (24,129,0))
        self.assert_unpack("RGB", "BGR;16", 2, (0,64,8), (0,129,24))
        self.assert_unpack("RGB", "RGB;4B", 2, (17,0,34), (51,0,68))
        self.assert_unpack("RGB", "RGBX", 4, (1,2,3), (5,6,7), (9,10,11))
        self.assert_unpack("RGB", "RGBX;L", 4, (1,4,7), (2,5,8), (3,6,9))
        self.assert_unpack("RGB", "BGRX", 4, (3,2,1), (7,6,5), (11,10,9))
        self.assert_unpack("RGB", "XRGB", 4, (2,3,4), (6,7,8), (10,11,12))
        self.assert_unpack("RGB", "XBGR", 4, (4,3,2), (8,7,6), (12,11,10))
        self.assert_unpack("RGB", "YCC;P",
            b'D]\x9c\x82\x1a\x91\xfaOC\xe7J\x12',  # random data
            (127,102,0), (192,227,0), (213,255,170), (98,255,133))
        self.assert_unpack("RGB", "R", 1, (1,0,0), (2,0,0), (3,0,0))
        self.assert_unpack("RGB", "G", 1, (0,1,0), (0,2,0), (0,3,0))
        self.assert_unpack("RGB", "B", 1, (0,0,1), (0,0,2), (0,0,3))

    def test_RGBA(self):
        self.assert_unpack("RGBA", "LA", 2, (1,1,1,2), (3,3,3,4), (5,5,5,6))
        self.assert_unpack("RGBA", "LA;16B", 4,
            (1,1,1,3), (5,5,5,7), (9,9,9,11))
        self.assert_unpack("RGBA", "RGBA", 4,
            (1,2,3,4), (5,6,7,8), (9,10,11,12))
        self.assert_unpack("RGBA", "RGBa", 4,
            (63,127,191,4), (159,191,223,8), (191,212,233,12))
        self.assert_unpack("RGBA", "BGRa", 4,
            (191,127,63,4), (223,191,159,8), (233,212,191,12))
        self.assert_unpack("RGBA", "RGBA;I", 4,
            (254,253,252,4), (250,249,248,8), (246,245,244,12))
        self.assert_unpack("RGBA", "RGBA;L", 4,
            (1,4,7,10), (2,5,8,11), (3,6,9,12))
        self.assert_unpack("RGBA", "RGBA;15", 2, (8,131,0,0), (24,0,8,0))
        self.assert_unpack("RGBA", "BGRA;15", 2, (0,131,8,0), (8,0,24,0))
        self.assert_unpack("RGBA", "RGBA;4B", 2, (17,0,34,0), (51,0,68,0))
        self.assert_unpack("RGBA", "RGBA;16B", 8, (1,3,5,7), (9,11,13,15))
        self.assert_unpack("RGBA", "BGRA", 4,
            (3,2,1,4), (7,6,5,8), (11,10,9,12))
        self.assert_unpack("RGBA", "ARGB", 4,
            (2,3,4,1), (6,7,8,5), (10,11,12,9))
        self.assert_unpack("RGBA", "ABGR", 4,
            (4,3,2,1), (8,7,6,5), (12,11,10,9))
        self.assert_unpack("RGBA", "YCCA;P",
            b']bE\x04\xdd\xbej\xed57T\xce\xac\xce:\x11',  # random data
            (0,161,0,4), (255,255,255,237), (27,158,0,206), (0,118,0,17))
        self.assert_unpack("RGBA", "R", 1, (1,0,0,0), (2,0,0,0), (3,0,0,0))
        self.assert_unpack("RGBA", "G", 1, (0,1,0,0), (0,2,0,0), (0,3,0,0))
        self.assert_unpack("RGBA", "B", 1, (0,0,1,0), (0,0,2,0), (0,0,3,0))
        self.assert_unpack("RGBA", "A", 1, (0,0,0,1), (0,0,0,2), (0,0,0,3))

    def test_RGBa(self):
        self.assert_unpack("RGBa", "RGBa", 4,
            (1,2,3,4), (5,6,7,8), (9,10,11,12))
        self.assert_unpack("RGBa", "BGRa", 4,
            (3,2,1,4), (7,6,5,8), (11,10,9,12))
        self.assert_unpack("RGBa", "aRGB", 4,
            (2,3,4,1), (6,7,8,5), (10,11,12,9))
        self.assert_unpack("RGBa", "aBGR", 4,
            (4,3,2,1), (8,7,6,5), (12,11,10,9))

    def test_RGBX(self):
        self.assert_unpack("RGBX", "RGB", 3, (1,2,3,X), (4,5,6,X), (7,8,9,X))
        self.assert_unpack("RGBX", "RGB;L", 3, (1,4,7,X), (2,5,8,X), (3,6,9,X))
        self.assert_unpack("RGBX", "RGB;16B", 6, (1,3,5,X), (7,9,11,X))
        self.assert_unpack("RGBX", "BGR", 3, (3,2,1,X), (6,5,4,X), (9,8,7,X))
        self.assert_unpack("RGBX", "RGB;15", 2, (8,131,0,X), (24,0,8,X))
        self.assert_unpack("RGBX", "BGR;15", 2, (0,131,8,X), (8,0,24,X))
        self.assert_unpack("RGBX", "RGB;4B", 2, (17,0,34,X), (51,0,68,X))
        self.assert_unpack("RGBX", "RGBX", 4,
            (1,2,3,4), (5,6,7,8), (9,10,11,12))
        self.assert_unpack("RGBX", "RGBX;L", 4,
            (1,4,7,10), (2,5,8,11), (3,6,9,12))
        self.assert_unpack("RGBX", "BGRX", 4, (3,2,1,X), (7,6,5,X), (11,10,9,X))
        self.assert_unpack("RGBX", "XRGB", 4, (2,3,4,X), (6,7,8,X), (10,11,12,X))
        self.assert_unpack("RGBX", "XBGR", 4, (4,3,2,X), (8,7,6,X), (12,11,10,X))
        self.assert_unpack("RGBX", "YCC;P",
            b'D]\x9c\x82\x1a\x91\xfaOC\xe7J\x12',  # random data
            (127,102,0,X), (192,227,0,X), (213,255,170,X), (98,255,133,X))
        self.assert_unpack("RGBX", "R", 1, (1,0,0,0), (2,0,0,0), (3,0,0,0))
        self.assert_unpack("RGBX", "G", 1, (0,1,0,0), (0,2,0,0), (0,3,0,0))
        self.assert_unpack("RGBX", "B", 1, (0,0,1,0), (0,0,2,0), (0,0,3,0))
        self.assert_unpack("RGBX", "X", 1, (0,0,0,1), (0,0,0,2), (0,0,0,3))

    def test_CMYK(self):
        self.assert_unpack("CMYK", "CMYK", 4, (1,2,3,4), (5,6,7,8), (9,10,11,12))
        self.assert_unpack("CMYK", "CMYK;I", 4,
            (254,253,252,251), (250,249,248,247), (246,245,244,243))
        self.assert_unpack("CMYK", "CMYK;L", 4,
            (1,4,7,10), (2,5,8,11), (3,6,9,12))
        self.assert_unpack("CMYK", "C", 1, (1,0,0,0), (2,0,0,0), (3,0,0,0))
        self.assert_unpack("CMYK", "M", 1, (0,1,0,0), (0,2,0,0), (0,3,0,0))
        self.assert_unpack("CMYK", "Y", 1, (0,0,1,0), (0,0,2,0), (0,0,3,0))
        self.assert_unpack("CMYK", "K", 1, (0,0,0,1), (0,0,0,2), (0,0,0,3))
        self.assert_unpack("CMYK", "C;I", 1,
            (254,0,0,0), (253,0,0,0), (252,0,0,0))
        self.assert_unpack("CMYK", "M;I", 1,
            (0,254,0,0), (0,253,0,0), (0,252,0,0))
        self.assert_unpack("CMYK", "Y;I", 1,
            (0,0,254,0), (0,0,253,0), (0,0,252,0))
        self.assert_unpack("CMYK", "K;I", 1,
            (0,0,0,254), (0,0,0,253), (0,0,0,252))

    def test_YCbCr(self):
        self.assert_unpack("YCbCr", "YCbCr", 3, (1,2,3), (4,5,6), (7,8,9))
        self.assert_unpack("YCbCr", "YCbCr;L", 3, (1,4,7), (2,5,8), (3,6,9))
        self.assert_unpack("YCbCr", "YCbCrX", 4, (1,2,3), (5,6,7), (9,10,11))
        self.assert_unpack("YCbCr", "YCbCrK", 4, (1,2,3), (5,6,7), (9,10,11))

    def test_LAB(self):
        self.assert_unpack("LAB", "LAB", 3,
            (1,130,131), (4,133,134), (7,136,137))
        self.assert_unpack("LAB", "L", 1, (1,0,0), (2,0,0), (3,0,0))
        self.assert_unpack("LAB", "A", 1, (0,1,0), (0,2,0), (0,3,0))
        self.assert_unpack("LAB", "B", 1, (0,0,1), (0,0,2), (0,0,3))

    def test_HSV(self):
        self.assert_unpack("HSV", "HSV", 3, (1,2,3), (4,5,6), (7,8,9))
        self.assert_unpack("HSV", "H", 1, (1,0,0), (2,0,0), (3,0,0))
        self.assert_unpack("HSV", "S", 1, (0,1,0), (0,2,0), (0,3,0))
        self.assert_unpack("HSV", "V", 1, (0,0,1), (0,0,2), (0,0,3))

    def test_I(self):
        self.assert_unpack("I", "I", 4, 0x04030201, 0x08070605)
        self.assert_unpack("I", "I;8", 1, 0x01, 0x02, 0x03, 0x04)
        self.assert_unpack("I", "I;8S", b'\x01\x83', 1, -125)
        self.assert_unpack("I", "I;16", 2, 0x0201, 0x0403)
        self.assert_unpack("I", "I;16S", b'\x83\x01\x01\x83', 0x0183, -31999)
        self.assert_unpack("I", "I;16B", 2, 0x0102, 0x0304)
        self.assert_unpack("I", "I;16BS", b'\x83\x01\x01\x83', -31999, 0x0183)
        self.assert_unpack("I", "I;32", 4, 0x04030201, 0x08070605)
        self.assert_unpack("I", "I;32S",
            b'\x83\x00\x00\x01\x01\x00\x00\x83',
            0x01000083, -2097151999)
        self.assert_unpack("I", "I;32B", 4, 0x01020304, 0x05060708)
        self.assert_unpack("I", "I;32BS",
            b'\x83\x00\x00\x01\x01\x00\x00\x83',
            -2097151999, 0x01000083)

        if sys.byteorder == 'little':
            self.assert_unpack("I", "I;16N", 2, 0x0201, 0x0403)
            self.assert_unpack("I", "I;16NS", b'\x83\x01\x01\x83', 0x0183, -31999)
            self.assert_unpack("I", "I;32N", 4, 0x04030201, 0x08070605)
            self.assert_unpack("I", "I;32NS",
                b'\x83\x00\x00\x01\x01\x00\x00\x83',
                0x01000083, -2097151999)
        else:
            self.assert_unpack("I", "I;16N", 2, 0x0102, 0x0304)
            self.assert_unpack("I", "I;16NS", b'\x83\x01\x01\x83', -31999, 0x0183)
            self.assert_unpack("I", "I;32N", 4, 0x01020304, 0x05060708)
            self.assert_unpack("I", "I;32NS",
                b'\x83\x00\x00\x01\x01\x00\x00\x83',
                -2097151999, 0x01000083)

    def test_F_int(self):
        self.assert_unpack("F", "F;8", 1, 0x01, 0x02, 0x03, 0x04)
        self.assert_unpack("F", "F;8S", b'\x01\x83', 1, -125)
        self.assert_unpack("F", "F;16", 2, 0x0201, 0x0403)
        self.assert_unpack("F", "F;16S", b'\x83\x01\x01\x83', 0x0183, -31999)
        self.assert_unpack("F", "F;16B", 2, 0x0102, 0x0304)
        self.assert_unpack("F", "F;16BS", b'\x83\x01\x01\x83', -31999, 0x0183)
        self.assert_unpack("F", "F;32", 4, 67305984, 134678016)
        self.assert_unpack("F", "F;32S",
            b'\x83\x00\x00\x01\x01\x00\x00\x83',
            16777348, -2097152000)
        self.assert_unpack("F", "F;32B", 4, 0x01020304, 0x05060708)
        self.assert_unpack("F", "F;32BS",
            b'\x83\x00\x00\x01\x01\x00\x00\x83',
            -2097152000, 16777348)

        if sys.byteorder == 'little':
            self.assert_unpack("F", "F;16N", 2, 0x0201, 0x0403)
            self.assert_unpack("F", "F;16NS", b'\x83\x01\x01\x83', 0x0183, -31999)
            self.assert_unpack("F", "F;32N", 4, 67305984, 134678016)
            self.assert_unpack("F", "F;32NS",
                b'\x83\x00\x00\x01\x01\x00\x00\x83',
                16777348, -2097152000)
        else:
            self.assert_unpack("F", "F;16N", 2, 0x0102, 0x0304)
            self.assert_unpack("F", "F;16NS", b'\x83\x01\x01\x83', -31999, 0x0183)
            self.assert_unpack("F", "F;32N", 4, 0x01020304, 0x05060708)
            self.assert_unpack("F", "F;32NS",
                b'\x83\x00\x00\x01\x01\x00\x00\x83',
                -2097152000, 16777348)

    def test_F_float(self):
        self.assert_unpack("F", "F", 4,
            1.539989614439558e-36, 4.063216068939723e-34)
        self.assert_unpack("F", "F;32F", 4,
            1.539989614439558e-36, 4.063216068939723e-34)
        self.assert_unpack("F", "F;32BF", 4,
            2.387939260590663e-38, 6.301941157072183e-36)
        self.assert_unpack("F", "F;64F",
            b'333333\xc3?\x00\x00\x00\x00\x00J\x93\xc0',  # by struct.pack
            0.15000000596046448, -1234.5)
        self.assert_unpack("F", "F;64BF",
            b'?\xc3333333\xc0\x93J\x00\x00\x00\x00\x00',  # by struct.pack
            0.15000000596046448, -1234.5)

        if sys.byteorder == 'little':
            self.assert_unpack("F", "F;32NF", 4,
                1.539989614439558e-36, 4.063216068939723e-34)
            self.assert_unpack("F", "F;64NF",
                b'333333\xc3?\x00\x00\x00\x00\x00J\x93\xc0',
                0.15000000596046448, -1234.5)
        else:
            self.assert_unpack("F", "F;32NF", 4,
                2.387939260590663e-38, 6.301941157072183e-36)
            self.assert_unpack("F", "F;64NF",
                b'?\xc3333333\xc0\x93J\x00\x00\x00\x00\x00',
                0.15000000596046448, -1234.5)

    def test_I16(self):
        self.assert_unpack("I;16", "I;16", 2, 0x0201, 0x0403, 0x0605)
        self.assert_unpack("I;16B", "I;16B", 2, 0x0102, 0x0304, 0x0506)
        self.assert_unpack("I;16L", "I;16L", 2, 0x0201, 0x0403, 0x0605)
        self.assert_unpack("I;16", "I;12", 2, 0x0010, 0x0203, 0x0040, 0x0506)
        if sys.byteorder == 'little':
            self.assert_unpack("I;16", "I;16N", 2, 0x0201, 0x0403, 0x0605)
            self.assert_unpack("I;16B", "I;16N", 2, 0x0201, 0x0403, 0x0605)
            self.assert_unpack("I;16L", "I;16N", 2, 0x0201, 0x0403, 0x0605)
        else:
            self.assert_unpack("I;16", "I;16N", 2, 0x0102, 0x0304, 0x0506)
            self.assert_unpack("I;16B", "I;16N", 2, 0x0102, 0x0304, 0x0506)
            self.assert_unpack("I;16L", "I;16N", 2, 0x0102, 0x0304, 0x0506)

    def test_value_error(self):
        self.assertRaises(ValueError, self.assert_unpack, "L", "L", 0, 0)
        self.assertRaises(ValueError, self.assert_unpack, "RGB", "RGB", 2, 0)
        self.assertRaises(ValueError, self.assert_unpack, "CMYK", "CMYK", 2, 0)


if __name__ == '__main__':
    unittest.main()
