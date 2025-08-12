from __future__ import annotations

from io import BytesIO

import pytest

from PIL import GbrImagePlugin, Image, _binary

from .helper import assert_image_equal_tofile


def test_gbr_file() -> None:
    with Image.open("Tests/images/gbr.gbr") as im:
        assert_image_equal_tofile(im, "Tests/images/gbr.png")


def test_load() -> None:
    with Image.open("Tests/images/gbr.gbr") as im:
        px = im.load()
        assert px is not None
        assert px[0, 0] == (0, 0, 0, 0)

        # Test again now that it has already been loaded once
        px = im.load()
        assert px is not None
        assert px[0, 0] == (0, 0, 0, 0)


def test_multiple_load_operations() -> None:
    with Image.open("Tests/images/gbr.gbr") as im:
        im.load()
        im.load()
        assert_image_equal_tofile(im, "Tests/images/gbr.png")


def create_gbr_image(info: dict[str, int] = {}, magic_number=b"") -> BytesIO:
    return BytesIO(
        b"".join(
            _binary.o32be(i)
            for i in [
                info.get("header_size", 20),
                info.get("version", 1),
                info.get("width", 1),
                info.get("height", 1),
                info.get("color_depth", 1),
            ]
        )
        + magic_number
    )


def test_invalid_file() -> None:
    for f in [
        create_gbr_image({"header_size": 0}),
        create_gbr_image({"width": 0}),
        create_gbr_image({"height": 0}),
    ]:
        with pytest.raises(SyntaxError, match="not a GIMP brush"):
            GbrImagePlugin.GbrImageFile(f)

    invalid_file = "Tests/images/flower.jpg"
    with pytest.raises(SyntaxError, match="Unsupported GIMP brush version"):
        GbrImagePlugin.GbrImageFile(invalid_file)


def test_unsupported_gimp_brush() -> None:
    f = create_gbr_image({"color_depth": 2})
    with pytest.raises(SyntaxError, match="Unsupported GIMP brush color depth: 2"):
        GbrImagePlugin.GbrImageFile(f)


def test_bad_magic_number() -> None:
    f = create_gbr_image({"version": 2}, magic_number=b"badm")
    with pytest.raises(SyntaxError, match="not a GIMP brush, bad magic number"):
        GbrImagePlugin.GbrImageFile(f)


def test_L() -> None:
    f = create_gbr_image()
    with Image.open(f) as im:
        assert im.mode == "L"
