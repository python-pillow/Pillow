from __future__ import annotations

from array import array
from types import ModuleType

import pytest

from PIL import Image, ImageFilter

from .helper import assert_image_equal

numpy: ModuleType | None
try:
    import numpy
except ImportError:
    numpy = None


class TestColorLut3DCoreAPI:
    def generate_identity_table(
        self, channels: int, size: int | tuple[int, int, int]
    ) -> tuple[int, int, int, int, list[float]]:
        if isinstance(size, tuple):
            size_1d, size_2d, size_3d = size
        else:
            size_1d, size_2d, size_3d = (size, size, size)

        table = [
            [
                r / (size_1d - 1) if size_1d != 1 else 0,
                g / (size_2d - 1) if size_2d != 1 else 0,
                b / (size_3d - 1) if size_3d != 1 else 0,
                r / (size_1d - 1) if size_1d != 1 else 0,
                g / (size_2d - 1) if size_2d != 1 else 0,
            ][:channels]
            for b in range(size_3d)
            for g in range(size_2d)
            for r in range(size_1d)
        ]
        return (
            channels,
            size_1d,
            size_2d,
            size_3d,
            [item for sublist in table for item in sublist],
        )

    def test_wrong_args(self) -> None:
        im = Image.new("RGB", (10, 10), 0)

        with pytest.raises(ValueError, match="filter"):
            im.im.color_lut_3d(
                "RGB", Image.Resampling.BICUBIC, *self.generate_identity_table(3, 3)
            )

        with pytest.raises(ValueError, match="image mode"):
            im.im.color_lut_3d(
                "wrong", Image.Resampling.BILINEAR, *self.generate_identity_table(3, 3)
            )

        with pytest.raises(ValueError, match="table_channels"):
            im.im.color_lut_3d(
                "RGB", Image.Resampling.BILINEAR, *self.generate_identity_table(5, 3)
            )

        with pytest.raises(ValueError, match="table_channels"):
            im.im.color_lut_3d(
                "RGB", Image.Resampling.BILINEAR, *self.generate_identity_table(1, 3)
            )

        with pytest.raises(ValueError, match="table_channels"):
            im.im.color_lut_3d(
                "RGB", Image.Resampling.BILINEAR, *self.generate_identity_table(2, 3)
            )

        with pytest.raises(ValueError, match="Table size"):
            im.im.color_lut_3d(
                "RGB",
                Image.Resampling.BILINEAR,
                *self.generate_identity_table(3, (1, 3, 3)),
            )

        with pytest.raises(ValueError, match="Table size"):
            im.im.color_lut_3d(
                "RGB",
                Image.Resampling.BILINEAR,
                *self.generate_identity_table(3, (66, 3, 3)),
            )

        with pytest.raises(ValueError, match=r"size1D \* size2D \* size3D"):
            im.im.color_lut_3d(
                "RGB", Image.Resampling.BILINEAR, 3, 2, 2, 2, [0, 0, 0] * 7
            )

        with pytest.raises(ValueError, match=r"size1D \* size2D \* size3D"):
            im.im.color_lut_3d(
                "RGB", Image.Resampling.BILINEAR, 3, 2, 2, 2, [0, 0, 0] * 9
            )

        with pytest.raises(TypeError):
            im.im.color_lut_3d(
                "RGB", Image.Resampling.BILINEAR, 3, 2, 2, 2, [0, 0, "0"] * 8
            )

        with pytest.raises(TypeError):
            im.im.color_lut_3d("RGB", Image.Resampling.BILINEAR, 3, 2, 2, 2, 16)

    @pytest.mark.parametrize(
        "lut_mode, table_channels, table_size",
        [
            ("RGB", 3, 3),
            ("CMYK", 4, 3),
            ("RGB", 3, (2, 3, 3)),
            ("RGB", 3, (65, 3, 3)),
            ("RGB", 3, (3, 65, 3)),
            ("RGB", 3, (2, 3, 65)),
        ],
    )
    def test_correct_args(
        self, lut_mode: str, table_channels: int, table_size: int | tuple[int, int, int]
    ) -> None:
        im = Image.new("RGB", (10, 10), 0)
        im.im.color_lut_3d(
            lut_mode,
            Image.Resampling.BILINEAR,
            *self.generate_identity_table(table_channels, table_size),
        )

    @pytest.mark.parametrize(
        "image_mode, lut_mode, table_channels, table_size",
        [
            ("L", "RGB", 3, 3),
            ("RGB", "L", 3, 3),
            ("L", "L", 3, 3),
            ("RGB", "RGBA", 3, 3),
            ("RGB", "RGB", 4, 3),
        ],
    )
    def test_wrong_mode(
        self, image_mode: str, lut_mode: str, table_channels: int, table_size: int
    ) -> None:
        with pytest.raises(ValueError, match="wrong mode"):
            im = Image.new(image_mode, (10, 10), 0)
            im.im.color_lut_3d(
                lut_mode,
                Image.Resampling.BILINEAR,
                *self.generate_identity_table(table_channels, table_size),
            )

    @pytest.mark.parametrize(
        "image_mode, lut_mode, table_channels, table_size",
        [
            ("RGBA", "RGBA", 3, 3),
            ("RGBA", "RGBA", 4, 3),
            ("RGB", "HSV", 3, 3),
            ("RGB", "RGBA", 4, 3),
        ],
    )
    def test_correct_mode(
        self, image_mode: str, lut_mode: str, table_channels: int, table_size: int
    ) -> None:
        im = Image.new(image_mode, (10, 10), 0)
        im.im.color_lut_3d(
            lut_mode,
            Image.Resampling.BILINEAR,
            *self.generate_identity_table(table_channels, table_size),
        )

    def test_identities(self) -> None:
        g = Image.linear_gradient("L")
        im = Image.merge(
            "RGB",
            [
                g,
                g.transpose(Image.Transpose.ROTATE_90),
                g.transpose(Image.Transpose.ROTATE_180),
            ],
        )

        # Fast test with small cubes
        for size in [2, 3, 5, 7, 11, 16, 17]:
            assert_image_equal(
                im,
                im._new(
                    im.im.color_lut_3d(
                        "RGB",
                        Image.Resampling.BILINEAR,
                        *self.generate_identity_table(3, size),
                    )
                ),
            )

        # Not so fast
        assert_image_equal(
            im,
            im._new(
                im.im.color_lut_3d(
                    "RGB",
                    Image.Resampling.BILINEAR,
                    *self.generate_identity_table(3, (2, 2, 65)),
                )
            ),
        )

    def test_identities_4_channels(self) -> None:
        g = Image.linear_gradient("L")
        im = Image.merge(
            "RGB",
            [
                g,
                g.transpose(Image.Transpose.ROTATE_90),
                g.transpose(Image.Transpose.ROTATE_180),
            ],
        )

        # Red channel copied to alpha
        assert_image_equal(
            Image.merge("RGBA", (im.split() * 2)[:4]),
            im._new(
                im.im.color_lut_3d(
                    "RGBA",
                    Image.Resampling.BILINEAR,
                    *self.generate_identity_table(4, 17),
                )
            ),
        )

    def test_copy_alpha_channel(self) -> None:
        g = Image.linear_gradient("L")
        im = Image.merge(
            "RGBA",
            [
                g,
                g.transpose(Image.Transpose.ROTATE_90),
                g.transpose(Image.Transpose.ROTATE_180),
                g.transpose(Image.Transpose.ROTATE_270),
            ],
        )

        assert_image_equal(
            im,
            im._new(
                im.im.color_lut_3d(
                    "RGBA",
                    Image.Resampling.BILINEAR,
                    *self.generate_identity_table(3, 17),
                )
            ),
        )

    def test_channels_order(self) -> None:
        g = Image.linear_gradient("L")
        im = Image.merge(
            "RGB",
            [
                g,
                g.transpose(Image.Transpose.ROTATE_90),
                g.transpose(Image.Transpose.ROTATE_180),
            ],
        )

        # Reverse channels by splitting and using table
        # fmt: off
        assert_image_equal(
            Image.merge('RGB', im.split()[::-1]),
            im._new(im.im.color_lut_3d('RGB', Image.Resampling.BILINEAR,
                    3, 2, 2, 2, [
                        0, 0, 0,  0, 0, 1,
                        0, 1, 0,  0, 1, 1,

                        1, 0, 0,  1, 0, 1,
                        1, 1, 0,  1, 1, 1,
                    ])))
        # fmt: on

    def test_overflow(self) -> None:
        g = Image.linear_gradient("L")
        im = Image.merge(
            "RGB",
            [
                g,
                g.transpose(Image.Transpose.ROTATE_90),
                g.transpose(Image.Transpose.ROTATE_180),
            ],
        )

        # fmt: off
        transformed = im._new(im.im.color_lut_3d('RGB', Image.Resampling.BILINEAR,
                              3, 2, 2, 2,
                              [
                                  -1, -1, -1,   2, -1, -1,
                                  -1,  2, -1,   2,  2, -1,

                                  -1, -1,  2,   2, -1,  2,
                                  -1,  2,  2,   2,  2,  2,
                              ])).load()
        # fmt: on
        assert transformed is not None
        assert transformed[0, 0] == (0, 0, 255)
        assert transformed[50, 50] == (0, 0, 255)
        assert transformed[255, 0] == (0, 255, 255)
        assert transformed[205, 50] == (0, 255, 255)
        assert transformed[0, 255] == (255, 0, 0)
        assert transformed[50, 205] == (255, 0, 0)
        assert transformed[255, 255] == (255, 255, 0)
        assert transformed[205, 205] == (255, 255, 0)

        # fmt: off
        transformed = im._new(im.im.color_lut_3d('RGB', Image.Resampling.BILINEAR,
                              3, 2, 2, 2,
                              [
                                  -3, -3, -3,   5, -3, -3,
                                  -3,  5, -3,   5,  5, -3,

                                  -3, -3,  5,   5, -3,  5,
                                  -3,  5,  5,   5,  5,  5,
                              ])).load()
        # fmt: on
        assert transformed is not None
        assert transformed[0, 0] == (0, 0, 255)
        assert transformed[50, 50] == (0, 0, 255)
        assert transformed[255, 0] == (0, 255, 255)
        assert transformed[205, 50] == (0, 255, 255)
        assert transformed[0, 255] == (255, 0, 0)
        assert transformed[50, 205] == (255, 0, 0)
        assert transformed[255, 255] == (255, 255, 0)
        assert transformed[205, 205] == (255, 255, 0)


