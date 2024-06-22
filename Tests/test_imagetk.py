from __future__ import annotations

import gc
import pytest
import tkinter as tk
from unittest import mock

from PIL import Image
from PIL import ImageTk

from .helper import assert_image_equal, hopper

TK_MODES = ("1", "L", "P", "RGB", "RGBA")

try:
    dir(ImageTk)
    HAS_TK = True
except (OSError, ImportError):
    HAS_TK = False

pytestmark = pytest.mark.skipif(not HAS_TK, reason="Tk not installed")


def setup_module() -> None:
    try:
        # setup tk
        tk.Frame()
    except RuntimeError as v:
        pytest.skip(f"RuntimeError: {v}")
    except tk.TclError as v:
        pytest.skip(f"TCL Error: {v}")


def test_kw() -> None:
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


@pytest.mark.parametrize("mode", TK_MODES)
def test_photoimage(mode: str) -> None:
    # test as image:
    im = hopper(mode)

    # this should not crash
    im_tk = ImageTk.PhotoImage(im)

    assert im_tk.width() == im.width
    assert im_tk.height() == im.height

    reloaded = ImageTk.getimage(im_tk)
    assert_image_equal(reloaded, im.convert("RGBA"))


def test_photoimage_apply_transparency() -> None:
    with Image.open("Tests/images/pil123p.png") as im:
        im_tk = ImageTk.PhotoImage(im)
        reloaded = ImageTk.getimage(im_tk)
        assert_image_equal(reloaded, im.convert("RGBA"))


@pytest.mark.parametrize("mode", TK_MODES)
def test_photoimage_blank(mode: str) -> None:
    # test a image using mode/size:
    im_tk = ImageTk.PhotoImage(mode, (100, 100))

    assert im_tk.width() == 100
    assert im_tk.height() == 100

    im = Image.new(mode, (100, 100))
    reloaded = ImageTk.getimage(im_tk)
    assert_image_equal(reloaded.convert(mode), im)


def test_bitmapimage() -> None:
    im = hopper("1")

    # this should not crash
    im_tk = ImageTk.BitmapImage(im)

    assert im_tk.width() == im.width
    assert im_tk.height() == im.height

    # reloaded = ImageTk.getimage(im_tk)
    # assert_image_equal(reloaded, im)


def test_bitmapimage_del() -> None:
    # Set up an image
    im = Image.new("1", (10, 10))

    # Mock the tkinter PhotoImage to track calls
    with mock.patch.object(tk, 'BitmapImage', wraps=tk.BitmapImage) as mock_bitmapimage:
        # Create an instance of BitmapImage
        bitmap_image = ImageTk.BitmapImage(im)
        
        # Ensure the BitmapImage was created
        assert mock_bitmapimage.call_count == 1

        # Get the internal Tkinter image object
        tk_image = bitmap_image._BitmapImage__photo
        
        # Mock the tk.call method to track the 'image delete' call
        with mock.patch.object(tk_image.tk, 'call', wraps=tk_image.tk.call) as mock_tk_call:
            # Delete the instance and force garbage collection
            del bitmap_image
            gc.collect()

            # Check that the 'image delete' command was called
            mock_tk_call.assert_any_call("image", "delete", tk_image.name)
