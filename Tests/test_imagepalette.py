import pytest

from PIL import Image, ImagePalette

from .helper import assert_image_equal, assert_image_equal_tofile


def test_sanity():

    palette = ImagePalette.ImagePalette("RGB", list(range(256)) * 3)
    assert len(palette.colors) == 256

    with pytest.warns(DeprecationWarning):
        with pytest.raises(ValueError):
            ImagePalette.ImagePalette("RGB", list(range(256)) * 3, 10)


def test_reload():
    with Image.open("Tests/images/hopper.gif") as im:
        original = im.copy()
        im.palette.dirty = 1
        assert_image_equal(im.convert("RGB"), original.convert("RGB"))


def test_getcolor():

    palette = ImagePalette.ImagePalette()
    assert len(palette.palette) == 0
    assert len(palette.colors) == 0

    test_map = {}
    for i in range(256):
        test_map[palette.getcolor((i, i, i))] = i
    assert len(test_map) == 256

    # Colors can be converted between RGB and RGBA
    rgba_palette = ImagePalette.ImagePalette("RGBA")
    assert rgba_palette.getcolor((0, 0, 0)) == rgba_palette.getcolor((0, 0, 0, 255))

    assert palette.getcolor((0, 0, 0)) == palette.getcolor((0, 0, 0, 255))

    # An error is raised when the palette is full
    with pytest.raises(ValueError):
        palette.getcolor((1, 2, 3))
    # But not if the image is not using one of the palette entries
    palette.getcolor((1, 2, 3), image=Image.new("P", (1, 1)))

    # Test unknown color specifier
    with pytest.raises(ValueError):
        palette.getcolor("unknown")


@pytest.mark.parametrize(
    "index, palette",
    [
        # Test when the palette is not full
        (0, ImagePalette.ImagePalette()),
        # Test when the palette is full
        (255, ImagePalette.ImagePalette("RGB", list(range(256)) * 3)),
    ],
)
def test_getcolor_not_special(index, palette):
    im = Image.new("P", (1, 1))

    # Do not use transparency index as a new color
    im.info["transparency"] = index
    index1 = palette.getcolor((0, 0, 0), im)
    assert index1 != index

    # Do not use background index as a new color
    im.info["background"] = index1
    index2 = palette.getcolor((0, 0, 1), im)
    assert index2 not in (index, index1)


def test_file(tmp_path):

    palette = ImagePalette.ImagePalette("RGB", list(range(256)) * 3)

    f = str(tmp_path / "temp.lut")

    palette.save(f)

    p = ImagePalette.load(f)

    # load returns raw palette information
    assert len(p[0]) == 768
    assert p[1] == "RGB"

    p = ImagePalette.raw(p[1], p[0])
    assert isinstance(p, ImagePalette.ImagePalette)
    assert p.palette == palette.tobytes()


def test_make_linear_lut():
    # Arrange
    black = 0
    white = 255

    # Act
    lut = ImagePalette.make_linear_lut(black, white)

    # Assert
    assert isinstance(lut, list)
    assert len(lut) == 256
    # Check values
    for i in range(0, len(lut)):
        assert lut[i] == i


def test_make_linear_lut_not_yet_implemented():
    # Update after FIXME
    # Arrange
    black = 1
    white = 255

    # Act
    with pytest.raises(NotImplementedError):
        ImagePalette.make_linear_lut(black, white)


def test_make_gamma_lut():
    # Arrange
    exp = 5

    # Act
    lut = ImagePalette.make_gamma_lut(exp)

    # Assert
    assert isinstance(lut, list)
    assert len(lut) == 256
    # Check a few values
    assert lut[0] == 0
    assert lut[63] == 0
    assert lut[127] == 8
    assert lut[191] == 60
    assert lut[255] == 255


def test_rawmode_valueerrors(tmp_path):
    # Arrange
    palette = ImagePalette.raw("RGB", list(range(256)) * 3)

    # Act / Assert
    with pytest.raises(ValueError):
        palette.tobytes()
    with pytest.raises(ValueError):
        palette.getcolor((1, 2, 3))
    f = str(tmp_path / "temp.lut")
    with pytest.raises(ValueError):
        palette.save(f)


def test_getdata():
    # Arrange
    data_in = list(range(256)) * 3
    palette = ImagePalette.ImagePalette("RGB", data_in)

    # Act
    mode, data_out = palette.getdata()

    # Assert
    assert mode == "RGB"


def test_rawmode_getdata():
    # Arrange
    data_in = list(range(256)) * 3
    palette = ImagePalette.raw("RGB", data_in)

    # Act
    rawmode, data_out = palette.getdata()

    # Assert
    assert rawmode == "RGB"
    assert data_in == data_out


def test_2bit_palette(tmp_path):
    # issue #2258, 2 bit palettes are corrupted.
    outfile = str(tmp_path / "temp.png")

    rgb = b"\x00" * 2 + b"\x01" * 2 + b"\x02" * 2
    img = Image.frombytes("P", (6, 1), rgb)
    img.putpalette(b"\xFF\x00\x00\x00\xFF\x00\x00\x00\xFF")  # RGB
    img.save(outfile, format="PNG")

    assert_image_equal_tofile(img, outfile)


def test_invalid_palette():
    with pytest.raises(OSError):
        ImagePalette.load("Tests/images/hopper.jpg")
