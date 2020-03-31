from PIL import Image

from .helper import assert_image_equal, cached_property


class TestImagingPaste:
    masks = {}
    size = 128

    def assert_9points_image(self, im, expected):
        expected = [
            point[0] if im.mode == "L" else point[: len(im.mode)] for point in expected
        ]
        px = im.load()
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
        assert actual == expected

    def assert_9points_paste(self, im, im2, mask, expected):
        im3 = im.copy()
        im3.paste(im2, (0, 0), mask)
        self.assert_9points_image(im3, expected)

        # Abbreviated syntax
        im.paste(im2, mask)
        self.assert_9points_image(im, expected)

    @cached_property
    def mask_1(self):
        mask = Image.new("1", (self.size, self.size))
        px = mask.load()
        for y in range(mask.height):
            for x in range(mask.width):
                px[y, x] = (x + y) % 2
        return mask

    @cached_property
    def mask_L(self):
        return self.gradient_L.transpose(Image.ROTATE_270)

    @cached_property
    def gradient_L(self):
        gradient = Image.new("L", (self.size, self.size))
        px = gradient.load()
        for y in range(gradient.height):
            for x in range(gradient.width):
                px[y, x] = (x + y) % 255
        return gradient

    @cached_property
    def gradient_RGB(self):
        return Image.merge(
            "RGB",
            [
                self.gradient_L,
                self.gradient_L.transpose(Image.ROTATE_90),
                self.gradient_L.transpose(Image.ROTATE_180),
            ],
        )

    @cached_property
    def gradient_RGBA(self):
        return Image.merge(
            "RGBA",
            [
                self.gradient_L,
                self.gradient_L.transpose(Image.ROTATE_90),
                self.gradient_L.transpose(Image.ROTATE_180),
                self.gradient_L.transpose(Image.ROTATE_270),
            ],
        )

    @cached_property
    def gradient_RGBa(self):
        return Image.merge(
            "RGBa",
            [
                self.gradient_L,
                self.gradient_L.transpose(Image.ROTATE_90),
                self.gradient_L.transpose(Image.ROTATE_180),
                self.gradient_L.transpose(Image.ROTATE_270),
            ],
        )

    def test_image_solid(self):
        for mode in ("RGBA", "RGB", "L"):
            im = Image.new(mode, (200, 200), "red")
            im2 = getattr(self, "gradient_" + mode)

            im.paste(im2, (12, 23))

            im = im.crop((12, 23, im2.width + 12, im2.height + 23))
            assert_image_equal(im, im2)

    def test_image_mask_1(self):
        for mode in ("RGBA", "RGB", "L"):
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

    def test_image_mask_L(self):
        for mode in ("RGBA", "RGB", "L"):
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

    def test_image_mask_RGBA(self):
        for mode in ("RGBA", "RGB", "L"):
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

    def test_image_mask_RGBa(self):
        for mode in ("RGBA", "RGB", "L"):
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

    def test_color_solid(self):
        for mode in ("RGBA", "RGB", "L"):
            im = Image.new(mode, (200, 200), "black")

            rect = (12, 23, 128 + 12, 128 + 23)
            im.paste("white", rect)

            hist = im.crop(rect).histogram()
            while hist:
                head, hist = hist[:256], hist[256:]
                assert head[255] == 128 * 128
                assert sum(head[:255]) == 0

    def test_color_mask_1(self):
        for mode in ("RGBA", "RGB", "L"):
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

    def test_color_mask_L(self):
        for mode in ("RGBA", "RGB", "L"):
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

    def test_color_mask_RGBA(self):
        for mode in ("RGBA", "RGB", "L"):
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

    def test_color_mask_RGBa(self):
        for mode in ("RGBA", "RGB", "L"):
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

    def test_different_sizes(self):
        im = Image.new("RGB", (100, 100))
        im2 = Image.new("RGB", (50, 50))

        im.copy().paste(im2)
        im.copy().paste(im2, (0, 0))
