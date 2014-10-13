from helper import unittest, PillowTestCase

from PIL import Image, ImageFilter


sample = Image.new("L", (7, 5))
sample.putdata(sum([
    [210, 50,  20,  10,  220, 230, 80 ],
    [190, 210, 20,  180, 170, 40,  110],
    [120, 210, 250, 60,  220, 0,   220],
    [220, 40,  230, 80,  130, 250, 40 ],
    [250, 0,   80,  30,  60,  20,  110],
 ], []))


def box_blur(self, radius):
    return self._new(self.im.box_blur(radius))


class TestBoxBlur(PillowTestCase):

    def assertImage(self, im, data, delta=0):
        it = iter(im.getdata())
        for data_row in data:
            im_row = [next(it) for _ in range(im.size[0])]
            if any(
                abs(data_v - im_v) > delta
                for data_v, im_v in zip(data_row, im_row)
            ):
                self.assertEqual(im_row, data_row)
        self.assertRaises(StopIteration, next, it)

    def test_radius_0(self):
        self.assertImage(
            box_blur(sample, 0),
            [
                [210, 50,  20,  10,  220, 230, 80 ],
                [190, 210, 20,  180, 170, 40,  110],
                [120, 210, 250, 60,  220, 0,   220],
                [220, 40,  230, 80,  130, 250, 40 ],
                [250, 0,   80,  30,  60,  20,  110],
            ]
        )

    def test_radius_0_02(self):
        self.assertImage(
            box_blur(sample, 0.02),
            [
                [206, 55,  20,  17,  215, 223, 83 ],
                [189, 203, 31,  171, 169, 46,  110],
                [125, 206, 241, 69,  210, 13,  210],
                [215, 49,  221, 82,  131, 235, 48 ],
                [244, 7,   80,  32,  60,  27,  107],
            ],
            delta=2,
        )

    def test_radius_0_05(self):
        self.assertImage(
            box_blur(sample, 0.05),
            [
                [202, 62,  22,  27,  209, 215, 88 ],
                [188, 194, 44,  161, 168, 56,  111],
                [131, 201, 229, 81,  198, 31,  198],
                [209, 62,  209, 86,  133, 216, 59 ],
                [237, 17,  80,  36,  60,  35,  103],
            ],
            delta=2,
        )

    def test_radius_0_1(self):
        self.assertImage(
            box_blur(sample, 0.1),
            [
                [196, 72,  24,  40,  200, 203, 93 ],
                [187, 183, 62,  148, 166, 68,  111],
                [139, 193, 213, 96,  182, 54,  182],
                [201, 78,  193, 91,  133, 191, 73 ],
                [227, 31,  80,  42,  61,  47,  99 ],
            ],
            delta=1,
        )

    def test_radius_0_5(self):
        self.assertImage(
            box_blur(sample, 0.5),
            [
                [176, 101, 46,  83,  163, 165, 111],
                [176, 149, 108, 122, 144, 120, 117],
                [164, 171, 159, 141, 134, 119, 129],
                [170, 136, 133, 114, 116, 124, 109],
                [184, 95,  72,  70,  69,  81,  89 ],
            ],
            delta=1,
        )

    def test_radius_1(self):
        self.assertImage(
            box_blur(sample, 1),
            [
                [170, 109, 63,  97,  146, 153, 116],
                [168, 142, 112, 128, 126, 143, 121],
                [169, 166, 142, 149, 126, 131, 114],
                [159, 156, 109, 127, 94,  117, 112],
                [164, 128, 63,  87,  76,  89,  90 ],
            ],
            delta=1,
        )

    def test_radius_1_5(self):
        self.assertImage(
            box_blur(sample, 1.5),
            [
                [155, 120, 105, 112, 124, 137, 130],
                [160, 136, 124, 125, 127, 134, 130],
                [166, 147, 130, 125, 120, 121, 119],
                [168, 145, 119, 109, 103, 105, 110],
                [168, 134, 96,  85,  85,  89,  97 ],
            ],
            delta=1,
        )
