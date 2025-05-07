from __future__ import annotations

from types import ModuleType

import pytest

from PIL import Image, JpegXlImagePlugin

from .helper import skip_unless_feature

pytestmark = [skip_unless_feature("jpegxl")]

ElementTree: ModuleType | None
try:
    from defusedxml import ElementTree
except ImportError:
    ElementTree = None


# cjxl flower.jpg flower.jxl --lossless_jpeg=0 -q 75 -e 8

# >>> from PIL import Image
# >>> with Image.open('Tests/images/flower2.webp') as im:
# >>>   with open('/tmp/xmp.xml', 'wb') as f:
# >>>     f.write(im.info['xmp'])
# cjxl flower2.jpg flower2.jxl --lossless_jpeg=0 -q 75 -e 8 -x xmp=/tmp/xmp.xml


def test_read_exif_metadata() -> None:
    with Image.open("Tests/images/flower.jxl") as image:
        assert image.format == "JPEG XL"
        exif_data = image.info.get("exif", None)
        assert exif_data

        exif = image.getexif()

        # Camera make
        assert exif[271] == "Canon"

        with Image.open("Tests/images/flower.jpg") as jpeg_image:
            expected_exif = jpeg_image.info["exif"]

        # jpeg xl always returns exif without 'Exif\0\0' prefix
        assert exif_data == expected_exif[6:]


def test_read_exif_metadata_without_prefix() -> None:
    with Image.open("Tests/images/flower2.jxl") as im:
        # Assert prefix is not present
        assert im.info["exif"][:6] != b"Exif\x00\x00"

        exif = im.getexif()
    assert exif[305] == "Adobe Photoshop CS6 (Macintosh)"


def test_read_icc_profile() -> None:
    with Image.open("Tests/images/flower2.jxl") as image:
        assert image.format == "JPEG XL"
        assert image.info.get("icc_profile", None)

        icc = image.info["icc_profile"]

    with Image.open("Tests/images/flower2.jxl") as jpeg_image:
        expected_icc = jpeg_image.info["icc_profile"]

    assert icc == expected_icc


def test_getxmp() -> None:
    with Image.open("Tests/images/flower.jxl") as im:
        assert "xmp" not in im.info
        if ElementTree is None:
            with pytest.warns(
                UserWarning,
                match="XMP data cannot be read without defusedxml dependency",
            ):
                xmp = im.getxmp()
        else:
            xmp = im.getxmp()
        assert xmp == {}

    with Image.open("Tests/images/flower2.jxl") as im:
        if ElementTree is None:
            with pytest.warns(
                UserWarning,
                match="XMP data cannot be read without defusedxml dependency",
            ):
                assert im.getxmp() == {}
        else:
            assert "xmp" in im.info
            assert (
                im.getxmp()["xmpmeta"]["xmptk"]
                == "Adobe XMP Core 5.3-c011 66.145661, 2012/02/06-14:56:27        "
            )


def test_4_byte_exif(monkeypatch: pytest.MonkeyPatch) -> None:
    class _mock_jpegxl:
        class PILJpegXlDecoder:
            def __init__(self, b: bytes) -> None:
                pass

            def get_info(self) -> tuple[int, int, str, int, int, int, int, int]:
                return (1, 1, "L", 0, 0, 0, 0, 0)

            def get_icc(self) -> None:
                pass

            def get_exif(self) -> bytes:
                return b"\0\0\0\0"

            def get_xmp(self) -> None:
                pass

    monkeypatch.setattr(JpegXlImagePlugin, "_jpegxl", _mock_jpegxl)

    with Image.open("Tests/images/hopper.jxl") as image:
        assert "exif" not in image.info


def test_read_exif_metadata_empty() -> None:
    with Image.open("Tests/images/hopper.jxl") as image:
        assert image.getexif() == {}
