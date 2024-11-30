from __future__ import annotations

import math
from typing import Callable

import pytest

from PIL import Image, ImageTransform

from .helper import assert_image_equal, assert_image_similar, hopper


class TestImageTransform:
    def test_sanity(self) -> None:
        im = hopper()

        for transform in (
            ImageTransform.AffineTransform((1, 0, 0, 0, 1, 0)),
            ImageTransform.PerspectiveTransform((1, 0, 0, 0, 1, 0, 0, 0)),
            ImageTransform.ExtentTransform((0, 0) + im.size),
            ImageTransform.QuadTransform(
                (0, 0, 0, im.height, im.width, im.height, im.width, 0)
            ),
            ImageTransform.MeshTransform(
                [
                    (
                        (0, 0) + im.size,
                        (0, 0, 0, im.height, im.width, im.height, im.width, 0),
                    )
                ]
            ),
        ):
            assert_image_equal(im, im.transform(im.size, transform))

    def test_info(self) -> None:
        comment = b"File written by Adobe Photoshop\xa8 4.0"

        with Image.open("Tests/images/hopper.gif") as im:
            assert im.info["comment"] == comment

            transform = ImageTransform.ExtentTransform((0, 0, 0, 0))
            new_im = im.transform((100, 100), transform)
        assert new_im.info["comment"] == comment

    def test_palette(self) -> None:
        with Image.open("Tests/images/hopper.gif") as im:
            transformed = im.transform(
                im.size, Image.Transform.AFFINE, [1, 0, 0, 0, 1, 0]
            )
            assert im.palette.palette == transformed.palette.palette

    def test_extent(self) -> None:
        im = hopper("RGB")
        (w, h) = im.size
        transformed = im.transform(
            im.size,
            Image.Transform.EXTENT,
            (0, 0, w // 2, h // 2),  # ul -> lr
            Image.Resampling.BILINEAR,
        )

        scaled = im.resize((w * 2, h * 2), Image.Resampling.BILINEAR).crop((0, 0, w, h))

        # undone -- precision?
        assert_image_similar(transformed, scaled, 23)

    def test_quad(self) -> None:
        # one simple quad transform, equivalent to scale & crop upper left quad
        im = hopper("RGB")
        (w, h) = im.size
        transformed = im.transform(
            im.size,
            Image.Transform.QUAD,
            (0, 0, 0, h // 2, w // 2, h // 2, w // 2, 0),  # ul -> ccw around quad
            Image.Resampling.BILINEAR,
        )

        scaled = im.transform(
            (w, h),
            Image.Transform.AFFINE,
            (0.5, 0, 0, 0, 0.5, 0),
            Image.Resampling.BILINEAR,
        )

        assert_image_equal(transformed, scaled)

    @pytest.mark.parametrize(
        "mode, expected_pixel",
        (
            ("RGB", (255, 0, 0)),
            ("RGBA", (255, 0, 0, 255)),
            ("LA", (76, 0)),
        ),
    )
    def test_fill(self, mode: str, expected_pixel: tuple[int, ...]) -> None:
        im = hopper(mode)
        (w, h) = im.size
        transformed = im.transform(
            im.size,
            Image.Transform.EXTENT,
            (0, 0, w * 2, h * 2),
            Image.Resampling.BILINEAR,
            fillcolor="red",
        )
        assert transformed.getpixel((w - 1, h - 1)) == expected_pixel

    def test_mesh(self) -> None:
        # this should be a checkerboard of halfsized hoppers in ul, lr
        im = hopper("RGBA")
        (w, h) = im.size
        transformed = im.transform(
            im.size,
            Image.Transform.MESH,
            (
                (
                    (0, 0, w // 2, h // 2),  # box
                    (0, 0, 0, h, w, h, w, 0),  # ul -> ccw around quad
                ),
                (
                    (w // 2, h // 2, w, h),  # box
                    (0, 0, 0, h, w, h, w, 0),  # ul -> ccw around quad
                ),
            ),
            Image.Resampling.BILINEAR,
        )

        scaled = im.transform(
            (w // 2, h // 2),
            Image.Transform.AFFINE,
            (2, 0, 0, 0, 2, 0),
            Image.Resampling.BILINEAR,
        )

        checker = Image.new("RGBA", im.size)
        checker.paste(scaled, (0, 0))
        checker.paste(scaled, (w // 2, h // 2))

        assert_image_equal(transformed, checker)

        # now, check to see that the extra area is (0, 0, 0, 0)
        blank = Image.new("RGBA", (w // 2, h // 2), (0, 0, 0, 0))

        assert_image_equal(blank, transformed.crop((w // 2, 0, w, h // 2)))
        assert_image_equal(blank, transformed.crop((0, h // 2, w // 2, h)))

    def _test_alpha_premult(
        self, op: Callable[[Image.Image, tuple[int, int]], Image.Image]
    ) -> None:
        # create image with half white, half black,
        # with the black half transparent.
        # do op,
        # there should be no darkness in the white section.
        im = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        im2 = Image.new("RGBA", (5, 10), (255, 255, 255, 255))
        im.paste(im2, (0, 0))

        im = op(im, (40, 10))
        im_background = Image.new("RGB", (40, 10), (255, 255, 255))
        im_background.paste(im, (0, 0), im)

        hist = im_background.histogram()
        assert 40 * 10 == hist[-1]

    def test_alpha_premult_resize(self) -> None:
        def op(im: Image.Image, sz: tuple[int, int]) -> Image.Image:
            return im.resize(sz, Image.Resampling.BILINEAR)

        self._test_alpha_premult(op)

    def test_alpha_premult_transform(self) -> None:
        def op(im: Image.Image, sz: tuple[int, int]) -> Image.Image:
            (w, h) = im.size
            return im.transform(
                sz, Image.Transform.EXTENT, (0, 0, w, h), Image.Resampling.BILINEAR
            )

        self._test_alpha_premult(op)

    def _test_nearest(
        self, op: Callable[[Image.Image, tuple[int, int]], Image.Image], mode: str
    ) -> None:
        # create white image with half transparent,
        # do op,
        # the image should remain white with half transparent
        transparent, opaque = {
            "RGBA": ((255, 255, 255, 0), (255, 255, 255, 255)),
            "LA": ((255, 0), (255, 255)),
        }[mode]
        im = Image.new(mode, (10, 10), transparent)
        im2 = Image.new(mode, (5, 10), opaque)
        im.paste(im2, (0, 0))

        im = op(im, (40, 10))

        colors = im.getcolors()
        assert colors is not None
        assert sorted(colors) == sorted(
            (
                (20 * 10, opaque),
                (20 * 10, transparent),
            )
        )

    @pytest.mark.parametrize("mode", ("RGBA", "LA"))
    def test_nearest_resize(self, mode: str) -> None:
        def op(im: Image.Image, sz: tuple[int, int]) -> Image.Image:
            return im.resize(sz, Image.Resampling.NEAREST)

        self._test_nearest(op, mode)

    @pytest.mark.parametrize("mode", ("RGBA", "LA"))
    def test_nearest_transform(self, mode: str) -> None:
        def op(im: Image.Image, sz: tuple[int, int]) -> Image.Image:
            (w, h) = im.size
            return im.transform(
                sz, Image.Transform.EXTENT, (0, 0, w, h), Image.Resampling.NEAREST
            )

        self._test_nearest(op, mode)

    def test_blank_fill(self) -> None:
        # attempting to hit
        # https://github.com/python-pillow/Pillow/issues/254 reported
        #
        # issue is that transforms with transparent overflow area
        # contained junk from previous images, especially on systems with
        # constrained memory. So, attempt to fill up memory with a
        # pattern, free it, and then run the mesh test again. Using a 1Mp
        # image with 4 bands, for 4 megs of data allocated, x 64. OMM (64
        # bit 12.04 VM with 512 megs available, this fails with Pillow <
        # a0eaf06cc5f62a6fb6de556989ac1014ff3348ea
        #
        # Running by default, but I'd totally understand not doing it in
        # the future

        pattern: list[Image.Image] | None = [
            Image.new("RGBA", (1024, 1024), (a, a, a, a)) for a in range(1, 65)
        ]

        # Yeah. Watch some JIT optimize this out.
        pattern = None  # noqa: F841

        self.test_mesh()

    def test_missing_method_data(self) -> None:
        with hopper() as im:
            with pytest.raises(ValueError):
                im.transform((100, 100), None)

    @pytest.mark.parametrize("resample", (Image.Resampling.BOX, "unknown"))
    def test_unknown_resampling_filter(self, resample: Image.Resampling | str) -> None:
        with hopper() as im:
            (w, h) = im.size
            with pytest.raises(ValueError):
                im.transform((100, 100), Image.Transform.EXTENT, (0, 0, w, h), resample)


class TestImageTransformAffine:
    transform = Image.Transform.AFFINE

    def _test_image(self) -> Image.Image:
        im = hopper("RGB")
        return im.crop((10, 20, im.width - 10, im.height - 20))

    @pytest.mark.parametrize(
        "deg, transpose",
        (
            (0, None),
            (90, Image.Transpose.ROTATE_90),
            (180, Image.Transpose.ROTATE_180),
            (270, Image.Transpose.ROTATE_270),
        ),
    )
    def test_rotate(self, deg: int, transpose: Image.Transpose | None) -> None:
        im = self._test_image()

        angle = -math.radians(deg)
        matrix = [
            round(math.cos(angle), 15),
            round(math.sin(angle), 15),
            0.0,
            round(-math.sin(angle), 15),
            round(math.cos(angle), 15),
            0.0,
            0,
            0,
        ]
        matrix[2] = (1 - matrix[0] - matrix[1]) * im.width / 2
        matrix[5] = (1 - matrix[3] - matrix[4]) * im.height / 2

        if transpose is not None:
            transposed = im.transpose(transpose)
        else:
            transposed = im

        for resample in [
            Image.Resampling.NEAREST,
            Image.Resampling.BILINEAR,
            Image.Resampling.BICUBIC,
        ]:
            transformed = im.transform(
                transposed.size, self.transform, matrix, resample
            )
            assert_image_equal(transposed, transformed)

    @pytest.mark.parametrize(
        "scale, epsilon_scale",
        (
            (1.1, 6.9),
            (1.5, 5.5),
            (2.0, 5.5),
            (2.3, 3.7),
            (2.5, 3.7),
        ),
    )
    @pytest.mark.parametrize(
        "resample,epsilon",
        (
            (Image.Resampling.NEAREST, 0),
            (Image.Resampling.BILINEAR, 2),
            (Image.Resampling.BICUBIC, 1),
        ),
    )
    def test_resize(
        self,
        scale: float,
        epsilon_scale: float,
        resample: Image.Resampling,
        epsilon: int,
    ) -> None:
        im = self._test_image()

        size_up = int(round(im.width * scale)), int(round(im.height * scale))
        matrix_up = [1 / scale, 0, 0, 0, 1 / scale, 0, 0, 0]
        matrix_down = [scale, 0, 0, 0, scale, 0, 0, 0]

        transformed = im.transform(size_up, self.transform, matrix_up, resample)
        transformed = transformed.transform(
            im.size, self.transform, matrix_down, resample
        )
        assert_image_similar(transformed, im, epsilon * epsilon_scale)

    @pytest.mark.parametrize(
        "x, y, epsilon_scale",
        (
            (0.1, 0, 3.7),
            (0.6, 0, 9.1),
            (50, 50, 0),
        ),
    )
    @pytest.mark.parametrize(
        "resample, epsilon",
        (
            (Image.Resampling.NEAREST, 0),
            (Image.Resampling.BILINEAR, 1.5),
            (Image.Resampling.BICUBIC, 1),
        ),
    )
    def test_translate(
        self,
        x: float,
        y: float,
        epsilon_scale: float,
        resample: Image.Resampling,
        epsilon: float,
    ) -> None:
        im = self._test_image()

        size_up = int(round(im.width + x)), int(round(im.height + y))
        matrix_up = [1, 0, -x, 0, 1, -y, 0, 0]
        matrix_down = [1, 0, x, 0, 1, y, 0, 0]

        transformed = im.transform(size_up, self.transform, matrix_up, resample)
        transformed = transformed.transform(
            im.size, self.transform, matrix_down, resample
        )
        assert_image_similar(transformed, im, epsilon * epsilon_scale)


class TestImageTransformPerspective(TestImageTransformAffine):
    # Repeat all tests for AFFINE transformations with PERSPECTIVE
    transform = Image.Transform.PERSPECTIVE
