from helper import unittest, PillowTestCase, tearDownModule

from PIL import Image


class TestImage(PillowTestCase):

    def test_sanity(self):

        im = Image.new("L", (100, 100))
        self.assertEqual(
            repr(im)[:45], "<PIL.Image.Image image mode=L size=100x100 at")
        self.assertEqual(im.mode, "L")
        self.assertEqual(im.size, (100, 100))

        im = Image.new("RGB", (100, 100))
        self.assertEqual(
            repr(im)[:45], "<PIL.Image.Image image mode=RGB size=100x100 ")
        self.assertEqual(im.mode, "RGB")
        self.assertEqual(im.size, (100, 100))

        Image.new("L", (100, 100), None)
        im2 = Image.new("L", (100, 100), 0)
        im3 = Image.new("L", (100, 100), "black")

        self.assertEqual(im2.getcolors(), [(10000, 0)])
        self.assertEqual(im3.getcolors(), [(10000, 0)])

        self.assertRaises(ValueError, lambda: Image.new("X", (100, 100)))
        # self.assertRaises(
        #     MemoryError, lambda: Image.new("L", (1000000, 1000000)))

    def test_internals(self):

        im = Image.new("L", (100, 100))
        im.readonly = 1
        im._copy()
        self.assertFalse(im.readonly)

        im.readonly = 1
        im.paste(0, (0, 0, 100, 100))
        self.assertFalse(im.readonly)

        file = self.tempfile("temp.ppm")
        im._dump(file)


if __name__ == '__main__':
    unittest.main()

# End of file
