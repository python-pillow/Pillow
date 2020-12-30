import pytest

from PIL import Image, ImageMath, ImageMode

from .helper import convert_to_comparable, skip_unless_feature

codecs = dir(Image.core)


# There are several internal implementations
remarkable_factors = [
    # special implementations
    1,
    2,
    3,
    4,
    5,
    6,
    # 1xN implementation
    (1, 2),
    (1, 3),
    (1, 4),
    (1, 7),
    # Nx1 implementation
    (2, 1),
    (3, 1),
    (4, 1),
    (7, 1),
    # general implementation with different paths
    (4, 6),
    (5, 6),
    (4, 7),
    (5, 7),
    (19, 17),
]

gradients_image = Image.open("Tests/images/radial_gradients.png")
gradients_image.load()


def test_args_factor():
    im = Image.new("L", (10, 10))

    assert (4, 4) == im.reduce(3).size
    assert (4, 10) == im.reduce((3, 1)).size
    assert (10, 4) == im.reduce((1, 3)).size

    with pytest.raises(ValueError):
        im.reduce(0)
    with pytest.raises(TypeError):
        im.reduce(2.0)
    with pytest.raises(ValueError):
        im.reduce((0, 10))


def test_args_box():
    im = Image.new("L", (10, 10))

    assert (5, 5) == im.reduce(2, (0, 0, 10, 10)).size
    assert (1, 1) == im.reduce(2, (5, 5, 6, 6)).size

    with pytest.raises(TypeError):
        im.reduce(2, "stri")
    with pytest.raises(TypeError):
        im.reduce(2, 2)
    with pytest.raises(ValueError):
        im.reduce(2, (0, 0, 11, 10))
    with pytest.raises(ValueError):
        im.reduce(2, (0, 0, 10, 11))
    with pytest.raises(ValueError):
        im.reduce(2, (-1, 0, 10, 10))
    with pytest.raises(ValueError):
        im.reduce(2, (0, -1, 10, 10))
    with pytest.raises(ValueError):
        im.reduce(2, (0, 5, 10, 5))
    with pytest.raises(ValueError):
        im.reduce(2, (5, 0, 5, 10))


def test_unsupported_modes():
    im = Image.new("P", (10, 10))
    with pytest.raises(ValueError):
        im.reduce(3)

    im = Image.new("1", (10, 10))
    with pytest.raises(ValueError):
        im.reduce(3)

    im = Image.new("I;16", (10, 10))
    with pytest.raises(ValueError):
        im.reduce(3)


def get_image(mode):
    mode_info = ImageMode.getmode(mode)
    if mode_info.basetype == "L":
        bands = [gradients_image]
        for _ in mode_info.bands[1:]:
            # rotate previous image
            band = bands[-1].transpose(Image.ROTATE_90)
            bands.append(band)
        # Correct alpha channel by transforming completely transparent pixels.
        # Low alpha values also emphasize error after alpha multiplication.
        if mode.endswith("A"):
            bands[-1] = bands[-1].point(lambda x: int(85 + x / 1.5))
        im = Image.merge(mode, bands)
    else:
        assert len(mode_info.bands) == 1
        im = gradients_image.convert(mode)
    # change the height to make a not-square image
    return im.crop((0, 0, im.width, im.height - 5))


def compare_reduce_with_box(im, factor):
    box = (11, 13, 146, 164)
    reduced = im.reduce(factor, box=box)
    reference = im.crop(box).reduce(factor)
    assert reduced == reference


