from __future__ import annotations

import pytest

from PIL import ImageQt

from .helper import assert_image_equal, assert_image_equal_tofile, hopper

TYPE_CHECKING = False
if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.skipif(
    not ImageQt.qt_is_installed, reason="Qt bindings are not installed"
)

if ImageQt.qt_is_installed:
    from PIL.ImageQt import QImage


@pytest.mark.parametrize("mode", ("RGB", "RGBA", "L", "P", "1"))
def test_sanity(mode: str, tmp_path: Path) -> None:
    src = hopper(mode)
    data = ImageQt.toqimage(src)

    assert isinstance(data, QImage)
    assert not data.isNull()

    # reload directly from the qimage
    rt = ImageQt.fromqimage(data)
    if mode in ("L", "P", "1"):
        assert_image_equal(rt, src.convert("RGB"))
    else:
        assert_image_equal(rt, src)

    if mode == "1":
        # BW appears to not save correctly on Qt
        # kicks out errors on console:
        #     libpng warning: Invalid color type/bit depth combination
        #                     in IHDR
        #     libpng error: Invalid IHDR data
        return

    # Test saving the file
    tempfile = str(tmp_path / f"temp_{mode}.png")
    data.save(tempfile)

    # Check that it actually worked.
    assert_image_equal_tofile(src, tempfile)
