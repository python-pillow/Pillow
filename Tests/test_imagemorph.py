# Test the ImageMorphology functionality
from helper import unittest, PillowTestCase, hopper

from PIL import Image
from PIL import ImageMorph


class MorphTests(PillowTestCase):

    def setUp(self):
        self.A = self.string_to_img(
            """
            .......
            .......
            ..111..
            ..111..
            ..111..
            .......
            .......
            """
            )

    def img_to_string(self, im):
        """Turn a (small) binary image into a string representation"""
        chars = '.1'
        width, height = im.size
        return '\n'.join(
            [''.join([chars[im.getpixel((c, r)) > 0] for c in range(width)])
             for r in range(height)])

    def string_to_img(self, image_string):
        """Turn a string image representation into a binary image"""
        rows = [s for s in image_string.replace(' ', '').split('\n')
                if len(s)]
        height = len(rows)
        width = len(rows[0])
        im = Image.new('L', (width, height))
        for i in range(width):
            for j in range(height):
                c = rows[j][i]
                v = c in 'X1'
                im.putpixel((i, j), v)

        return im

    def img_string_normalize(self, im):
        return self.img_to_string(self.string_to_img(im))

    def assert_img_equal(self, A, B):
        self.assertEqual(self.img_to_string(A), self.img_to_string(B))

    def assert_img_equal_img_string(self, A, Bstring):
        self.assertEqual(
            self.img_to_string(A),
            self.img_string_normalize(Bstring))

    def test_str_to_img(self):
        im = Image.open('Tests/images/morph_a.png')
        self.assert_image_equal(self.A, im)

    def create_lut(self):
        for op in (
                'corner', 'dilation4', 'dilation8',
                'erosion4', 'erosion8', 'edge'):
            lb = ImageMorph.LutBuilder(op_name=op)
            lut = lb.build_lut()
            with open('Tests/images/%s.lut' % op, 'wb') as f:
                f.write(lut)

    # create_lut()
    def test_lut(self):
        for op in (
                'corner', 'dilation4', 'dilation8',
                'erosion4', 'erosion8', 'edge'):
            lb = ImageMorph.LutBuilder(op_name=op)
            lut = lb.build_lut()
            with open('Tests/images/%s.lut' % op, 'rb') as f:
                self.assertEqual(lut, bytearray(f.read()))

    # Test the named patterns
    def test_erosion8(self):
        # erosion8
        mop = ImageMorph.MorphOp(op_name='erosion8')
        count, Aout = mop.apply(self.A)
        self.assertEqual(count, 8)
        self.assert_img_equal_img_string(Aout,
                                         """
                                         .......
                                         .......
                                         .......
                                         ...1...
                                         .......
                                         .......
                                         .......
                                         """)

    def test_dialation8(self):
        # dialation8
        mop = ImageMorph.MorphOp(op_name='dilation8')
        count, Aout = mop.apply(self.A)
        self.assertEqual(count, 16)
        self.assert_img_equal_img_string(Aout,
                                         """
                                         .......
                                         .11111.
                                         .11111.
                                         .11111.
                                         .11111.
                                         .11111.
                                         .......
                                         """)

    def test_erosion4(self):
        # erosion4
        mop = ImageMorph.MorphOp(op_name='dilation4')
        count, Aout = mop.apply(self.A)
        self.assertEqual(count, 12)
        self.assert_img_equal_img_string(Aout,
                                         """
                                         .......
                                         ..111..
                                         .11111.
                                         .11111.
                                         .11111.
                                         ..111..
                                         .......
                                         """)

    def test_edge(self):
        # edge
        mop = ImageMorph.MorphOp(op_name='edge')
        count, Aout = mop.apply(self.A)
        self.assertEqual(count, 1)
        self.assert_img_equal_img_string(Aout,
                                         """
                                         .......
                                         .......
                                         ..111..
                                         ..1.1..
                                         ..111..
                                         .......
                                         .......
                                         """)

    def test_corner(self):
        # Create a corner detector pattern
        mop = ImageMorph.MorphOp(patterns=['1:(... ... ...)->0',
                                           '4:(00. 01. ...)->1'])
        count, Aout = mop.apply(self.A)
        self.assertEqual(count, 5)
        self.assert_img_equal_img_string(Aout,
                                         """
                                         .......
                                         .......
                                         ..1.1..
                                         .......
                                         ..1.1..
                                         .......
                                         .......
                                         """)

        # Test the coordinate counting with the same operator
        coords = mop.match(self.A)
        self.assertEqual(len(coords), 4)
        self.assertEqual(tuple(coords), ((2, 2), (4, 2), (2, 4), (4, 4)))

        coords = mop.get_on_pixels(Aout)
        self.assertEqual(len(coords), 4)
        self.assertEqual(tuple(coords), ((2, 2), (4, 2), (2, 4), (4, 4)))

    def test_non_binary_images(self):
        im = hopper('RGB')
        mop = ImageMorph.MorphOp(op_name="erosion8")

        self.assertRaises(Exception, lambda: mop.apply(im))
        self.assertRaises(Exception, lambda: mop.match(im))
        self.assertRaises(Exception, lambda: mop.get_on_pixels(im))


if __name__ == '__main__':
    unittest.main()

# End of file
