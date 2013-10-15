from tester import *

from PIL import Image

def pack():
    pass # not yet

def test_pack():

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

    assert_equal(pack("1", "1"), [128])
    assert_equal(pack("1", "1;I"), [0])
    assert_equal(pack("1", "1;R"), [1])
    assert_equal(pack("1", "1;IR"), [0])

    assert_equal(pack("L", "L"), [1])

    assert_equal(pack("I", "I"), [1, 0, 0, 0][::order])

    assert_equal(pack("F", "F"), [0, 0, 128, 63][::order])

    assert_equal(pack("LA", "LA"), [1, 2])

    assert_equal(pack("RGB", "RGB"), [1, 2, 3])
    assert_equal(pack("RGB", "RGB;L"), [1, 2, 3])
    assert_equal(pack("RGB", "BGR"), [3, 2, 1])
    assert_equal(pack("RGB", "RGBX"), [1, 2, 3, 255]) # 255?
    assert_equal(pack("RGB", "BGRX"), [3, 2, 1, 0])
    assert_equal(pack("RGB", "XRGB"), [0, 1, 2, 3])
    assert_equal(pack("RGB", "XBGR"), [0, 3, 2, 1])

    assert_equal(pack("RGBX", "RGBX"), [1, 2, 3, 4]) # 4->255?

    assert_equal(pack("RGBA", "RGBA"), [1, 2, 3, 4])

    assert_equal(pack("CMYK", "CMYK"), [1, 2, 3, 4])
    assert_equal(pack("YCbCr", "YCbCr"), [1, 2, 3])

def test_unpack():

    def unpack(mode, rawmode, bytes_):
        im = None

        if py3:
            data = bytes(range(1,bytes_+1))
        else:
            data = ''.join(chr(i) for i in range(1,bytes_+1))

        im = Image.frombytes(mode, (1, 1), data, "raw", rawmode, 0, 1)

        return im.getpixel((0, 0))

    def unpack_1(mode, rawmode, value):
        assert mode == "1"
        im = None

        if py3:
            im = Image.frombytes(mode, (8, 1), bytes([value]), "raw", rawmode, 0, 1)
        else:
            im = Image.frombytes(mode, (8, 1), chr(value), "raw", rawmode, 0, 1)

        return tuple(im.getdata())

    X = 255

    assert_equal(unpack_1("1", "1", 1),    (0,0,0,0,0,0,0,X))
    assert_equal(unpack_1("1", "1;I", 1),  (X,X,X,X,X,X,X,0))
    assert_equal(unpack_1("1", "1;R", 1),  (X,0,0,0,0,0,0,0))
    assert_equal(unpack_1("1", "1;IR", 1), (0,X,X,X,X,X,X,X))

    assert_equal(unpack_1("1", "1", 170),    (X,0,X,0,X,0,X,0))
    assert_equal(unpack_1("1", "1;I", 170),  (0,X,0,X,0,X,0,X))
    assert_equal(unpack_1("1", "1;R", 170),  (0,X,0,X,0,X,0,X))
    assert_equal(unpack_1("1", "1;IR", 170), (X,0,X,0,X,0,X,0))

    assert_equal(unpack("L", "L;2", 1), 0)
    assert_equal(unpack("L", "L;4", 1), 0)
    assert_equal(unpack("L", "L", 1), 1)
    assert_equal(unpack("L", "L;I", 1), 254)
    assert_equal(unpack("L", "L;R", 1), 128)
    assert_equal(unpack("L", "L;16", 2), 2) # little endian
    assert_equal(unpack("L", "L;16B", 2), 1) # big endian

    assert_equal(unpack("LA", "LA", 2), (1, 2))
    assert_equal(unpack("LA", "LA;L", 2), (1, 2))

    assert_equal(unpack("RGB", "RGB", 3), (1, 2, 3))
    assert_equal(unpack("RGB", "RGB;L", 3), (1, 2, 3))
    assert_equal(unpack("RGB", "RGB;R", 3), (128, 64, 192))
    assert_equal(unpack("RGB", "RGB;16B", 6), (1, 3, 5)) # ?
    assert_equal(unpack("RGB", "BGR", 3), (3, 2, 1))
    assert_equal(unpack("RGB", "RGB;15", 2), (8, 131, 0))
    assert_equal(unpack("RGB", "BGR;15", 2), (0, 131, 8))
    assert_equal(unpack("RGB", "RGB;16", 2), (8, 64, 0))
    assert_equal(unpack("RGB", "BGR;16", 2), (0, 64, 8))
    assert_equal(unpack("RGB", "RGB;4B", 2), (17, 0, 34))

    assert_equal(unpack("RGB", "RGBX", 4), (1, 2, 3))
    assert_equal(unpack("RGB", "BGRX", 4), (3, 2, 1))
    assert_equal(unpack("RGB", "XRGB", 4), (2, 3, 4))
    assert_equal(unpack("RGB", "XBGR", 4), (4, 3, 2))

    assert_equal(unpack("RGBA", "RGBA", 4), (1, 2, 3, 4))
    assert_equal(unpack("RGBA", "BGRA", 4), (3, 2, 1, 4))
    assert_equal(unpack("RGBA", "ARGB", 4), (2, 3, 4, 1))
    assert_equal(unpack("RGBA", "ABGR", 4), (4, 3, 2, 1))
    assert_equal(unpack("RGBA", "RGBA;15", 2), (8, 131, 0, 0))
    assert_equal(unpack("RGBA", "BGRA;15", 2), (0, 131, 8, 0))
    assert_equal(unpack("RGBA", "RGBA;4B", 2), (17, 0, 34, 0))

    assert_equal(unpack("RGBX", "RGBX", 4), (1, 2, 3, 4)) # 4->255?
    assert_equal(unpack("RGBX", "BGRX", 4), (3, 2, 1, 255))
    assert_equal(unpack("RGBX", "XRGB", 4), (2, 3, 4, 255))
    assert_equal(unpack("RGBX", "XBGR", 4), (4, 3, 2, 255))
    assert_equal(unpack("RGBX", "RGB;15", 2), (8, 131, 0, 255))
    assert_equal(unpack("RGBX", "BGR;15", 2), (0, 131, 8, 255))
    assert_equal(unpack("RGBX", "RGB;4B", 2), (17, 0, 34, 255))

    assert_equal(unpack("CMYK", "CMYK", 4), (1, 2, 3, 4))
    assert_equal(unpack("CMYK", "CMYK;I", 4), (254, 253, 252, 251))

    assert_exception(ValueError, lambda: unpack("L", "L", 0))
    assert_exception(ValueError, lambda: unpack("RGB", "RGB", 2))
    assert_exception(ValueError, lambda: unpack("CMYK", "CMYK", 2))

run()
