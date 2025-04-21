from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import IO

import pytest

from PIL import Image, ImageFile, WmfImagePlugin

from .helper import assert_image_equal_tofile, assert_image_similar_tofile, hopper


def test_load_raw() -> None:
    # Test basic EMF open and rendering
    with Image.open("Tests/images/drawing.emf") as im:
        if hasattr(Image.core, "drawwmf"):
            # Currently, support for WMF/EMF is Windows-only
            im.load()
            # Compare to reference rendering
            assert_image_similar_tofile(im, "Tests/images/drawing_emf_ref.png", 0)

    # Test basic WMF open and rendering
    with Image.open("Tests/images/drawing.wmf") as im:
        if hasattr(Image.core, "drawwmf"):
            # Currently, support for WMF/EMF is Windows-only
            im.load()
            # Compare to reference rendering
            assert_image_similar_tofile(im, "Tests/images/drawing_wmf_ref.png", 2.0)


def test_load() -> None:
    with Image.open("Tests/images/drawing.emf") as im:
        if hasattr(Image.core, "drawwmf"):
            px = im.load()
            assert px is not None
            assert px[0, 0] == (255, 255, 255)


def test_load_zero_inch() -> None:
    b = BytesIO(b"\xd7\xcd\xc6\x9a\x00\x00" + b"\x00" * 10)
    with pytest.raises(ValueError):
        with Image.open(b):
            pass


def test_render() -> None:
    with open("Tests/images/drawing.emf", "rb") as fp:
        data = fp.read()
    b = BytesIO(data[:808] + b"\x00" + data[809:])
    with Image.open(b) as im:
        if hasattr(Image.core, "drawwmf"):
            assert_image_equal_tofile(im, "Tests/images/drawing.emf")


def test_register_handler(tmp_path: Path) -> None:
    class TestHandler(ImageFile.StubHandler):
        methodCalled = False

        def load(self, im: ImageFile.StubImageFile) -> Image.Image:
            return Image.new("RGB", (1, 1))

        def save(self, im: Image.Image, fp: IO[bytes], filename: str) -> None:
            self.methodCalled = True

    handler = TestHandler()
    original_handler = WmfImagePlugin._handler
    WmfImagePlugin.register_handler(handler)

    im = hopper()
    tmpfile = tmp_path / "temp.wmf"
    im.save(tmpfile)
    assert handler.methodCalled

    # Restore the state before this test
    WmfImagePlugin.register_handler(original_handler)


def test_load_float_dpi() -> None:
    with Image.open("Tests/images/drawing.emf") as im:
        assert im.info["dpi"] == 1423.7668161434979

    with open("Tests/images/drawing.emf", "rb") as fp:
        data = fp.read()
    b = BytesIO(data[:8] + b"\x06\xfa" + data[10:])
    with Image.open(b) as im:
        assert im.info["dpi"][0] == 2540


def test_load_set_dpi() -> None:
    with Image.open("Tests/images/drawing.wmf") as im:
        assert isinstance(im, WmfImagePlugin.WmfStubImageFile)
        assert im.size == (82, 82)

        if hasattr(Image.core, "drawwmf"):
            im.load(144)
            assert im.size == (164, 164)

            assert_image_similar_tofile(im, "Tests/images/drawing_wmf_ref_144.png", 2.1)

    with Image.open("Tests/images/drawing.emf") as im:
        assert im.size == (1625, 1625)

        if not hasattr(Image.core, "drawwmf"):
            return
        assert isinstance(im, WmfImagePlugin.WmfStubImageFile)
        im.load(im.info["dpi"])
        assert im.size == (1625, 1625)

    with Image.open("Tests/images/drawing.emf") as im:
        assert isinstance(im, WmfImagePlugin.WmfStubImageFile)
        im.load((72, 144))
        assert im.size == (82, 164)

        assert_image_equal_tofile(im, "Tests/images/drawing_emf_ref_72_144.png")


@pytest.mark.parametrize("ext", (".wmf", ".emf"))
def test_save(ext: str, tmp_path: Path) -> None:
    im = hopper()

    tmpfile = tmp_path / ("temp" + ext)
    with pytest.raises(OSError):
        im.save(tmpfile)