class TestColorLut3DFilter:
    def test_wrong_args(self) -> None:
        with pytest.raises(ValueError, match="should be either an integer"):
            ImageFilter.Color3DLUT("small", [1])  # type: ignore[arg-type]

        with pytest.raises(ValueError, match="should be either an integer"):
            ImageFilter.Color3DLUT((11, 11), [1])  # type: ignore[arg-type]

        with pytest.raises(ValueError, match=r"in \[2, 65\] range"):
            ImageFilter.Color3DLUT((11, 11, 1), [1])

        with pytest.raises(ValueError, match=r"in \[2, 65\] range"):
            ImageFilter.Color3DLUT((11, 11, 66), [1])

        with pytest.raises(ValueError, match="table should have .+ items"):
            ImageFilter.Color3DLUT((3, 3, 3), [1, 1, 1])

        with pytest.raises(ValueError, match="table should have .+ items"):
            ImageFilter.Color3DLUT((3, 3, 3), [[1, 1, 1]] * 2)

        with pytest.raises(ValueError, match="should have a length of 4"):
            ImageFilter.Color3DLUT((3, 3, 3), [[1, 1, 1]] * 27, channels=4)

        with pytest.raises(ValueError, match="should have a length of 3"):
            ImageFilter.Color3DLUT((2, 2, 2), [[1, 1]] * 8)

        with pytest.raises(ValueError, match="Only 3 or 4 output"):
            ImageFilter.Color3DLUT((2, 2, 2), [[1, 1]] * 8, channels=2)

    def test_convert_table(self) -> None:
        lut = ImageFilter.Color3DLUT(2, [0, 1, 2] * 8)
        assert tuple(lut.size) == (2, 2, 2)
        assert lut.name == "Color 3D LUT"

        # fmt: off
        lut = ImageFilter.Color3DLUT((2, 2, 2), [
            (0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11),
            (12, 13, 14), (15, 16, 17), (18, 19, 20), (21, 22, 23)])
        # fmt: on
        assert tuple(lut.size) == (2, 2, 2)
        assert lut.table == list(range(24))

        lut = ImageFilter.Color3DLUT((2, 2, 2), [(0, 1, 2, 3)] * 8, channels=4)
        assert tuple(lut.size) == (2, 2, 2)
        assert lut.table == list(range(4)) * 8

    @pytest.mark.skipif(numpy is None, reason="NumPy not installed")
    def test_numpy_sources(self) -> None:
        assert numpy is not None
        table = numpy.ones((5, 6, 7, 3), dtype=numpy.float16)
        with pytest.raises(ValueError, match="should have either channels"):
            lut = ImageFilter.Color3DLUT((5, 6, 7), table)

        table = numpy.ones((7, 6, 5, 3), dtype=numpy.float16)
        lut = ImageFilter.Color3DLUT((5, 6, 7), table)
        assert isinstance(lut.table, numpy.ndarray)
        assert lut.table.dtype == table.dtype
        assert lut.table.shape == (table.size,)

        table = numpy.ones((7 * 6 * 5, 3), dtype=numpy.float16)
        lut = ImageFilter.Color3DLUT((5, 6, 7), table)
        assert lut.table.shape == (table.size,)

        table = numpy.ones((7 * 6 * 5 * 3), dtype=numpy.float16)
        lut = ImageFilter.Color3DLUT((5, 6, 7), table)
        assert lut.table.shape == (table.size,)

        # Check application
        Image.new("RGB", (10, 10), 0).filter(lut)

        # Check copy
        table[0] = 33
        assert lut.table[0] == 1

        # Check not copy
        table = numpy.ones((7 * 6 * 5 * 3), dtype=numpy.float16)
        lut = ImageFilter.Color3DLUT((5, 6, 7), table, _copy_table=False)
        table[0] = 33
        assert lut.table[0] == 33

    @pytest.mark.skipif(numpy is None, reason="NumPy not installed")
    def test_numpy_formats(self) -> None:
        assert numpy is not None
        g = Image.linear_gradient("L")
        im = Image.merge(
            "RGB",
            [
                g,
                g.transpose(Image.Transpose.ROTATE_90),
                g.transpose(Image.Transpose.ROTATE_180),
            ],
        )

        lut = ImageFilter.Color3DLUT.generate((7, 9, 11), lambda r, g, b: (r, g, b))
        lut.table = numpy.array(lut.table, dtype=numpy.float32)[:-1]
        with pytest.raises(ValueError, match="should have table_channels"):
            im.filter(lut)

        lut = ImageFilter.Color3DLUT.generate((7, 9, 11), lambda r, g, b: (r, g, b))
        lut.table = numpy.array(lut.table, dtype=numpy.float32).reshape((7 * 9 * 11), 3)
        with pytest.raises(ValueError, match="should have table_channels"):
            im.filter(lut)

        lut = ImageFilter.Color3DLUT.generate((7, 9, 11), lambda r, g, b: (r, g, b))
        lut.table = numpy.array(lut.table, dtype=numpy.float16)
        assert_image_equal(im, im.filter(lut))

        lut = ImageFilter.Color3DLUT.generate((7, 9, 11), lambda r, g, b: (r, g, b))
        lut.table = numpy.array(lut.table, dtype=numpy.float32)
        assert_image_equal(im, im.filter(lut))

        lut = ImageFilter.Color3DLUT.generate((7, 9, 11), lambda r, g, b: (r, g, b))
        lut.table = numpy.array(lut.table, dtype=numpy.float64)
        assert_image_equal(im, im.filter(lut))

        lut = ImageFilter.Color3DLUT.generate((7, 9, 11), lambda r, g, b: (r, g, b))
        lut.table = numpy.array(lut.table, dtype=numpy.int32)
        im.filter(lut)
        lut.table = numpy.array(lut.table, dtype=numpy.int8)
        im.filter(lut)

    def test_repr(self) -> None:
        lut = ImageFilter.Color3DLUT(2, [0, 1, 2] * 8)
        assert repr(lut) == "<Color3DLUT from list size=2x2x2 channels=3>"

        lut = ImageFilter.Color3DLUT(
            (3, 4, 5),
            array("f", [0, 0, 0, 0] * (3 * 4 * 5)),
            channels=4,
            target_mode="YCbCr",
            _copy_table=False,
        )
        assert (
            repr(lut)
            == "<Color3DLUT from array size=3x4x5 channels=4 target_mode=YCbCr>"
        )


