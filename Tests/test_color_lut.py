from __future__ import division
from helper import unittest, PillowTestCase

import time
from PIL import Image


class TestColorLut3DCoreAPI(PillowTestCase):
    def generate_unit_table(self, channels, size):
        if isinstance(size, tuple):
            size1D, size2D, size3D = size
        else:
            size1D, size2D, size3D = (size, size, size)

        table = [
            [
                r / float(size1D-1) if size1D != 1 else 0,
                g / float(size2D-1) if size2D != 1 else 0,
                b / float(size3D-1) if size3D != 1 else 0,
                r / float(size1D-1) if size1D != 1 else 0,
                g / float(size2D-1) if size2D != 1 else 0,
            ][:channels]
            for b in range(size3D)
                for g in range(size2D)
                    for r in range(size1D)
        ]
        return (
            channels, size1D, size2D, size3D,
            [item for sublist in table for item in sublist])

    def test_wrong_arguments(self):
        im = Image.new('RGB', (10, 10), 0)

        with self.assertRaisesRegexp(ValueError, "filter"):
            im.im.color_lut_3d('RGB', Image.CUBIC,
                *self.generate_unit_table(3, 3))

        with self.assertRaisesRegexp(ValueError, "image mode"):
            im.im.color_lut_3d('wrong', Image.LINEAR,
                *self.generate_unit_table(3, 3))

        with self.assertRaisesRegexp(ValueError, "table_channels"):
            im.im.color_lut_3d('RGB', Image.LINEAR,
                *self.generate_unit_table(5, 3))

        with self.assertRaisesRegexp(ValueError, "table_channels"):
            im.im.color_lut_3d('RGB', Image.LINEAR,
                *self.generate_unit_table(1, 3))

        with self.assertRaisesRegexp(ValueError, "table_channels"):
            im.im.color_lut_3d('RGB', Image.LINEAR,
                *self.generate_unit_table(2, 3))

        with self.assertRaisesRegexp(ValueError, "Table size"):
            im.im.color_lut_3d('RGB', Image.LINEAR,
                *self.generate_unit_table(3, (1, 3, 3)))

        with self.assertRaisesRegexp(ValueError, "Table size"):
            im.im.color_lut_3d('RGB', Image.LINEAR,
                *self.generate_unit_table(3, (66, 3, 3)))

        with self.assertRaisesRegexp(ValueError, r"size1D \* size2D \* size3D"):
            im.im.color_lut_3d('RGB', Image.LINEAR,
                3, 2, 2, 2, [0, 0, 0] * 7)

        with self.assertRaisesRegexp(ValueError, r"size1D \* size2D \* size3D"):
            im.im.color_lut_3d('RGB', Image.LINEAR,
                3, 2, 2, 2, [0, 0, 0] * 9)

    def test_correct_arguments(self):
        im = Image.new('RGB', (10, 10), 0)

        im.im.color_lut_3d('RGB', Image.LINEAR,
            *self.generate_unit_table(3, 3))

        im.im.color_lut_3d('CMYK', Image.LINEAR,
            *self.generate_unit_table(4, 3))

        im.im.color_lut_3d('RGB', Image.LINEAR,
            *self.generate_unit_table(3, (2, 3, 3)))

        im.im.color_lut_3d('RGB', Image.LINEAR,
            *self.generate_unit_table(3, (65, 3, 3)))

        im.im.color_lut_3d('RGB', Image.LINEAR,
            *self.generate_unit_table(3, (3, 65, 3)))

        im.im.color_lut_3d('RGB', Image.LINEAR,
            *self.generate_unit_table(3, (3, 3, 65)))

    def test_wrong_mode(self):
        with self.assertRaisesRegexp(ValueError, "wrong mode"):
            im = Image.new('L', (10, 10), 0)
            im.im.color_lut_3d('RGB', Image.LINEAR,
                *self.generate_unit_table(3, 3))

        with self.assertRaisesRegexp(ValueError, "wrong mode"):
            im = Image.new('RGB', (10, 10), 0)
            im.im.color_lut_3d('L', Image.LINEAR,
                *self.generate_unit_table(3, 3))

        with self.assertRaisesRegexp(ValueError, "wrong mode"):
            im = Image.new('L', (10, 10), 0)
            im.im.color_lut_3d('L', Image.LINEAR,
                *self.generate_unit_table(3, 3))

        with self.assertRaisesRegexp(ValueError, "wrong mode"):
            im = Image.new('RGB', (10, 10), 0)
            im.im.color_lut_3d('RGBA', Image.LINEAR,
                *self.generate_unit_table(3, 3))

        with self.assertRaisesRegexp(ValueError, "wrong mode"):
            im = Image.new('RGB', (10, 10), 0)
            im.im.color_lut_3d('RGB', Image.LINEAR,
                *self.generate_unit_table(4, 3))

    def test_correct_mode(self):
        im = Image.new('RGBA', (10, 10), 0)
        im.im.color_lut_3d('RGBA', Image.LINEAR,
            *self.generate_unit_table(3, 3))

        im = Image.new('RGBA', (10, 10), 0)
        im.im.color_lut_3d('RGBA', Image.LINEAR,
            *self.generate_unit_table(4, 3))

        im = Image.new('RGB', (10, 10), 0)
        im.im.color_lut_3d('HSV', Image.LINEAR,
            *self.generate_unit_table(3, 3))

        im = Image.new('RGB', (10, 10), 0)
        im.im.color_lut_3d('RGBA', Image.LINEAR,
            *self.generate_unit_table(4, 3))

    def test_units(self):
        g = Image.linear_gradient('L')
        im = Image.merge('RGB', [g, g.transpose(Image.ROTATE_90),
                                 g.transpose(Image.ROTATE_180)])

        # Fast test with small cubes
        for size in [2, 3, 5, 7, 11, 16, 17]:
            self.assert_image_equal(im, im._new(
                im.im.color_lut_3d('RGB', Image.LINEAR,
                    *self.generate_unit_table(3, size))))

        # Not so fast
        self.assert_image_equal(im, im._new(
            im.im.color_lut_3d('RGB', Image.LINEAR,
                *self.generate_unit_table(3, (2, 2, 65)))))

    def test_channels_order(self):
        g = Image.linear_gradient('L')
        im = Image.merge('RGB', [g, g.transpose(Image.ROTATE_90),
                                 g.transpose(Image.ROTATE_180)])

        # Reverse channels by splitting and using table
        self.assert_image_equal(
            Image.merge('RGB', im.split()[::-1]),
            im._new(im.im.color_lut_3d('RGB', Image.LINEAR,
                3, 2, 2, 2, [
                    0, 0, 0,  0, 0, 1,
                    0, 1, 0,  0, 1, 1,

                    1, 0, 0,  1, 0, 1,
                    1, 1, 0,  1, 1, 1,
                ])))

    def test_overflow(self):
        g = Image.linear_gradient('L')
        im = Image.merge('RGB', [g, g.transpose(Image.ROTATE_90),
                                 g.transpose(Image.ROTATE_180)])

        transformed = im._new(im.im.color_lut_3d('RGB', Image.LINEAR,
                3, 2, 2, 2,
                [
                    -1, -1, -1,   2, -1, -1,
                    -1,  2, -1,   2,  2, -1,

                    -1, -1,  2,   2, -1,  2,
                    -1,  2,  2,   2,  2,  2,
                ])).load()

        self.assertEqual(transformed[0, 0], (0, 0, 255))
        self.assertEqual(transformed[50, 50], (0, 0, 255))
        self.assertEqual(transformed[255, 0], (0, 255, 255))
        self.assertEqual(transformed[205, 50], (0, 255, 255))
        self.assertEqual(transformed[0, 255], (255, 0, 0))
        self.assertEqual(transformed[50, 205], (255, 0, 0))
        self.assertEqual(transformed[255, 255], (255, 255, 0))
        self.assertEqual(transformed[205, 205], (255, 255, 0))


if __name__ == '__main__':
    unittest.main()
