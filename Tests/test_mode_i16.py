from helper import unittest, PillowTestCase, hopper

from PIL import Image


class TestModeI16(PillowTestCase):

    original = hopper().resize((32, 32)).convert('I')

    def verify(self, im1):
        im2 = self.original.copy()
        self.assertEqual(im1.size, im2.size)
        pix1 = im1.load()
        pix2 = im2.load()
        for y in range(im1.size[1]):
            for x in range(im1.size[0]):
                xy = x, y
                p1 = pix1[xy]
                p2 = pix2[xy]
                self.assertEqual(
                    p1, p2,
                    ("got %r from mode %s at %s, expected %r" %
                        (p1, im1.mode, xy, p2)))

    def test_basic(self):
        # PIL 1.1 has limited support for 16-bit image data.  Check that
        # create/copy/transform and save works as expected.

        def basic(mode):

            imIn = self.original.convert(mode)
            self.verify(imIn)

            w, h = imIn.size

            imOut = imIn.copy()
            self.verify(imOut)  # copy

            imOut = imIn.transform((w, h), Image.EXTENT, (0, 0, w, h))
            self.verify(imOut)  # transform

            filename = self.tempfile("temp.im")
            imIn.save(filename)

            imOut = Image.open(filename)

            self.verify(imIn)
            self.verify(imOut)

            imOut = imIn.crop((0, 0, w, h))
            self.verify(imOut)

            imOut = Image.new(mode, (w, h), None)
            imOut.paste(imIn.crop((0, 0, w//2, h)), (0, 0))
            imOut.paste(imIn.crop((w//2, 0, w, h)), (w//2, 0))

            self.verify(imIn)
            self.verify(imOut)

            imIn = Image.new(mode, (1, 1), 1)
            self.assertEqual(imIn.getpixel((0, 0)), 1)

            imIn.putpixel((0, 0), 2)
            self.assertEqual(imIn.getpixel((0, 0)), 2)

            if mode == "L":
                maximum = 255
            else:
                maximum = 32767

            imIn = Image.new(mode, (1, 1), 256)
            self.assertEqual(imIn.getpixel((0, 0)), min(256, maximum))

            imIn.putpixel((0, 0), 512)
            self.assertEqual(imIn.getpixel((0, 0)), min(512, maximum))

        basic("L")

        basic("I;16")
        basic("I;16B")
        basic("I;16L")

        basic("I")

    def test_tobytes(self):

        def tobytes(mode):
            return Image.new(mode, (1, 1), 1).tobytes()

        order = 1 if Image._ENDIAN == '<' else -1

        self.assertEqual(tobytes("L"), b"\x01")
        self.assertEqual(tobytes("I;16"), b"\x01\x00")
        self.assertEqual(tobytes("I;16B"), b"\x00\x01")
        self.assertEqual(tobytes("I"), b"\x01\x00\x00\x00"[::order])

    def test_convert(self):

        im = self.original.copy()

        self.verify(im.convert("I;16"))
        self.verify(im.convert("I;16").convert("L"))
        self.verify(im.convert("I;16").convert("I"))

        self.verify(im.convert("I;16B"))
        self.verify(im.convert("I;16B").convert("L"))
        self.verify(im.convert("I;16B").convert("I"))


if __name__ == '__main__':
    unittest.main()
