import colorsys
import itertools

from PIL import Image

from .helper import PillowTestCase, hopper


class TestFormatHSV(PillowTestCase):
    def int_to_float(self, i):
        return float(i) / 255.0

    def str_to_float(self, i):
        return float(ord(i)) / 255.0

    def tuple_to_ints(self, tp):
        x, y, z = tp
        return int(x * 255.0), int(y * 255.0), int(z * 255.0)

    def test_sanity(self):
        Image.new("HSV", (100, 100))

    def wedge(self):
        w = Image._wedge()
        w90 = w.rotate(90)

        (px, h) = w.size

        r = Image.new("L", (px * 3, h))
        g = r.copy()
        b = r.copy()

        r.paste(w, (0, 0))
        r.paste(w90, (px, 0))

        g.paste(w90, (0, 0))
        g.paste(w, (2 * px, 0))

        b.paste(w, (px, 0))
        b.paste(w90, (2 * px, 0))

        img = Image.merge("RGB", (r, g, b))

        return img

    def to_xxx_colorsys(self, im, func, mode):
        # convert the hard way using the library colorsys routines.

        (r, g, b) = im.split()

        conv_func = self.int_to_float

        converted = [
            self.tuple_to_ints(func(conv_func(_r), conv_func(_g), conv_func(_b)))
            for (_r, _g, _b) in itertools.zip_longest(
                r.tobytes(), g.tobytes(), b.tobytes()
            )
        ]

        new_bytes = b"".join(
            bytes(chr(h) + chr(s) + chr(v), "latin-1") for (h, s, v) in converted
        )

        hsv = Image.frombytes(mode, r.size, new_bytes)

        return hsv

    def to_hsv_colorsys(self, im):
        return self.to_xxx_colorsys(im, colorsys.rgb_to_hsv, "HSV")

    def to_rgb_colorsys(self, im):
        return self.to_xxx_colorsys(im, colorsys.hsv_to_rgb, "RGB")

    def test_wedge(self):
        src = self.wedge().resize((3 * 32, 32), Image.BILINEAR)
        im = src.convert("HSV")
        comparable = self.to_hsv_colorsys(src)

        self.assert_image_similar(
            im.getchannel(0), comparable.getchannel(0), 1, "Hue conversion is wrong"
        )
        self.assert_image_similar(
            im.getchannel(1),
            comparable.getchannel(1),
            1,
            "Saturation conversion is wrong",
        )
        self.assert_image_similar(
            im.getchannel(2), comparable.getchannel(2), 1, "Value conversion is wrong"
        )

        comparable = src
        im = im.convert("RGB")

        self.assert_image_similar(
            im.getchannel(0), comparable.getchannel(0), 3, "R conversion is wrong"
        )
        self.assert_image_similar(
            im.getchannel(1), comparable.getchannel(1), 3, "G conversion is wrong"
        )
        self.assert_image_similar(
            im.getchannel(2), comparable.getchannel(2), 3, "B conversion is wrong"
        )

    def test_convert(self):
        im = hopper("RGB").convert("HSV")
        comparable = self.to_hsv_colorsys(hopper("RGB"))

        self.assert_image_similar(
            im.getchannel(0), comparable.getchannel(0), 1, "Hue conversion is wrong"
        )
        self.assert_image_similar(
            im.getchannel(1),
            comparable.getchannel(1),
            1,
            "Saturation conversion is wrong",
        )
        self.assert_image_similar(
            im.getchannel(2), comparable.getchannel(2), 1, "Value conversion is wrong"
        )

    def test_hsv_to_rgb(self):
        comparable = self.to_hsv_colorsys(hopper("RGB"))
        converted = comparable.convert("RGB")
        comparable = self.to_rgb_colorsys(comparable)

        self.assert_image_similar(
            converted.getchannel(0),
            comparable.getchannel(0),
            3,
            "R conversion is wrong",
        )
        self.assert_image_similar(
            converted.getchannel(1),
            comparable.getchannel(1),
            3,
            "G conversion is wrong",
        )
        self.assert_image_similar(
            converted.getchannel(2),
            comparable.getchannel(2),
            3,
            "B conversion is wrong",
        )
