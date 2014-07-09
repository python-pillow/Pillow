from helper import unittest, PillowTestCase, lena

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

    def test_comparison_with_other_type(self):
        # Arrange
        item = Image.new('RGB', (25, 25), '#000')
        num = 12

        # Act/Assert
        # Shouldn't cause AttributeError (#774)
        self.assertFalse(item is None)
        self.assertFalse(item == None)
        self.assertFalse(item == num)

    def test_expand_x(self):
        # Arrange
        im = lena()
        orig_size = im.size
        xmargin = 5

        # Act
        im = im._expand(xmargin)

        # Assert
        self.assertEqual(im.size[0], orig_size[0] + 2*xmargin)
        self.assertEqual(im.size[1], orig_size[1] + 2*xmargin)

    def test_expand_xy(self):
        # Arrange
        im = lena()
        orig_size = im.size
        xmargin = 5
        ymargin = 3

        # Act
        im = im._expand(xmargin, ymargin)

        # Assert
        self.assertEqual(im.size[0], orig_size[0] + 2*xmargin)
        self.assertEqual(im.size[1], orig_size[1] + 2*ymargin)

    def test_getbands(self):
        # Arrange
        im = lena()

        # Act
        bands = im.getbands()

        # Assert
        self.assertEqual(bands, ('R', 'G', 'B'))

    def test_getbbox(self):
        # Arrange
        im = lena()

        # Act
        bbox = im.getbbox()

        # Assert
        self.assertEqual(bbox, (0, 0, 128, 128))


if __name__ == '__main__':
    unittest.main()

# End of file
