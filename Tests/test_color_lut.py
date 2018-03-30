from __future__ import division

import os
from tempfile import NamedTemporaryFile

from PIL import Image, ImageFilter
from helper import unittest, PillowTestCase


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

    def test_wrong_args(self):
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

    def test_correct_args(self):
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

    def test_units_4channels(self):
        g = Image.linear_gradient('L')
        im = Image.merge('RGB', [g, g.transpose(Image.ROTATE_90),
                                 g.transpose(Image.ROTATE_180)])

        # Red channel copied to alpha
        self.assert_image_equal(
            Image.merge('RGBA', (im.split()*2)[:4]),
            im._new(im.im.color_lut_3d('RGBA', Image.LINEAR,
                *self.generate_unit_table(4, 17))))

    def test_copy_alpha_channel(self):
        g = Image.linear_gradient('L')
        im = Image.merge('RGBA', [g, g.transpose(Image.ROTATE_90),
                                  g.transpose(Image.ROTATE_180),
                                  g.transpose(Image.ROTATE_270)])

        self.assert_image_equal(im, im._new(
            im.im.color_lut_3d('RGBA', Image.LINEAR,
                *self.generate_unit_table(3, 17))))

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

        transformed = im._new(im.im.color_lut_3d('RGB', Image.LINEAR,
                3, 2, 2, 2,
                [
                    -3, -3, -3,   5, -3, -3,
                    -3,  5, -3,   5,  5, -3,

                    -3, -3,  5,   5, -3,  5,
                    -3,  5,  5,   5,  5,  5,
                ])).load()
        self.assertEqual(transformed[0, 0], (0, 0, 255))
        self.assertEqual(transformed[50, 50], (0, 0, 255))
        self.assertEqual(transformed[255, 0], (0, 255, 255))
        self.assertEqual(transformed[205, 50], (0, 255, 255))
        self.assertEqual(transformed[0, 255], (255, 0, 0))
        self.assertEqual(transformed[50, 205], (255, 0, 0))
        self.assertEqual(transformed[255, 255], (255, 255, 0))
        self.assertEqual(transformed[205, 205], (255, 255, 0))


