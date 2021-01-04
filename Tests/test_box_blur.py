import pytest

from PIL import Image, ImageFilter

sample = Image.new("L", (7, 5))
# fmt: off
sample.putdata(sum([
    [210, 50,  20,  10,  220, 230, 80],
    [190, 210, 20,  180, 170, 40,  110],
    [120, 210, 250, 60,  220, 0,   220],
    [220, 40,  230, 80,  130, 250, 40],
    [250, 0,   80,  30,  60,  20,  110],
], []))
# fmt: on


def test_imageops_box_blur():
    i = sample.filter(ImageFilter.BoxBlur(1))
    assert i.mode == sample.mode
    assert i.size == sample.size
    assert isinstance(i, Image.Image)


def box_blur(image, radius=1, n=1):
    return image._new(image.im.box_blur(radius, n))


def assertImage(im, data, delta=0):
    it = iter(im.getdata())
    for data_row in data:
        im_row = [next(it) for _ in range(im.size[0])]
        if any(abs(data_v - im_v) > delta for data_v, im_v in zip(data_row, im_row)):
            assert im_row == data_row
    with pytest.raises(StopIteration):
        next(it)


def assertBlur(im, radius, data, passes=1, delta=0):
    # check grayscale image
    assertImage(box_blur(im, radius, passes), data, delta)
    rgba = Image.merge("RGBA", (im, im, im, im))
    for band in box_blur(rgba, radius, passes).split():
        assertImage(band, data, delta)


def test_color_modes():
    with pytest.raises(ValueError):
        box_blur(sample.convert("1"))
    with pytest.raises(ValueError):
        box_blur(sample.convert("P"))
    box_blur(sample.convert("L"))
    box_blur(sample.convert("LA"))
    box_blur(sample.convert("LA").convert("La"))
    with pytest.raises(ValueError):
        box_blur(sample.convert("I"))
    with pytest.raises(ValueError):
        box_blur(sample.convert("F"))
    box_blur(sample.convert("RGB"))
    box_blur(sample.convert("RGBA"))
    box_blur(sample.convert("RGBA").convert("RGBa"))
    box_blur(sample.convert("CMYK"))
    with pytest.raises(ValueError):
        box_blur(sample.convert("YCbCr"))


def test_radius_0():
    assertBlur(
        sample,
        0,
        [
            # fmt: off
            [210, 50,  20,  10,  220, 230, 80],
            [190, 210, 20,  180, 170, 40,  110],
            [120, 210, 250, 60,  220, 0,   220],
            [220, 40,  230, 80,  130, 250, 40],
            [250, 0,   80,  30,  60,  20,  110],
            # fmt: on
        ],
    )


def test_radius_0_02():
    assertBlur(
        sample,
        0.02,
        [
            # fmt: off
            [206, 55,  20,  17,  215, 223, 83],
            [189, 203, 31,  171, 169, 46,  110],
            [125, 206, 241, 69,  210, 13,  210],
            [215, 49,  221, 82,  131, 235, 48],
            [244, 7,   80,  32,  60,  27,  107],
            # fmt: on
        ],
        delta=2,
    )


def test_radius_0_05():
    assertBlur(
        sample,
        0.05,
        [
            # fmt: off
            [202, 62,  22,  27,  209, 215, 88],
            [188, 194, 44,  161, 168, 56,  111],
            [131, 201, 229, 81,  198, 31,  198],
            [209, 62,  209, 86,  133, 216, 59],
            [237, 17,  80,  36,  60,  35,  103],
            # fmt: on
        ],
        delta=2,
    )


def test_radius_0_1():
    assertBlur(
        sample,
        0.1,
        [
            # fmt: off
            [196, 72,  24,  40,  200, 203, 93],
            [187, 183, 62,  148, 166, 68,  111],
            [139, 193, 213, 96,  182, 54,  182],
            [201, 78,  193, 91,  133, 191, 73],
            [227, 31,  80,  42,  61,  47,  99],
            # fmt: on
        ],
        delta=1,
    )


def test_radius_0_5():
    assertBlur(
        sample,
        0.5,
        [
            # fmt: off
            [176, 101, 46,  83,  163, 165, 111],
            [176, 149, 108, 122, 144, 120, 117],
            [164, 171, 159, 141, 134, 119, 129],
            [170, 136, 133, 114, 116, 124, 109],
            [184, 95,  72,  70,  69,  81,  89],
            # fmt: on
        ],
        delta=1,
    )


def test_radius_1():
    assertBlur(
        sample,
        1,
        [
            # fmt: off
            [170, 109, 63,  97,  146, 153, 116],
            [168, 142, 112, 128, 126, 143, 121],
            [169, 166, 142, 149, 126, 131, 114],
            [159, 156, 109, 127, 94,  117, 112],
            [164, 128, 63,  87,  76,  89,  90],
            # fmt: on
        ],
        delta=1,
    )


def test_radius_1_5():
    assertBlur(
        sample,
        1.5,
        [
            # fmt: off
            [155, 120, 105, 112, 124, 137, 130],
            [160, 136, 124, 125, 127, 134, 130],
            [166, 147, 130, 125, 120, 121, 119],
            [168, 145, 119, 109, 103, 105, 110],
            [168, 134, 96,  85,  85,  89,  97],
            # fmt: on
        ],
        delta=1,
    )


def test_radius_bigger_then_half():
    assertBlur(
        sample,
        3,
        [
            # fmt: off
            [144, 145, 142, 128, 114, 115, 117],
            [148, 145, 137, 122, 109, 111, 112],
            [152, 145, 131, 117, 103, 107, 108],
            [156, 144, 126, 111, 97,  102, 103],
            [160, 144, 121, 106, 92,  98,  99],
            # fmt: on
        ],
        delta=1,
    )


def test_radius_bigger_then_width():
    assertBlur(
        sample,
        10,
        [
            [158, 153, 147, 141, 135, 129, 123],
            [159, 153, 147, 141, 136, 130, 124],
            [159, 154, 148, 142, 136, 130, 124],
            [160, 154, 148, 142, 137, 131, 125],
            [160, 155, 149, 143, 137, 131, 125],
        ],
        delta=0,
    )


def test_extreme_large_radius():
    assertBlur(
        sample,
        600,
        [
            [162, 162, 162, 162, 162, 162, 162],
            [162, 162, 162, 162, 162, 162, 162],
            [162, 162, 162, 162, 162, 162, 162],
            [162, 162, 162, 162, 162, 162, 162],
            [162, 162, 162, 162, 162, 162, 162],
        ],
        delta=1,
    )


def test_two_passes():
    assertBlur(
        sample,
        1,
        [
            # fmt: off
            [153, 123, 102, 109, 132, 135, 129],
            [159, 138, 123, 121, 133, 131, 126],
            [162, 147, 136, 124, 127, 121, 121],
            [159, 140, 125, 108, 111, 106, 108],
            [154, 126, 105, 87,  94,  93,  97],
            # fmt: on
        ],
        passes=2,
        delta=1,
    )


def test_three_passes():
    assertBlur(
        sample,
        1,
        [
            # fmt: off
            [146, 131, 116, 118, 126, 131, 130],
            [151, 138, 125, 123, 126, 128, 127],
            [154, 143, 129, 123, 120, 120, 119],
            [152, 139, 122, 113, 108, 108, 108],
            [148, 132, 112, 102, 97,  99,  100],
            # fmt: on
        ],
        passes=3,
        delta=1,
    )
