import pytest

from PIL import Image

from .helper import (
    assert_image_equal,
    assert_image_similar,
    fromstring,
    hopper,
    tostring,
)


def test_sanity():
    im = hopper()
    assert im.thumbnail((100, 100)) is None

    assert im.size == (100, 100)


def test_aspect():
    im = Image.new("L", (128, 128))
    im.thumbnail((100, 100))
    assert im.size == (100, 100)

    im = Image.new("L", (128, 256))
    im.thumbnail((100, 100))
    assert im.size == (50, 100)

    im = Image.new("L", (128, 256))
    im.thumbnail((50, 100))
    assert im.size == (50, 100)

    im = Image.new("L", (256, 128))
    im.thumbnail((100, 100))
    assert im.size == (100, 50)

    im = Image.new("L", (256, 128))
    im.thumbnail((100, 50))
    assert im.size == (100, 50)

    im = Image.new("L", (64, 64))
    im.thumbnail((100, 100))
    assert im.size == (64, 64)

    im = Image.new("L", (256, 162))  # ratio is 1.5802469136
    im.thumbnail((33, 33))
    assert im.size == (33, 21)  # ratio is 1.5714285714

    im = Image.new("L", (162, 256))  # ratio is 0.6328125
    im.thumbnail((33, 33))
    assert im.size == (21, 33)  # ratio is 0.6363636364

    im = Image.new("L", (145, 100))  # ratio is 1.45
    im.thumbnail((50, 50))
    assert im.size == (50, 34)  # ratio is 1.47058823529

    im = Image.new("L", (100, 145))  # ratio is 0.689655172414
    im.thumbnail((50, 50))
    assert im.size == (34, 50)  # ratio is 0.68

    im = Image.new("L", (100, 30))  # ratio is 3.333333333333
    im.thumbnail((75, 75))
    assert im.size == (75, 23)  # ratio is 3.260869565217


def test_division_by_zero():
    im = Image.new("L", (200, 2))
    im.thumbnail((75, 75))
    assert im.size == (75, 1)


def test_float():
    im = Image.new("L", (128, 128))
    im.thumbnail((99.9, 99.9))
    assert im.size == (99, 99)


def test_no_resize():
    # Check that draft() can resize the image to the destination size
    with Image.open("Tests/images/hopper.jpg") as im:
        im.draft(None, (64, 64))
        assert im.size == (64, 64)

    # Test thumbnail(), where only draft() is necessary to resize the image
    with Image.open("Tests/images/hopper.jpg") as im:
        im.thumbnail((64, 64))
        assert im.size == (64, 64)


# valgrind test is failing with memory allocated in libjpeg
@pytest.mark.valgrind_known_error(reason="Known Failing")
def test_DCT_scaling_edges():
    # Make an image with red borders and size (N * 8) + 1 to cross DCT grid
    im = Image.new("RGB", (257, 257), "red")
    im.paste(Image.new("RGB", (235, 235)), (11, 11))

    thumb = fromstring(tostring(im, "JPEG", quality=99, subsampling=0))
    # small reducing_gap to amplify the effect
    thumb.thumbnail((32, 32), Image.BICUBIC, reducing_gap=1.0)

    ref = im.resize((32, 32), Image.BICUBIC)
    # This is still JPEG, some error is present. Without the fix it is 11.5
    assert_image_similar(thumb, ref, 1.5)


def test_reducing_gap_values():
    im = hopper()
    im.thumbnail((18, 18), Image.BICUBIC)

    ref = hopper()
    ref.thumbnail((18, 18), Image.BICUBIC, reducing_gap=2.0)
    # reducing_gap=2.0 should be the default
    assert_image_equal(ref, im)

    ref = hopper()
    ref.thumbnail((18, 18), Image.BICUBIC, reducing_gap=None)
    with pytest.raises(AssertionError):
        assert_image_equal(ref, im)

    assert_image_similar(ref, im, 3.5)


def test_reducing_gap_for_DCT_scaling():
    with Image.open("Tests/images/hopper.jpg") as ref:
        # thumbnail should call draft with reducing_gap scale
        ref.draft(None, (18 * 3, 18 * 3))
        ref = ref.resize((18, 18), Image.BICUBIC)

        with Image.open("Tests/images/hopper.jpg") as im:
            im.thumbnail((18, 18), Image.BICUBIC, reducing_gap=3.0)

            assert_image_equal(ref, im)