class TestColorLut3DFilter(PillowTestCase):
    def test_wrong_args(self):
        with self.assertRaisesRegexp(ValueError, "should be either an integer"):
            ImageFilter.Color3DLUT("small", [1])

        with self.assertRaisesRegexp(ValueError, "should be either an integer"):
            ImageFilter.Color3DLUT((11, 11), [1])

        with self.assertRaisesRegexp(ValueError, r"in \[2, 65\] range"):
            ImageFilter.Color3DLUT((11, 11, 1), [1])

        with self.assertRaisesRegexp(ValueError, r"in \[2, 65\] range"):
            ImageFilter.Color3DLUT((11, 11, 66), [1])

        with self.assertRaisesRegexp(ValueError, "table should have .+ items"):
            ImageFilter.Color3DLUT((3, 3, 3), [1, 1, 1])

        with self.assertRaisesRegexp(ValueError, "table should have .+ items"):
            ImageFilter.Color3DLUT((3, 3, 3), [[1, 1, 1]] * 2)

        with self.assertRaisesRegexp(ValueError, "should have a length of 4"):
            ImageFilter.Color3DLUT((3, 3, 3), [[1, 1, 1]] * 27, channels=4)

        with self.assertRaisesRegexp(ValueError, "should have a length of 3"):
            ImageFilter.Color3DLUT((2, 2, 2), [[1, 1]] * 8)

    def test_convert_table(self):
        lut = ImageFilter.Color3DLUT(2, [0, 1, 2] * 8)
        self.assertEqual(tuple(lut.size), (2, 2, 2))
        self.assertEqual(lut.name, "Color 3D LUT")

        lut = ImageFilter.Color3DLUT((2, 2, 2), [
            (0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11),
            (12, 13, 14), (15, 16, 17), (18, 19, 20), (21, 22, 23)])
        self.assertEqual(tuple(lut.size), (2, 2, 2))
        self.assertEqual(lut.table, list(range(24)))

        lut = ImageFilter.Color3DLUT((2, 2, 2), [(0, 1, 2, 3)] * 8,
            channels=4)

    def test_generate(self):
        lut = ImageFilter.Color3DLUT.generate(5, lambda r, g, b: (r, g, b))
        self.assertEqual(tuple(lut.size), (5, 5, 5))
        self.assertEqual(lut.name, "Color 3D LUT")
        self.assertEqual(lut.table[:24], [
            0.0, 0.0, 0.0,  0.25, 0.0, 0.0,  0.5, 0.0, 0.0,  0.75, 0.0, 0.0,
            1.0, 0.0, 0.0,  0.0, 0.25, 0.0,  0.25, 0.25, 0.0,  0.5, 0.25, 0.0])

        g = Image.linear_gradient('L')
        im = Image.merge('RGB', [g, g.transpose(Image.ROTATE_90),
                                 g.transpose(Image.ROTATE_180)])
        self.assertEqual(im, im.filter(lut))

        lut = ImageFilter.Color3DLUT.generate(5, channels=4,
            callback=lambda r, g, b: (b, r, g, (r+g+b) / 2))
        self.assertEqual(tuple(lut.size), (5, 5, 5))
        self.assertEqual(lut.name, "Color 3D LUT")
        self.assertEqual(lut.table[:24], [
            0.0, 0.0, 0.0, 0.0,  0.0, 0.25, 0.0, 0.125,  0.0, 0.5, 0.0, 0.25,
            0.0, 0.75, 0.0, 0.375,  0.0, 1.0, 0.0, 0.5,  0.0, 0.0, 0.25, 0.125])

        with self.assertRaisesRegexp(ValueError, "should have a length of 3"):
            ImageFilter.Color3DLUT.generate(5, lambda r, g, b: (r, g, b, r))

        with self.assertRaisesRegexp(ValueError, "should have a length of 4"):
            ImageFilter.Color3DLUT.generate(5, channels=4,
                callback=lambda r, g, b: (r, g, b))

    def test_from_cube_file_minimal(self):
        lut = ImageFilter.Color3DLUT.from_cube_file([
            "LUT_3D_SIZE 2",
            "",
            "0    0 0.031",
            "0.96 0 0.031",
            "0    1 0.031",
            "0.96 1 0.031",
            "0    0 0.931",
            "0.96 0 0.931",
            "0    1 0.931",
            "0.96 1 0.931",
        ])
        self.assertEqual(tuple(lut.size), (2, 2, 2))
        self.assertEqual(lut.name, "Color 3D LUT")
        self.assertEqual(lut.table[:12], [
            0, 0, 0.031,  0.96, 0, 0.031,  0, 1, 0.031,  0.96, 1, 0.031])

    def test_from_cube_file_parser(self):
        lut = ImageFilter.Color3DLUT.from_cube_file([
            " # Comment",
            'TITLE "LUT name from file"',
            "  LUT_3D_SIZE 2 3 4",
            " SKIP THIS",
            " # Comment",
            "CHANNELS 4",
            "",
        ] + [
            " # Comment",
            "0    0 0.031 1",
            "0.96 0 0.031 1",
            "",
            "0    1 0.031 1",
            "0.96 1 0.031 1",
        ] * 6, target_mode='HSV')
        self.assertEqual(tuple(lut.size), (2, 3, 4))
        self.assertEqual(lut.channels, 4)
        self.assertEqual(lut.name, "LUT name from file")
        self.assertEqual(lut.mode, 'HSV')
        self.assertEqual(lut.table[:12], [
            0, 0, 0.031, 1,  0.96, 0, 0.031, 1,  0, 1, 0.031, 1])

    def test_from_cube_file_errors(self):
        with self.assertRaisesRegexp(ValueError, "No size found"):
            lut = ImageFilter.Color3DLUT.from_cube_file([
                'TITLE "LUT name from file"',
                "",
            ] + [
                "0    0 0.031",
                "0.96 0 0.031",
            ] * 3)

        with self.assertRaisesRegexp(ValueError, "number of colors on line 4"):
            lut = ImageFilter.Color3DLUT.from_cube_file([
                'LUT_3D_SIZE 2',
                "",
            ] + [
                "0    0 0.031",
                "0.96 0 0.031 1",
            ] * 3)

        with self.assertRaisesRegexp(ValueError, "Not a number on line 3"):
            lut = ImageFilter.Color3DLUT.from_cube_file([
                'LUT_3D_SIZE 2',
                "",
            ] + [
                "0  green 0.031",
                "0.96 0 0.031",
            ] * 3)

    def test_from_cube_file_filename(self):
        with NamedTemporaryFile('w+t', delete=False) as f:
            f.write(
                "LUT_3D_SIZE 2\n"
                "\n"
                "0    0 0.031\n"
                "0.96 0 0.031\n"
                "0    1 0.031\n"
                "0.96 1 0.031\n"
                "0    0 0.931\n"
                "0.96 0 0.931\n"
                "0    1 0.931\n"
                "0.96 1 0.931\n"
            )

        try:
            lut = ImageFilter.Color3DLUT.from_cube_file(f.name)
            self.assertEqual(tuple(lut.size), (2, 2, 2))
            self.assertEqual(lut.name, "Color 3D LUT")
            self.assertEqual(lut.table[:12], [
                0, 0, 0.031,  0.96, 0, 0.031,  0, 1, 0.031,  0.96, 1, 0.031])
        finally:
            os.unlink(f.name)


if __name__ == '__main__':
    unittest.main()
