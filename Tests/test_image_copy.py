import copy

import pytest

from PIL import Image

from .helper import hopper, skip_unless_feature


@pytest.mark.parametrize("mode", ("1", "P", "L", "RGB", "I", "F"))
def test_copy(mode):
    cropped_coordinates = (10, 10, 20, 20)
    cropped_size = (10, 10)

    # Internal copy method
    im = hopper(mode)
    out = im.copy()
    assert out.mode == im.mode
    assert out.size == im.size

    # Python's copy method
    im = hopper(mode)
    out = copy.copy(im)
    assert out.mode == im.mode
    assert out.size == im.size

    # Internal copy method on a cropped image
    im = hopper(mode)
    out = im.crop(cropped_coordinates).copy()
    assert out.mode == im.mode
    assert out.size == cropped_size

    # Python's copy method on a cropped image
    im = hopper(mode)
    out = copy.copy(im.crop(cropped_coordinates))
    assert out.mode == im.mode
    assert out.size == cropped_size


def test_copy_zero():
    im = Image.new("RGB", (0, 0))
    out = im.copy()
    assert out.mode == im.mode
    assert out.size == im.size


@skip_unless_feature("libtiff")
def test_deepcopy():
    with Image.open("Tests/images/g4_orientation_5.tif") as im:
        out = copy.deepcopy(im)
    assert out.size == (590, 88)
