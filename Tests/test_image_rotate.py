from PIL import Image

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar,
    hopper,
)


def rotate(im, mode, angle, center=None, translate=None):
    out = im.rotate(angle, center=center, translate=translate)
    assert out.mode == mode
    assert out.size == im.size  # default rotate clips output
    out = im.rotate(angle, center=center, translate=translate, expand=1)
    assert out.mode == mode
    if angle % 180 == 0:
        assert out.size == im.size
    elif im.size == (0, 0):
        assert out.size == im.size
    else:
        assert out.size != im.size


def test_mode():
    for mode in ("1", "P", "L", "RGB", "I", "F"):
        im = hopper(mode)
        rotate(im, mode, 45)


def test_angle():
    for angle in (0, 90, 180, 270):
        with Image.open("Tests/images/test-card.png") as im:
            rotate(im, im.mode, angle)

        im = hopper()
        assert_image_equal(im.rotate(angle), im.rotate(angle, expand=1))


def test_zero():
    for angle in (0, 45, 90, 180, 270):
        im = Image.new("RGB", (0, 0))
        rotate(im, im.mode, angle)


def test_resample():
    # Target image creation, inspected by eye.
    # >>> im = Image.open('Tests/images/hopper.ppm')
    # >>> im = im.rotate(45, resample=Image.BICUBIC, expand=True)
    # >>> im.save('Tests/images/hopper_45.png')

    with Image.open("Tests/images/hopper_45.png") as target:
        for (resample, epsilon) in (
            (Image.NEAREST, 10),
            (Image.BILINEAR, 5),
            (Image.BICUBIC, 0),
        ):
            im = hopper()
            im = im.rotate(45, resample=resample, expand=True)
            assert_image_similar(im, target, epsilon)


def test_center_0():
    im = hopper()
    im = im.rotate(45, center=(0, 0), resample=Image.BICUBIC)

    with Image.open("Tests/images/hopper_45.png") as target:
        target_origin = target.size[1] / 2
        target = target.crop((0, target_origin, 128, target_origin + 128))

    assert_image_similar(im, target, 15)


def test_center_14():
    im = hopper()
    im = im.rotate(45, center=(14, 14), resample=Image.BICUBIC)

    with Image.open("Tests/images/hopper_45.png") as target:
        target_origin = target.size[1] / 2 - 14
        target = target.crop((6, target_origin, 128 + 6, target_origin + 128))

        assert_image_similar(im, target, 10)


def test_translate():
    im = hopper()
    with Image.open("Tests/images/hopper_45.png") as target:
        target_origin = (target.size[1] / 2 - 64) - 5
        target = target.crop(
            (target_origin, target_origin, target_origin + 128, target_origin + 128)
        )

    im = im.rotate(45, translate=(5, 5), resample=Image.BICUBIC)

    assert_image_similar(im, target, 1)


def test_fastpath_center():
    # if the center is -1,-1 and we rotate by 90<=x<=270 the
    # resulting image should be black
    for angle in (90, 180, 270):
        im = hopper().rotate(angle, center=(-1, -1))
        assert_image_equal(im, Image.new("RGB", im.size, "black"))


def test_fastpath_translate():
    # if we post-translate by -128
    # resulting image should be black
    for angle in (0, 90, 180, 270):
        im = hopper().rotate(angle, translate=(-128, -128))
        assert_image_equal(im, Image.new("RGB", im.size, "black"))


def test_center():
    im = hopper()
    rotate(im, im.mode, 45, center=(0, 0))
    rotate(im, im.mode, 45, translate=(im.size[0] / 2, 0))
    rotate(im, im.mode, 45, center=(0, 0), translate=(im.size[0] / 2, 0))


def test_rotate_no_fill():
    im = Image.new("RGB", (100, 100), "green")
    im = im.rotate(45)
    assert_image_equal_tofile(im, "Tests/images/rotate_45_no_fill.png")


def test_rotate_with_fill():
    im = Image.new("RGB", (100, 100), "green")
    im = im.rotate(45, fillcolor="white")
    assert_image_equal_tofile(im, "Tests/images/rotate_45_with_fill.png")


def test_alpha_rotate_no_fill():
    # Alpha images are handled differently internally
    im = Image.new("RGBA", (10, 10), "green")
    im = im.rotate(45, expand=1)
    corner = im.getpixel((0, 0))
    assert corner == (0, 0, 0, 0)


def test_alpha_rotate_with_fill():
    # Alpha images are handled differently internally
    im = Image.new("RGBA", (10, 10), "green")
    im = im.rotate(45, expand=1, fillcolor=(255, 0, 0, 255))
    corner = im.getpixel((0, 0))
    assert corner == (255, 0, 0, 255)
