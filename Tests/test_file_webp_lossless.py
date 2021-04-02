import pytest

from PIL import Image

from .helper import assert_image_equal, hopper

_webp = pytest.importorskip("PIL._webp", reason="WebP support not installed")
RGB_MODE = "RGB"


def test_write_lossless_rgb(tmp_path):
    if _webp.WebPDecoderVersion() < 0x0200:
        pytest.skip("lossless not included")

    temp_file = str(tmp_path / "temp.webp")

    hopper(RGB_MODE).save(temp_file, lossless=True)

    with Image.open(temp_file) as image:
        image.load()

        assert image.mode == RGB_MODE
        assert image.size == (128, 128)
        assert image.format == "WEBP"
        image.load()
        image.getdata()

        assert_image_equal(image, hopper(RGB_MODE))
