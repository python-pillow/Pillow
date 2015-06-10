from helper import unittest, PillowTestCase, py3

from PIL import Image


class TestLibPack(PillowTestCase):

    def pack(self):
        pass  # not yet

    def test_pack(self):

        def pack(mode, rawmode):
            if len(mode) == 1:
                im = Image.new(mode, (1, 1), 1)
            else:
                im = Image.new(mode, (1, 1), (1, 2, 3, 4)[:len(mode)])

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

        self.assertEqual(pack("RGBa", "RGBa"), [1, 2, 3, 4])
        self.assertEqual(pack("RGBa", "BGRa"), [3, 2, 1, 4])
        self.assertEqual(pack("RGBa", "aBGR"), [4, 3, 2, 1])

        self.assertEqual(pack("CMYK", "CMYK"), [1, 2, 3, 4])
        self.assertEqual(pack("YCbCr", "YCbCr"), [1, 2, 3])

    def test_unpack(self):

        def unpack(mode, rawmode, bytes_):
            im = None

            if py3:
                data = bytes(range(1, bytes_+1))
            else:
                data = ''.join(chr(i) for i in range(1, bytes_+1))

            im = Image.frombytes(mode, (1, 1), data, "raw", rawmode, 0, 1)

            return im.getpixel((0, 0))

        def unpack_1(mode, rawmode, value):
            assert mode == "1"
            im = None

            if py3:
                im = Image.frombytes(
                    mode, (8, 1), bytes([value]), "raw", rawmode, 0, 1)
            else:
                im = Image.frombytes(
                    mode, (8, 1), chr(value), "raw", rawmode, 0, 1)

            return tuple(im.getdata())

        X = 255

        self.assertEqual(unpack_1("1", "1", 1), (0, 0, 0, 0, 0, 0, 0, X))
        self.assertEqual(unpack_1("1", "1;I", 1), (X, X, X, X, X, X, X, 0))
        self.assertEqual(unpack_1("1", "1;R", 1), (X, 0, 0, 0, 0, 0, 0, 0))
        self.assertEqual(unpack_1("1", "1;IR", 1), (0, X, X, X, X, X, X, X))

        self.assertEqual(unpack_1("1", "1", 170), (X, 0, X, 0, X, 0, X, 0))
        self.assertEqual(unpack_1("1", "1;I", 170), (0, X, 0, X, 0, X, 0, X))
        self.assertEqual(unpack_1("1", "1;R", 170), (0, X, 0, X, 0, X, 0, X))
        self.assertEqual(unpack_1("1", "1;IR", 170), (X, 0, X, 0, X, 0, X, 0))

        self.assertEqual(unpack("L", "L;2", 1), 0)
        self.assertEqual(unpack("L", "L;4", 1), 0)
        self.assertEqual(unpack("L", "L", 1), 1)
        self.assertEqual(unpack("L", "L;I", 1), 254)
        self.assertEqual(unpack("L", "L;R", 1), 128)
        self.assertEqual(unpack("L", "L;16", 2), 2)  # little endian
        self.assertEqual(unpack("L", "L;16B", 2), 1)  # big endian

        self.assertEqual(unpack("LA", "LA", 2), (1, 2))
        self.assertEqual(unpack("LA", "LA;L", 2), (1, 2))

        self.assertEqual(unpack("RGB", "RGB", 3), (1, 2, 3))
        self.assertEqual(unpack("RGB", "RGB;L", 3), (1, 2, 3))
        self.assertEqual(unpack("RGB", "RGB;R", 3), (128, 64, 192))
        self.assertEqual(unpack("RGB", "RGB;16B", 6), (1, 3, 5))  # ?
        self.assertEqual(unpack("RGB", "BGR", 3), (3, 2, 1))
        self.assertEqual(unpack("RGB", "RGB;15", 2), (8, 131, 0))
        self.assertEqual(unpack("RGB", "BGR;15", 2), (0, 131, 8))
        self.assertEqual(unpack("RGB", "RGB;16", 2), (8, 64, 0))
        self.assertEqual(unpack("RGB", "BGR;16", 2), (0, 64, 8))
        self.assertEqual(unpack("RGB", "RGB;4B", 2), (17, 0, 34))

        self.assertEqual(unpack("RGB", "RGBX", 4), (1, 2, 3))
        self.assertEqual(unpack("RGB", "BGRX", 4), (3, 2, 1))
        self.assertEqual(unpack("RGB", "XRGB", 4), (2, 3, 4))
        self.assertEqual(unpack("RGB", "XBGR", 4), (4, 3, 2))

        self.assertEqual(unpack("RGBA", "RGBA", 4), (1, 2, 3, 4))
        self.assertEqual(unpack("RGBA", "BGRA", 4), (3, 2, 1, 4))
        self.assertEqual(unpack("RGBA", "ARGB", 4), (2, 3, 4, 1))
        self.assertEqual(unpack("RGBA", "ABGR", 4), (4, 3, 2, 1))
        self.assertEqual(unpack("RGBA", "RGBA;15", 2), (8, 131, 0, 0))
        self.assertEqual(unpack("RGBA", "BGRA;15", 2), (0, 131, 8, 0))
        self.assertEqual(unpack("RGBA", "RGBA;4B", 2), (17, 0, 34, 0))

        self.assertEqual(unpack("RGBa", "RGBa", 4), (1, 2, 3, 4))
        self.assertEqual(unpack("RGBa", "BGRa", 4), (3, 2, 1, 4))
        self.assertEqual(unpack("RGBa", "aRGB", 4), (2, 3, 4, 1))
        self.assertEqual(unpack("RGBa", "aBGR", 4), (4, 3, 2, 1))

        self.assertEqual(unpack("RGBX", "RGBX", 4), (1, 2, 3, 4))  # 4->255?
        self.assertEqual(unpack("RGBX", "BGRX", 4), (3, 2, 1, 255))
        self.assertEqual(unpack("RGBX", "XRGB", 4), (2, 3, 4, 255))
        self.assertEqual(unpack("RGBX", "XBGR", 4), (4, 3, 2, 255))
        self.assertEqual(unpack("RGBX", "RGB;15", 2), (8, 131, 0, 255))
        self.assertEqual(unpack("RGBX", "BGR;15", 2), (0, 131, 8, 255))
        self.assertEqual(unpack("RGBX", "RGB;4B", 2), (17, 0, 34, 255))

        self.assertEqual(unpack("CMYK", "CMYK", 4), (1, 2, 3, 4))
        self.assertEqual(unpack("CMYK", "CMYK;I", 4), (254, 253, 252, 251))

        self.assertRaises(ValueError, lambda: unpack("L", "L", 0))
        self.assertRaises(ValueError, lambda: unpack("RGB", "RGB", 2))
        self.assertRaises(ValueError, lambda: unpack("CMYK", "CMYK", 2))


if __name__ == '__main__':
    unittest.main()

# End of file
