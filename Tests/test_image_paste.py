from __future__ import annotations

import pytest

from PIL import Image

from .helper import CachedProperty, assert_image_equal


class TestImagingPaste:
    size = 128

    def assert_9points_image(
        self, im: Image.Image, expected: list[tuple[int, int, int, int]]
    ) -> None:
        px = im.load()
        assert px is not None
        actual = [
            px[0, 0],
            px[self.size // 2, 0],
            px[self.size - 1, 0],
            px[0, self.size // 2],
            px[self.size // 2, self.size // 2],
            px[self.size - 1, self.size // 2],
            px[0, self.size - 1],
            px[self.size // 2, self.size - 1],
            px[self.size - 1, self.size - 1],
        ]
        assert actual == [
            point[0] if im.mode == "L" else point[: len(im.mode)] for point in expected
        ]

    def assert_9points_paste(
        self,
        im: Image.Image,
        im2: Image.Image | str | tuple[int, ...],
        mask: Image.Image,
        expected: list[tuple[int, int, int, int]],
    ) -> None:
        im3 = im.copy()
        im3.paste(im2, (0, 0), mask)
        self.assert_9points_image(im3, expected)

        # Abbreviated syntax
        im.paste(im2, mask)
        self.assert_9points_image(im, expected)

    @CachedProperty
    def mask_1(self) -> Image.Image:
        mask = Image.new("1", (self.size, self.size))
        px = mask.load()
        assert px is not None
        for y in range(mask.height):
            for x in range(mask.width):
                px[y, x] = (x + y) % 2
        return mask

    @CachedProperty
    def mask_L(self) -> Image.Image:
        return self.gradient_L.transpose(Image.Transpose.ROTATE_270)

    @CachedProperty
    def gradient_L(self) -> Image.Image:
        gradient = Image.new("L", (self.size, self.size))
        px = gradient.load()
        assert px is not None
        for y in range(gradient.height):
            for x in range(gradient.width):
                px[y, x] = (x + y) % 255
        return gradient

    @CachedProperty
    def gradient_RGB(self) -> Image.Image:
        return Image.merge(
            "RGB",
            [
                self.gradient_L,
                self.gradient_L.transpose(Image.Transpose.ROTATE_90),
                self.gradient_L.transpose(Image.Transpose.ROTATE_180),
            ],
        )

    @CachedProperty
    def gradient_LA(self) -> Image.Image:
        return Image.merge(
            "LA",
            [
                self.gradient_L,
                self.gradient_L.transpose(Image.Transpose.ROTATE_90),
            ],
        )

    @CachedProperty
    def gradient_RGBA(self) -> Image.Image:
        return Image.merge(
            "RGBA",
            [
                self.gradient_L,
                self.gradient_L.transpose(Image.Transpose.ROTATE_90),
                self.gradient_L.transpose(Image.Transpose.ROTATE_180),
                self.gradient_L.transpose(Image.Transpose.ROTATE_270),
            ],
        )

    @CachedProperty
    def gradient_RGBa(self) -> Image.Image:
        return Image.merge(
            "RGBa",
            [
                self.gradient_L,
                self.gradient_L.transpose(Image.Transpose.ROTATE_90),
                self.gradient_L.transpose(Image.Transpose.ROTATE_180),
                self.gradient_L.transpose(Image.Transpose.ROTATE_270),
            ],
        )

    @pytest.mark.parametrize("mode", ["RGBA", "RGB", "L"])
    def test_image_solid(self, mode: str) -> None:
        im = Image.new(mode, (200, 200), "red")
        im2 = getattr(self, "gradient_" + mode)

        im.paste(im2, (12, 23))

        im = im.crop((12, 23, im2.width + 12, im2.height + 23))
        assert_image_equal(im, im2)

    @pytest.mark.parametrize("y", [10, -10])
    @pytest.mark.parametrize("mode", ["L", "RGB"])
    @pytest.mark.parametrize("mask_mode", ["", "1", "L", "LA", "RGBa"])
    def test_image_self(self, y: int, mode: str, mask_mode: str) -> None:
        im = getattr(self, "gradient_" + mode)
        mask = Image.new(mask_mode, im.size, 0xFFFFFFFF) if mask_mode else None

        im_self = im.copy()
        im_self.paste(im_self, (0, y), mask)

        im_copy = im.copy()
        im_copy.paste(im_copy.copy(), (0, y), mask)

        assert_image_equal(im_self, im_copy)

    @pytest.mark.parametrize("mode", ["RGBA", "RGB", "L"])
    def test_image_mask_1(self, mode: str) -> None:
        im = Image.new(mode, (200, 200), "white")
        im2 = getattr(self, "gradient_" + mode)

        self.assert_9points_paste(
            im,
            im2,
            self.mask_1,
            [
                (255, 255, 255, 255),
                (255, 255, 255, 255),
                (127, 254, 127, 0),
                (255, 255, 255, 255),
                (255, 255, 255, 255),
                (191, 190, 63, 64),
                (127, 0, 127, 254),
                (191, 64, 63, 190),
                (255, 255, 255, 255),
            ],
        )

    @pytest.mark.parametrize("mode", ["RGBA", "RGB", "L"])
    def test_image_mask_L(self, mode: str) -> None:
        im = Image.new(mode, (200, 200), "white")
        im2 = getattr(self, "gradient_" + mode)

        self.assert_9points_paste(
            im,
            im2,
            self.mask_L,
            [
                (128, 191, 255, 191),
                (208, 239, 239, 208),
                (255, 255, 255, 255),
                (112, 111, 206, 207),
                (192, 191, 191, 191),
                (239, 239, 207, 207),
                (128, 1, 128, 254),
                (207, 113, 112, 207),
                (255, 191, 128, 191),
            ],
        )

    @pytest.mark.parametrize("mode", ["RGBA", "RGB", "L"])
    def test_image_mask_LA(self, mode: str) -> None:
        im = Image.new(mode, (200, 200), "white")
        im2 = getattr(self, "gradient_" + mode)

        self.assert_9points_paste(
            im,
            im2,
            self.gradient_LA,
            [
                (128, 191, 255, 191),
                (112, 207, 206, 111),
                (128, 254, 128, 1),
                (208, 208, 239, 239),
                (192, 191, 191, 191),
                (207, 207, 112, 113),
                (255, 255, 255, 255),
                (239, 207, 207, 239),
                (255, 191, 128, 191),
            ],
        )

    @pytest.mark.parametrize("mode", ["RGBA", "RGB", "L"])
    def test_image_mask_RGBA(self, mode: str) -> None:
        im = Image.new(mode, (200, 200), "white")
        im2 = getattr(self, "gradient_" + mode)

        self.assert_9points_paste(
            im,
            im2,
            self.gradient_RGBA,
            [
                (128, 191, 255, 191),
                (208, 239, 239, 208),
                (255, 255, 255, 255),
                (112, 111, 206, 207),
                (192, 191, 191, 191),
                (239, 239, 207, 207),
                (128, 1, 128, 254),
                (207, 113, 112, 207),
                (255, 191, 128, 191),
            ],
        )

    @pytest.mark.parametrize("mode", ["RGBA", "RGB", "L"])
    def test_image_mask_RGBa(self, mode: str) -> None:
        im = Image.new(mode, (200, 200), "white")
        im2 = getattr(self, "gradient_" + mode)

        self.assert_9points_paste(
            im,
            im2,
            self.gradient_RGBa,
            [
                (128, 255, 126, 255),
                (0, 127, 126, 255),
                (126, 253, 126, 255),
                (128, 127, 254, 255),
                (0, 255, 254, 255),
                (126, 125, 254, 255),
                (128, 1, 128, 255),
                (0, 129, 128, 255),
                (126, 255, 128, 255),
            ],
        )

    @pytest.mark.parametrize("mode", ["RGBA", "RGB", "L"])
    def test_color_solid(self, mode: str) -> None:
        im = Image.new(mode, (200, 200), "black")

        rect = (12, 23, 128 + 12, 128 + 23)
        im.paste("white", rect)

        hist = im.crop(rect).histogram()
        while hist:
            head, hist = hist[:256], hist[256:]
            assert head[255] == 128 * 128
            assert sum(head[:255]) == 0

    @pytest.mark.parametrize("mode", ["RGBA", "RGB", "L"])
    def test_color_mask_1(self, mode: str) -> None:
        im = Image.new(mode, (200, 200), (50, 60, 70, 80)[: len(mode)])
        color = (10, 20, 30, 40)[: len(mode)]

        self.assert_9points_paste(
            im,
            color,
            self.mask_1,
            [
                (50, 60, 70, 80),
                (50, 60, 70, 80),
                (10, 20, 30, 40),
                (50, 60, 70, 80),
                (50, 60, 70, 80),
                (10, 20, 30, 40),
                (10, 20, 30, 40),
                (10, 20, 30, 40),
                (50, 60, 70, 80),
            ],
        )

    @pytest.mark.parametrize("mode", ["RGBA", "RGB", "L"])
    def test_color_mask_L(self, mode: str) -> None:
        im = getattr(self, "gradient_" + mode).copy()
        color = "white"

        self.assert_9points_paste(
            im,
            color,
            self.mask_L,
            [
                (127, 191, 254, 191),
                (111, 207, 206, 110),
                (127, 254, 127, 0),
                (207, 207, 239, 239),
                (191, 191, 190, 191),
                (207, 206, 111, 112),
                (254, 254, 254, 255),
                (239, 206, 206, 238),
                (254, 191, 127, 191),
            ],
        )

    @pytest.mark.parametrize("mode", ["RGBA", "RGB", "L"])
    def test_color_mask_RGBA(self, mode: str) -> None:
        im = getattr(self, "gradient_" + mode).copy()
        color = "white"

        self.assert_9points_paste(
            im,
            color,
            self.gradient_RGBA,
            [
                (127, 191, 254, 191),
                (111, 207, 206, 110),
                (127, 254, 127, 0),
                (207, 207, 239, 239),
                (191, 191, 190, 191),
                (207, 206, 111, 112),
                (254, 254, 254, 255),
                (239, 206, 206, 238),
                (254, 191, 127, 191),
            ],
        )

    @pytest.mark.parametrize("mode", ["RGBA", "RGB", "L"])
    def test_color_mask_RGBa(self, mode: str) -> None:
        im = getattr(self, "gradient_" + mode).copy()
        color = "white"

        self.assert_9points_paste(
            im,
            color,
            self.gradient_RGBa,
            [
                (255, 63, 126, 63),
                (47, 143, 142, 46),
                (126, 253, 126, 255),
                (15, 15, 47, 47),
                (63, 63, 62, 63),
                (142, 141, 46, 47),
                (255, 255, 255, 0),
                (48, 15, 15, 47),
                (126, 63, 255, 63),
            ],
        )

    def test_different_sizes(self) -> None:
        im = Image.new("RGB", (100, 100))
        im2 = Image.new("RGB", (50, 50))

        im.copy().paste(im2)
        im.copy().paste(im2, (0, 0))

    def test_incorrect_abbreviated_form(self) -> None:
        im = Image.new("L", (1, 1))
        with pytest.raises(ValueError):
            im.paste(im, im, im)
