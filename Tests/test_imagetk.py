import pytest

from PIL import Image

from .helper import assert_image_equal, hopper

try:
    import tkinter as tk

    from PIL import ImageTk

    dir(ImageTk)
    HAS_TK = True
except (OSError, ImportError):
    # Skipped via pytestmark
    HAS_TK = False

TK_MODES = ("1", "L", "P", "RGB", "RGBA")


pytestmark = pytest.mark.skipif(not HAS_TK, reason="Tk not installed")


def setup_module():
    try:
        # setup tk
        tk.Frame()
        # root = tk.Tk()
    except tk.TclError as v:
        pytest.skip(f"TCL Error: {v}")


def test_kw():
    TEST_JPG = "Tests/images/hopper.jpg"
    TEST_PNG = "Tests/images/hopper.png"
    with Image.open(TEST_JPG) as im1:
        with Image.open(TEST_PNG) as im2:
            with open(TEST_PNG, "rb") as fp:
                data = fp.read()
            kw = {"file": TEST_JPG, "data": data}

            # Test "file"
            im = ImageTk._get_image_from_kw(kw)
            assert_image_equal(im, im1)

            # Test "data"
            im = ImageTk._get_image_from_kw(kw)
            assert_image_equal(im, im2)

    # Test no relevant entry
    im = ImageTk._get_image_from_kw(kw)
    assert im is None


def test_photoimage():
    for mode in TK_MODES:
        # test as image:
        im = hopper(mode)

        # this should not crash
        im_tk = ImageTk.PhotoImage(im)

        assert im_tk.width() == im.width
        assert im_tk.height() == im.height

        reloaded = ImageTk.getimage(im_tk)
        assert_image_equal(reloaded, im.convert("RGBA"))


def test_photoimage_blank():
    # test a image using mode/size:
    for mode in TK_MODES:
        im_tk = ImageTk.PhotoImage(mode, (100, 100))

        assert im_tk.width() == 100
        assert im_tk.height() == 100

        # reloaded = ImageTk.getimage(im_tk)
        # assert_image_equal(reloaded, im)


def test_bitmapimage():
    im = hopper("1")

    # this should not crash
    im_tk = ImageTk.BitmapImage(im)

    assert im_tk.width() == im.width
    assert im_tk.height() == im.height

    # reloaded = ImageTk.getimage(im_tk)
    # assert_image_equal(reloaded, im)
