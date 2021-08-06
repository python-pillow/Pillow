import pytest

from PIL import Image, SgiImagePlugin

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar,
    hopper,
)


def test_rgb():
    # Created with ImageMagick then renamed:
    # convert hopper.ppm -compress None sgi:hopper.rgb
    test_file = "Tests/images/hopper.rgb"

    with Image.open(test_file) as im:
        assert_image_equal(im, hopper())
        assert im.get_format_mimetype() == "image/rgb"


def test_rgb16():
    assert_image_equal_tofile(hopper(), "Tests/images/hopper16.rgb")


def test_l():
    # Created with ImageMagick
    # convert hopper.ppm -monochrome -compress None sgi:hopper.bw
    test_file = "Tests/images/hopper.bw"

    with Image.open(test_file) as im:
        assert_image_similar(im, hopper("L"), 2)
        assert im.get_format_mimetype() == "image/sgi"


def test_rgba():
    # Created with ImageMagick:
    # convert transparent.png -compress None transparent.sgi
    test_file = "Tests/images/transparent.sgi"

    with Image.open(test_file) as im:
        assert_image_equal_tofile(im, "Tests/images/transparent.png")
        assert im.get_format_mimetype() == "image/sgi"


def test_rle():
    # Created with ImageMagick:
    # convert hopper.ppm  hopper.sgi
    test_file = "Tests/images/hopper.sgi"

    with Image.open(test_file) as im:
        assert_image_equal_tofile(im, "Tests/images/hopper.rgb")


def test_rle16():
    test_file = "Tests/images/tv16.sgi"

    with Image.open(test_file) as im:
        assert_image_equal_tofile(im, "Tests/images/tv.rgb")


def test_invalid_file():
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(ValueError):
        SgiImagePlugin.SgiImageFile(invalid_file)


def test_write(tmp_path):
    def roundtrip(img):
        out = str(tmp_path / "temp.sgi")
        img.save(out, format="sgi")
        assert_image_equal_tofile(img, out)

        out = str(tmp_path / "fp.sgi")
        with open(out, "wb") as fp:
            img.save(fp)
            assert_image_equal_tofile(img, out)

            assert not fp.closed

    for mode in ("L", "RGB", "RGBA"):
        roundtrip(hopper(mode))

    # Test 1 dimension for an L mode image
    roundtrip(Image.new("L", (10, 1)))


def test_write16(tmp_path):
    test_file = "Tests/images/hopper16.rgb"

    with Image.open(test_file) as im:
        out = str(tmp_path / "temp.sgi")
        im.save(out, format="sgi", bpc=2)

        assert_image_equal_tofile(im, out)


def test_unsupported_mode(tmp_path):
    im = hopper("LA")
    out = str(tmp_path / "temp.sgi")

    with pytest.raises(ValueError):
        im.save(out, format="sgi")
