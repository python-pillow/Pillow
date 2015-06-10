from helper import unittest, PillowTestCase

from PIL import _binary


class TestBinary(PillowTestCase):

    def test_standard(self):
        self.assertEqual(_binary.i8(b'*'), 42)
        self.assertEqual(_binary.o8(42), b'*')

    def test_little_endian(self):
        self.assertEqual(_binary.i16le(b'\xff\xff\x00\x00'), 65535)
        self.assertEqual(_binary.i32le(b'\xff\xff\x00\x00'), 65535)

        self.assertEqual(_binary.o16le(65535), b'\xff\xff')
        self.assertEqual(_binary.o32le(65535), b'\xff\xff\x00\x00')

    def test_big_endian(self):
        self.assertEqual(_binary.i16be(b'\x00\x00\xff\xff'), 0)
        self.assertEqual(_binary.i32be(b'\x00\x00\xff\xff'), 65535)

        self.assertEqual(_binary.o16be(65535), b'\xff\xff')
        self.assertEqual(_binary.o32be(65535), b'\x00\x00\xff\xff')

if __name__ == '__main__':
    unittest.main()

# End of file
