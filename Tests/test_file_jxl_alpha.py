from __future__ import annotations

from PIL import Image

from .helper import assert_image_similar_tofile, skip_unless_feature

pytestmark = [skip_unless_feature("jpegxl")]


def test_read_rgba() -> None:
    """
    Can we read an RGBA mode file without error?
    Does it have the bits we expect?
    """

    # Generated with `cjxl transparent.png transparent.jxl -q 100 -e 8`
    with Image.open("Tests/images/transparent.jxl") as im:
        assert im.mode == "RGBA"
        assert im.size == (200, 150)
        assert im.format == "JPEG XL"
        im.load()
        im.getdata()

        im.tobytes()

        assert_image_similar_tofile(im, "Tests/images/transparent.png", 1)
