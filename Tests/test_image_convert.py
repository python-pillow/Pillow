import pytest

from PIL import Image

from .helper import assert_image, assert_image_equal, assert_image_similar, hopper


def test_sanity():
    def convert(im, mode):
        out = im.convert(mode)
        assert out.mode == mode
        assert out.size == im.size

    modes = (
        "1",
        "L",
        "LA",
        "P",
        "PA",
        "I",
        "F",
        "RGB",
        "RGBA",
        "RGBX",
        "CMYK",
        "YCbCr",
        "HSV",
    )

    for mode in modes:
        im = hopper(mode)
        for mode in modes:
            convert(im, mode)

        # Check 0
        im = Image.new(mode, (0, 0))
        for mode in modes:
            convert(im, mode)


def test_default():

    im = hopper("P")
    assert_image(im, "P", im.size)
    converted_im = im.convert()
    assert_image(converted_im, "RGB", im.size)
    converted_im = im.convert()
    assert_image(converted_im, "RGB", im.size)

    im.info["transparency"] = 0
    converted_im = im.convert()
    assert_image(converted_im, "RGBA", im.size)


# ref https://github.com/python-pillow/Pillow/issues/274


def _test_float_conversion(im):
    orig = im.getpixel((5, 5))
    converted = im.convert("F").getpixel((5, 5))
    assert orig == converted


def test_8bit():
    with Image.open("Tests/images/hopper.jpg") as im:
        _test_float_conversion(im.convert("L"))


def test_16bit():
    with Image.open("Tests/images/16bit.cropped.tif") as im:
        _test_float_conversion(im)


def test_16bit_workaround():
    with Image.open("Tests/images/16bit.cropped.tif") as im:
        _test_float_conversion(im.convert("I"))


def test_rgba_p():
    im = hopper("RGBA")
    im.putalpha(hopper("L"))

    converted = im.convert("P")
    comparable = converted.convert("RGBA")

    assert_image_similar(im, comparable, 20)


def test_trns_p(tmp_path):
    im = hopper("P")
    im.info["transparency"] = 0

    f = str(tmp_path / "temp.png")

    im_l = im.convert("L")
    assert im_l.info["transparency"] == 0  # undone
    im_l.save(f)

    im_rgb = im.convert("RGB")
    assert im_rgb.info["transparency"] == (0, 1, 2)  # undone
    im_rgb.save(f)


# ref https://github.com/python-pillow/Pillow/issues/664


@pytest.mark.parametrize("mode", ("LA", "PA", "RGBA"))
def test_trns_p_transparency(mode):
    # Arrange
    im = hopper("P")
    im.info["transparency"] = 128

    # Act
    converted_im = im.convert(mode)

    # Assert
    assert "transparency" not in converted_im.info
    if mode == "PA":
        assert converted_im.palette is not None
    else:
        # https://github.com/python-pillow/Pillow/issues/2702
        assert converted_im.palette is None


def test_trns_l(tmp_path):
    im = hopper("L")
    im.info["transparency"] = 128

    f = str(tmp_path / "temp.png")

    im_rgb = im.convert("RGB")
    assert im_rgb.info["transparency"] == (128, 128, 128)  # undone
    im_rgb.save(f)

    im_p = im.convert("P")
    assert "transparency" in im_p.info
    im_p.save(f)

    im_p = im.convert("P", palette=Image.ADAPTIVE)
    assert "transparency" in im_p.info
    im_p.save(f)


def test_trns_RGB(tmp_path):
    im = hopper("RGB")
    im.info["transparency"] = im.getpixel((0, 0))

    f = str(tmp_path / "temp.png")

    im_l = im.convert("L")
    assert im_l.info["transparency"] == im_l.getpixel((0, 0))  # undone
    im_l.save(f)

    im_p = im.convert("P")
    assert "transparency" in im_p.info
    im_p.save(f)

    im_rgba = im.convert("RGBA")
    assert "transparency" not in im_rgba.info
    im_rgba.save(f)

    im_p = pytest.warns(UserWarning, im.convert, "P", palette=Image.ADAPTIVE)
    assert "transparency" not in im_p.info
    im_p.save(f)

    im = Image.new("RGB", (1, 1))
    im.info["transparency"] = im.getpixel((0, 0))
    im_p = im.convert("P", palette=Image.ADAPTIVE)
    assert im_p.info["transparency"] == im_p.getpixel((0, 0))
    im_p.save(f)


def test_gif_with_rgba_palette_to_p():
    # See https://github.com/python-pillow/Pillow/issues/2433
    with Image.open("Tests/images/hopper.gif") as im:
        im.info["transparency"] = 255
        im.load()
        assert im.palette.mode == "RGB"
        im_p = im.convert("P")

    # Should not raise ValueError: unrecognized raw mode
    im_p.load()


def test_p_la():
    im = hopper("RGBA")
    alpha = hopper("L")
    im.putalpha(alpha)

    comparable = im.convert("P").convert("LA").getchannel("A")

    assert_image_similar(alpha, comparable, 5)


def test_matrix_illegal_conversion():
    # Arrange
    im = hopper("CMYK")
    # fmt: off
    matrix = (
        0.412453, 0.357580, 0.180423, 0,
        0.212671, 0.715160, 0.072169, 0,
        0.019334, 0.119193, 0.950227, 0)
    # fmt: on
    assert im.mode != "RGB"

    # Act / Assert
    with pytest.raises(ValueError):
        im.convert(mode="CMYK", matrix=matrix)


def test_matrix_wrong_mode():
    # Arrange
    im = hopper("L")
    # fmt: off
    matrix = (
        0.412453, 0.357580, 0.180423, 0,
        0.212671, 0.715160, 0.072169, 0,
        0.019334, 0.119193, 0.950227, 0)
    # fmt: on
    assert im.mode == "L"

    # Act / Assert
    with pytest.raises(ValueError):
        im.convert(mode="L", matrix=matrix)


def test_matrix_xyz():
    def matrix_convert(mode):
        # Arrange
        im = hopper("RGB")
        im.info["transparency"] = (255, 0, 0)
        # fmt: off
        matrix = (
            0.412453, 0.357580, 0.180423, 0,
            0.212671, 0.715160, 0.072169, 0,
            0.019334, 0.119193, 0.950227, 0)
        # fmt: on
        assert im.mode == "RGB"

        # Act
        # Convert an RGB image to the CIE XYZ colour space
        converted_im = im.convert(mode=mode, matrix=matrix)

        # Assert
        assert converted_im.mode == mode
        assert converted_im.size == im.size
        with Image.open("Tests/images/hopper-XYZ.png") as target:
            if converted_im.mode == "RGB":
                assert_image_similar(converted_im, target, 3)
                assert converted_im.info["transparency"] == (105, 54, 4)
            else:
                assert_image_similar(converted_im, target.getchannel(0), 1)
                assert converted_im.info["transparency"] == 105

    matrix_convert("RGB")
    matrix_convert("L")


def test_matrix_identity():
    # Arrange
    im = hopper("RGB")
    # fmt: off
    identity_matrix = (
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0)
    # fmt: on
    assert im.mode == "RGB"

    # Act
    # Convert with an identity matrix
    converted_im = im.convert(mode="RGB", matrix=identity_matrix)

    # Assert
    # No change
    assert_image_equal(converted_im, im)
