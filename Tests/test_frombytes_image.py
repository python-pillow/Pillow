import unittest
from PIL import Image
import unittest


class TestFromBytes(unittest.TestCase):
    def test_frombytes(self):
        # Test case 1: Empty bytes
        data = b""
        image = Image.frombytes("RGB", (0, 0), data)
        self.assertEqual(image.size, (0, 0))

        # Test case 2: Non-empty bytes
        data = b"\x00\x00\xFF\xFF\x00\x00"
        image = Image.frombytes("RGB", (2, 1), data)
        self.assertEqual(image.size, (2, 1))
        self.assertEqual(image.getpixel((0, 0)), (0, 0, 255))
        self.assertEqual(image.getpixel((1, 0)), (255, 0, 0))

        # Test case 3: Invalid mode
        data = b"\x00\x00\xFF\xFF\x00\x00"
        with self.assertRaises(ValueError):
            Image.frombytes("RGBA", (2, 1), data)

        # Test case 4: Non-RGB mode
        data = b"\x00\x00\xFF\xFF\x00\x00"
        image = Image.frombytes("L", (2, 1), data)
        self.assertEqual(image.size, (2, 1))
        self.assertEqual(image.getpixel((0, 0)), 0)
        self.assertEqual(image.getpixel((1, 0)), 255)

        # Test case 5: Zero width
        data = b""
        image = Image.frombytes("RGB", (0, 1), data)
        self.assertEqual(image.size, (0, 1))

        # Test case 6: Zero height
        data = b""
        image = Image.frombytes("RGB", (1, 0), data)
        self.assertEqual(image.size, (1, 0))

        # Test case 7: s[0] < 0
        data = b"\x00\x00\xFF\xFF\x00\x00"
        s = (-1, 1)
        with self.assertRaises(ValueError):
            Image.frombytes("RGB", s, data)

        # Test case 8: s[1] == 0
        data = b"\x00\x00\xFF\xFF\x00\x00"
        s = (2, 0)
        with self.assertRaises(ValueError):
            Image.frombytes("RGB", s, data)

        # Test case 5: Different size
        data = b"\x00\x00\xFF\xFF\x00\x00\xFF\xFF\x00\x00"
        image = Image.frombytes("RGB", (3, 1), data)
        self.assertEqual(image.size, (3, 1))
        self.assertEqual(image.getpixel((0, 0)), (0, 0, 255))
        self.assertEqual(image.getpixel((1, 0)), (255, 0, 0))
        self.assertEqual(image.getpixel((2, 0)), (255, 0, 0))

if __name__ == "__main__":
    unittest.main()