class TestGenerateColorLut3D:
    def test_wrong_channels_count(self) -> None:
        with pytest.raises(ValueError, match="3 or 4 output channels"):
            ImageFilter.Color3DLUT.generate(
                5, channels=2, callback=lambda r, g, b: (r, g, b)
            )

        with pytest.raises(ValueError, match="should have either channels"):
            ImageFilter.Color3DLUT.generate(5, lambda r, g, b: (r, g, b, r))

        with pytest.raises(ValueError, match="should have either channels"):
            ImageFilter.Color3DLUT.generate(
                5, channels=4, callback=lambda r, g, b: (r, g, b)
            )

    def test_3_channels(self) -> None:
        lut = ImageFilter.Color3DLUT.generate(5, lambda r, g, b: (r, g, b))
        assert tuple(lut.size) == (5, 5, 5)
        assert lut.name == "Color 3D LUT"
        # fmt: off
        assert lut.table[:24] == [
            0.0, 0.0, 0.0,  0.25, 0.0, 0.0,  0.5, 0.0, 0.0,  0.75, 0.0, 0.0,
            1.0, 0.0, 0.0,  0.0, 0.25, 0.0,  0.25, 0.25, 0.0,  0.5, 0.25, 0.0]
        # fmt: on

    def test_4_channels(self) -> None:
        lut = ImageFilter.Color3DLUT.generate(
            5, channels=4, callback=lambda r, g, b: (b, r, g, (r + g + b) / 2)
        )
        assert tuple(lut.size) == (5, 5, 5)
        assert lut.name == "Color 3D LUT"
        # fmt: off
        assert lut.table[:24] == [
            0.0, 0.0, 0.0, 0.0,  0.0, 0.25, 0.0, 0.125,  0.0, 0.5, 0.0, 0.25,
            0.0, 0.75, 0.0, 0.375,  0.0, 1.0, 0.0, 0.5,  0.0, 0.0, 0.25, 0.125
        ]
        # fmt: on

    def test_apply(self) -> None:
        lut = ImageFilter.Color3DLUT.generate(5, lambda r, g, b: (r, g, b))

        g = Image.linear_gradient("L")
        im = Image.merge(
            "RGB",
            [
                g,
                g.transpose(Image.Transpose.ROTATE_90),
                g.transpose(Image.Transpose.ROTATE_180),
            ],
        )
        assert im == im.filter(lut)


