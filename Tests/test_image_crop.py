import pytest

from PIL import Image

from .helper import assert_image_equal, hopper


def test_crop():
    def crop(mode):
        im = hopper(mode)
        assert_image_equal(im.crop(), im)

        cropped = im.crop((50, 50, 100, 100))
        assert cropped.mode == mode
        assert cropped.size == (50, 50)

    for mode in "1", "P", "L", "RGB", "I", "F":
        crop(mode)


def test_wide_crop():
    def crop(*bbox):
        i = im.crop(bbox)
        h = i.histogram()
        while h and not h[-1]:
            del h[-1]
        return tuple(h)

    im = Image.new("L", (100, 100), 1)

    assert crop(0, 0, 100, 100) == (0, 10000)
    assert crop(25, 25, 75, 75) == (0, 2500)

    # sides
    assert crop(-25, 0, 25, 50) == (1250, 1250)
    assert crop(0, -25, 50, 25) == (1250, 1250)
    assert crop(75, 0, 125, 50) == (1250, 1250)
    assert crop(0, 75, 50, 125) == (1250, 1250)

    assert crop(-25, 25, 125, 75) == (2500, 5000)
    assert crop(25, -25, 75, 125) == (2500, 5000)

    # corners
    assert crop(-25, -25, 25, 25) == (1875, 625)
    assert crop(75, -25, 125, 25) == (1875, 625)
    assert crop(75, 75, 125, 125) == (1875, 625)
    assert crop(-25, 75, 25, 125) == (1875, 625)


def test_negative_crop():
    # Check negative crop size (@PIL171)

    im = Image.new("L", (512, 512))
    im = im.crop((400, 400, 200, 200))

    assert im.size == (0, 0)
    assert len(im.getdata()) == 0
    with pytest.raises(IndexError):
        im.getdata()[0]


def test_crop_float():
    # Check cropping floats are rounded to nearest integer
    # https://github.com/python-pillow/Pillow/issues/1744

    # Arrange
    im = Image.new("RGB", (10, 10))
    assert im.size == (10, 10)

    # Act
    cropped = im.crop((0.9, 1.1, 4.2, 5.8))

    # Assert
    assert cropped.size == (3, 5)


def test_crop_crash():
    # Image.crop crashes prepatch with an access violation
    # apparently a use after free on Windows, see
    # https://github.com/python-pillow/Pillow/issues/1077

    test_img = "Tests/images/bmp/g/pal8-0.bmp"
    extents = (1, 1, 10, 10)
    # works prepatch
    with Image.open(test_img) as img:
        img2 = img.crop(extents)
    img2.load()

    # fail prepatch
    with Image.open(test_img) as img:
        img = img.crop(extents)
    img.load()


def test_crop_zero():

    im = Image.new("RGB", (0, 0), "white")

    cropped = im.crop((0, 0, 0, 0))
    assert cropped.size == (0, 0)

    cropped = im.crop((10, 10, 20, 20))
    assert cropped.size == (10, 10)
    assert cropped.getdata()[0] == (0, 0, 0)

    im = Image.new("RGB", (0, 0))

    cropped = im.crop((10, 10, 20, 20))
    assert cropped.size == (10, 10)
    assert cropped.getdata()[2] == (0, 0, 0)
