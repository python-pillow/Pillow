import pytest

from PIL import Image

from .helper import (
    assert_image_equal,
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
)

_webp = pytest.importorskip("PIL._webp", reason="WebP support not installed")


def setup_module():
    if _webp.WebPDecoderBuggyAlpha():
        pytest.skip("Buggy early version of WebP installed, not testing transparency")


def test_read_rgba():
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


def test_write_lossless_rgb(tmp_path):
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


def test_write_rgba(tmp_path):
    """
    Can we write a RGBA mode file to WebP without error.
    Does it have the bits we expect?
    """

    temp_file = str(tmp_path / "temp.webp")

    pil_image = Image.new("RGBA", (10, 10), (255, 0, 0, 20))
    pil_image.save(temp_file)

    if _webp.WebPDecoderBuggyAlpha():
        return

    with Image.open(temp_file) as image:
        image.load()

        assert image.mode == "RGBA"
        assert image.size == (10, 10)
        assert image.format == "WEBP"
        image.load()
        image.getdata()

        # Early versions of WebP are known to produce higher deviations:
        # deal with it
        if _webp.WebPDecoderVersion() <= 0x201:
            assert_image_similar(image, pil_image, 3.0)
        else:
            assert_image_similar(image, pil_image, 1.0)

def test_write_rgba_keep_transparent(tmp_path):
    """
    Can we write a RGBA mode file to WebP while preserving
    the transparent RGB without error.
    Does it have the bits we expect?
    """

    temp_output_file = str(tmp_path / "temp.webp")

    input_image = hopper("RGB")
    # make a copy of the image
    output_image = input_image.copy()
    # make a single channel image with the same size as input_image
    new_alpha = Image.new("L", input_image.size, 255)
    # make the left half transparent
    new_alpha.paste((0,), (0, 0, new_alpha.size[0]//2, new_alpha.size[1]))
    # putalpha on output_image
    output_image.putalpha(new_alpha)

    # now save with transparent area preserved.
    output_image.save(temp_output_file, "WEBP", exact=True, lossless=True)
    # even though it is lossless, if we don't put exact=True, the transparent
    # area will be filled with black (or something more conducive to compression)

    with Image.open(temp_output_file) as image:
        image.load()

        assert image.mode == "RGBA"
        assert image.format == "WEBP"
        image.load()
        image = image.convert("RGB")
        assert_image_similar(image, input_image, 1.0)



def test_write_unsupported_mode_PA(tmp_path):
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
