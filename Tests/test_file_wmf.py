from __future__ import annotations

from pathlib import Path
from typing import IO

import pytest

from PIL import Image, ImageFile, WmfImagePlugin

from .helper import assert_image_similar_tofile, hopper


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
    tmpfile = str(tmp_path / "temp.wmf")
    im.save(tmpfile)
    assert handler.methodCalled

    # Restore the state before this test
    WmfImagePlugin.register_handler(original_handler)


def test_load_float_dpi() -> None:
    with Image.open("Tests/images/drawing.emf") as im:
        assert im.info["dpi"] == 1423.7668161434979


def test_load_set_dpi() -> None:
    with Image.open("Tests/images/drawing.wmf") as im:
        assert isinstance(im, WmfImagePlugin.WmfStubImageFile)
        assert im.size == (82, 82)

        if hasattr(Image.core, "drawwmf"):
            im.load(144)
            assert im.size == (164, 164)

            assert_image_similar_tofile(im, "Tests/images/drawing_wmf_ref_144.png", 2.1)


@pytest.mark.parametrize("ext", (".wmf", ".emf"))
def test_save(ext: str, tmp_path: Path) -> None:
    im = hopper()

    tmpfile = str(tmp_path / ("temp" + ext))
    with pytest.raises(OSError):
        im.save(tmpfile)