def compare_reduce_with_reference(im, factor, average_diff=0.4, max_diff=1):
    """Image.reduce() should look very similar to Image.resize(BOX).

    A reference image is compiled from a large source area
    and possible last column and last row.
    +-----------+
    |..........c|
    |..........c|
    |..........c|
    |rrrrrrrrrrp|
    +-----------+
    """
    reduced = im.reduce(factor)

    if not isinstance(factor, (list, tuple)):
        factor = (factor, factor)

    reference = Image.new(im.mode, reduced.size)
    area_size = (im.size[0] // factor[0], im.size[1] // factor[1])
    area_box = (0, 0, area_size[0] * factor[0], area_size[1] * factor[1])
    area = im.resize(area_size, Image.BOX, area_box)
    reference.paste(area, (0, 0))

    if area_size[0] < reduced.size[0]:
        assert reduced.size[0] - area_size[0] == 1
        last_column_box = (area_box[2], 0, im.size[0], area_box[3])
        last_column = im.resize((1, area_size[1]), Image.BOX, last_column_box)
        reference.paste(last_column, (area_size[0], 0))

    if area_size[1] < reduced.size[1]:
        assert reduced.size[1] - area_size[1] == 1
        last_row_box = (0, area_box[3], area_box[2], im.size[1])
        last_row = im.resize((area_size[0], 1), Image.BOX, last_row_box)
        reference.paste(last_row, (0, area_size[1]))

    if area_size[0] < reduced.size[0] and area_size[1] < reduced.size[1]:
        last_pixel_box = (area_box[2], area_box[3], im.size[0], im.size[1])
        last_pixel = im.resize((1, 1), Image.BOX, last_pixel_box)
        reference.paste(last_pixel, area_size)

    assert_compare_images(reduced, reference, average_diff, max_diff)


def assert_compare_images(a, b, max_average_diff, max_diff=255):
    assert a.mode == b.mode, f"got mode {repr(a.mode)}, expected {repr(b.mode)}"
    assert a.size == b.size, f"got size {repr(a.size)}, expected {repr(b.size)}"

    a, b = convert_to_comparable(a, b)

    bands = ImageMode.getmode(a.mode).bands
    for band, ach, bch in zip(bands, a.split(), b.split()):
        ch_diff = ImageMath.eval("convert(abs(a - b), 'L')", a=ach, b=bch)
        ch_hist = ch_diff.histogram()

        average_diff = sum(i * num for i, num in enumerate(ch_hist)) / (
            a.size[0] * a.size[1]
        )
        msg = (
            f"average pixel value difference {average_diff:.4f} > "
            f"expected {max_average_diff:.4f} for '{band}' band"
        )
        assert max_average_diff >= average_diff, msg

        last_diff = [i for i, num in enumerate(ch_hist) if num > 0][-1]
        assert max_diff >= last_diff, (
            f"max pixel value difference {last_diff} > expected {max_diff} "
            f"for '{band}' band"
        )


def test_mode_L():
    im = get_image("L")
    for factor in remarkable_factors:
        compare_reduce_with_reference(im, factor)
        compare_reduce_with_box(im, factor)


def test_mode_LA():
    im = get_image("LA")
    for factor in remarkable_factors:
        compare_reduce_with_reference(im, factor, 0.8, 5)

    # With opaque alpha, an error should be way smaller.
    im.putalpha(Image.new("L", im.size, 255))
    for factor in remarkable_factors:
        compare_reduce_with_reference(im, factor)
        compare_reduce_with_box(im, factor)


def test_mode_La():
    im = get_image("La")
    for factor in remarkable_factors:
        compare_reduce_with_reference(im, factor)
        compare_reduce_with_box(im, factor)


def test_mode_RGB():
    im = get_image("RGB")
    for factor in remarkable_factors:
        compare_reduce_with_reference(im, factor)
        compare_reduce_with_box(im, factor)


def test_mode_RGBA():
    im = get_image("RGBA")
    for factor in remarkable_factors:
        compare_reduce_with_reference(im, factor, 0.8, 5)

    # With opaque alpha, an error should be way smaller.
    im.putalpha(Image.new("L", im.size, 255))
    for factor in remarkable_factors:
        compare_reduce_with_reference(im, factor)
        compare_reduce_with_box(im, factor)


def test_mode_RGBa():
    im = get_image("RGBa")
    for factor in remarkable_factors:
        compare_reduce_with_reference(im, factor)
        compare_reduce_with_box(im, factor)


def test_mode_I():
    im = get_image("I")
    for factor in remarkable_factors:
        compare_reduce_with_reference(im, factor)
        compare_reduce_with_box(im, factor)


def test_mode_F():
    im = get_image("F")
    for factor in remarkable_factors:
        compare_reduce_with_reference(im, factor, 0, 0)
        compare_reduce_with_box(im, factor)


@skip_unless_feature("jpg_2000")
def test_jpeg2k():
    with Image.open("Tests/images/test-card-lossless.jp2") as im:
        assert im.reduce(2).size == (320, 240)
