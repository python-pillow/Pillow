from PIL import Image, features

from .helper import assert_image_equal, hopper


def test_split():
    def split(mode):
        layers = hopper(mode).split()
        return [(i.mode, i.size[0], i.size[1]) for i in layers]

    assert split("1") == [("1", 128, 128)]
    assert split("L") == [("L", 128, 128)]
    assert split("I") == [("I", 128, 128)]
    assert split("F") == [("F", 128, 128)]
    assert split("P") == [("P", 128, 128)]
    assert split("RGB") == [("L", 128, 128), ("L", 128, 128), ("L", 128, 128)]
    assert split("RGBA") == [
        ("L", 128, 128),
        ("L", 128, 128),
        ("L", 128, 128),
        ("L", 128, 128),
    ]
    assert split("CMYK") == [
        ("L", 128, 128),
        ("L", 128, 128),
        ("L", 128, 128),
        ("L", 128, 128),
    ]
    assert split("YCbCr") == [("L", 128, 128), ("L", 128, 128), ("L", 128, 128)]


def test_split_merge():
    def split_merge(mode):
        return Image.merge(mode, hopper(mode).split())

    assert_image_equal(hopper("1"), split_merge("1"))
    assert_image_equal(hopper("L"), split_merge("L"))
    assert_image_equal(hopper("I"), split_merge("I"))
    assert_image_equal(hopper("F"), split_merge("F"))
    assert_image_equal(hopper("P"), split_merge("P"))
    assert_image_equal(hopper("RGB"), split_merge("RGB"))
    assert_image_equal(hopper("RGBA"), split_merge("RGBA"))
    assert_image_equal(hopper("CMYK"), split_merge("CMYK"))
    assert_image_equal(hopper("YCbCr"), split_merge("YCbCr"))


def test_split_open(tmp_path):
    if features.check("zlib"):
        test_file = str(tmp_path / "temp.png")
    else:
        test_file = str(tmp_path / "temp.pcx")

    def split_open(mode):
        hopper(mode).save(test_file)
        with Image.open(test_file) as im:
            return len(im.split())

    assert split_open("1") == 1
    assert split_open("L") == 1
    assert split_open("P") == 1
    assert split_open("RGB") == 3
    if features.check("zlib"):
        assert split_open("RGBA") == 4
