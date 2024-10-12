from __future__ import annotations

from pathlib import Path

import pytest

from PIL import Image

from .helper import (
    assert_image_equal,
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
)

pytest.importorskip("PIL._webp", reason="WebP support not installed")


def test_read_rgba() -> None:
    """
    Can we read an RGBA mode file without error?
    Does it have the bits we expect?
    """

    # Generated with `cwebp transparent.png -o transparent.webp`
    file_path = "Tests/images/transparent.webp"
    with Image.open(file_path) as image:
        assert image.mode == "RGBA"
        assert image.size == (200, 150)
        assert image.format == "WEBP"
        image.load()
        image.getdata()

        image.tobytes()

        assert_image_similar_tofile(image, "Tests/images/transparent.png", 20.0)


def test_write_lossless_rgb(tmp_path: Path) -> None:
    """
    Can we write an RGBA mode file with lossless compression without error?
    Does it have the bits we expect?
    """

    temp_file = str(tmp_path / "temp.webp")
    # temp_file = "temp.webp"

    pil_image = hopper("RGBA")

    mask = Image.new("RGBA", (64, 64), (128, 128, 128, 128))
    # Add some partially transparent bits:
    pil_image.paste(mask, (0, 0), mask)

    pil_image.save(temp_file, lossless=True)

    with Image.open(temp_file) as image:
        image.load()

        assert image.mode == "RGBA"
        assert image.size == pil_image.size
        assert image.format == "WEBP"
        image.load()
        image.getdata()

        assert_image_equal(image, pil_image)


def test_write_rgba(tmp_path: Path) -> None:
    """
    Can we write a RGBA mode file to WebP without error.
    Does it have the bits we expect?
    """

    temp_file = str(tmp_path / "temp.webp")

    pil_image = Image.new("RGBA", (10, 10), (255, 0, 0, 20))
    pil_image.save(temp_file)

    with Image.open(temp_file) as image:
        image.load()

        assert image.mode == "RGBA"
        assert image.size == (10, 10)
        assert image.format == "WEBP"
        image.load()
        image.getdata()

        assert_image_similar(image, pil_image, 1.0)


def test_keep_rgb_values_when_transparent(tmp_path: Path) -> None:
    """
    Saving transparent pixels should retain their original RGB values
    when using the "exact" parameter.
    """

    image = hopper("RGB")

    # create a copy of the image
    # with the left half transparent
    half_transparent_image = image.copy()
    new_alpha = Image.new("L", (128, 128), 255)
    new_alpha.paste(0, (0, 0, 64, 128))
    half_transparent_image.putalpha(new_alpha)

    # save with transparent area preserved
    temp_file = str(tmp_path / "temp.webp")
    half_transparent_image.save(temp_file, exact=True, lossless=True)

    with Image.open(temp_file) as reloaded:
        assert reloaded.mode == "RGBA"
        assert reloaded.format == "WEBP"

        # even though it is lossless, if we don't use exact=True
        # in libwebp >= 0.5, the transparent area will be filled with black
        # (or something more conducive to compression)
        assert_image_equal(reloaded.convert("RGB"), image)


def test_write_unsupported_mode_PA(tmp_path: Path) -> None:
    """
    Saving a palette-based file with transparency to WebP format
    should work, and be similar to the original file.
    """

    temp_file = str(tmp_path / "temp.webp")
    file_path = "Tests/images/transparent.gif"
    with Image.open(file_path) as im:
        im.save(temp_file)
    with Image.open(temp_file) as image:
        assert image.mode == "RGBA"
        assert image.size == (200, 150)
        assert image.format == "WEBP"

        image.load()
        image.getdata()
        with Image.open(file_path) as im:
            target = im.convert("RGBA")

        assert_image_similar(image, target, 25.0)


def test_alpha_quality(tmp_path: Path) -> None:
    with Image.open("Tests/images/transparent.png") as im:
        out = str(tmp_path / "temp.webp")
        im.save(out)

        out_quality = str(tmp_path / "quality.webp")
        im.save(out_quality, alpha_quality=50)
        with Image.open(out) as reloaded:
            with Image.open(out_quality) as reloaded_quality:
                assert reloaded.tobytes() != reloaded_quality.tobytes()