class TestTransformColorLut3D:
    def test_wrong_args(self) -> None:
        source = ImageFilter.Color3DLUT.generate(5, lambda r, g, b: (r, g, b))

        with pytest.raises(ValueError, match="Only 3 or 4 output"):
            source.transform(lambda r, g, b: (r, g, b), channels=8)

        with pytest.raises(ValueError, match="should have either channels"):
            source.transform(lambda r, g, b: (r, g, b), channels=4)

        with pytest.raises(ValueError, match="should have either channels"):
            source.transform(lambda r, g, b: (r, g, b, 1))

        with pytest.raises(TypeError):
            source.transform(lambda r, g, b, a: (r, g, b))

    def test_target_mode(self) -> None:
        source = ImageFilter.Color3DLUT.generate(
            2, lambda r, g, b: (r, g, b), target_mode="HSV"
        )

        lut = source.transform(lambda r, g, b: (r, g, b))
        assert lut.mode == "HSV"

        lut = source.transform(lambda r, g, b: (r, g, b), target_mode="RGB")
        assert lut.mode == "RGB"

    def test_3_to_3_channels(self) -> None:
        source = ImageFilter.Color3DLUT.generate((3, 4, 5), lambda r, g, b: (r, g, b))
        lut = source.transform(lambda r, g, b: (r * r, g * g, b * b))
        assert tuple(lut.size) == tuple(source.size)
        assert len(lut.table) == len(source.table)
        assert lut.table != source.table
        assert lut.table[:10] == [0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]

    def test_3_to_4_channels(self) -> None:
        source = ImageFilter.Color3DLUT.generate((6, 5, 4), lambda r, g, b: (r, g, b))
        lut = source.transform(lambda r, g, b: (r * r, g * g, b * b, 1), channels=4)
        assert tuple(lut.size) == tuple(source.size)
        assert len(lut.table) != len(source.table)
        assert lut.table != source.table
        # fmt: off
        assert lut.table[:16] == [
            0.0, 0.0, 0.0, 1,  0.2**2, 0.0, 0.0, 1,
            0.4**2, 0.0, 0.0, 1,  0.6**2, 0.0, 0.0, 1]
        # fmt: on

    def test_4_to_3_channels(self) -> None:
        source = ImageFilter.Color3DLUT.generate(
            (3, 6, 5), lambda r, g, b: (r, g, b, 1), channels=4
        )
        lut = source.transform(
            lambda r, g, b, a: (a - r * r, a - g * g, a - b * b), channels=3
        )
        assert tuple(lut.size) == tuple(source.size)
        assert len(lut.table) != len(source.table)
        assert lut.table != source.table
        # fmt: off
        assert lut.table[:18] == [
            1.0, 1.0, 1.0,  0.75, 1.0, 1.0,  0.0, 1.0, 1.0,
            1.0, 0.96, 1.0,  0.75, 0.96, 1.0,  0.0, 0.96, 1.0]
        # fmt: on

    def test_4_to_4_channels(self) -> None:
        source = ImageFilter.Color3DLUT.generate(
            (6, 5, 4), lambda r, g, b: (r, g, b, 1), channels=4
        )
        lut = source.transform(lambda r, g, b, a: (r * r, g * g, b * b, a - 0.5))
        assert tuple(lut.size) == tuple(source.size)
        assert len(lut.table) == len(source.table)
        assert lut.table != source.table
        # fmt: off
        assert lut.table[:16] == [
            0.0, 0.0, 0.0, 0.5,  0.2**2, 0.0, 0.0, 0.5,
            0.4**2, 0.0, 0.0, 0.5,  0.6**2, 0.0, 0.0, 0.5]
        # fmt: on

    def test_with_normals_3_channels(self) -> None:
        source = ImageFilter.Color3DLUT.generate(
            (6, 5, 4), lambda r, g, b: (r * r, g * g, b * b)
        )
        lut = source.transform(
            lambda nr, ng, nb, r, g, b: (nr - r, ng - g, nb - b), with_normals=True
        )
        assert tuple(lut.size) == tuple(source.size)
        assert len(lut.table) == len(source.table)
        assert lut.table != source.table
        # fmt: off
        assert lut.table[:18] == [
            0.0, 0.0, 0.0,  0.16, 0.0, 0.0,  0.24, 0.0, 0.0,
            0.24, 0.0, 0.0,  0.8 - (0.8**2), 0, 0,  0, 0, 0]
        # fmt: on

    def test_with_normals_4_channels(self) -> None:
        source = ImageFilter.Color3DLUT.generate(
            (3, 6, 5), lambda r, g, b: (r * r, g * g, b * b, 1), channels=4
        )
        lut = source.transform(
            lambda nr, ng, nb, r, g, b, a: (nr - r, ng - g, nb - b, a - 0.5),
            with_normals=True,
        )
        assert tuple(lut.size) == tuple(source.size)
        assert len(lut.table) == len(source.table)
        assert lut.table != source.table
        # fmt: off
        assert lut.table[:16] == [
            0.0, 0.0, 0.0, 0.5,  0.25, 0.0, 0.0, 0.5,
            0.0, 0.0, 0.0, 0.5,  0.0, 0.16, 0.0, 0.5]
        # fmt: on
