from __future__ import annotations

from types import ModuleType

import pytest

from PIL import Image

from .helper import skip_unless_feature

pytestmark = [
    skip_unless_feature("jpegxl"),
]

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
    file_path = "Tests/images/flower.jxl"
    with Image.open(file_path) as image:
        assert image.format == "JPEG XL"
        exif_data = image.info.get("exif", None)
        assert exif_data

        exif = image._getexif()

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
    file_path = "Tests/images/flower2.jxl"
    with Image.open(file_path) as image:
        assert image.format == "JPEG XL"
        assert image.info.get("icc_profile", None)

        icc = image.info["icc_profile"]

        with Image.open("Tests/images/flower2.jxl") as jpeg_image:
            expected_icc = jpeg_image.info["icc_profile"]

            assert icc == expected_icc


def test_getxmp() -> None:
    with Image.open("Tests/images/flower.jxl") as im:
        assert "xmp" not in im.info
        assert im.getxmp() == {}

    with Image.open("Tests/images/flower2.jxl") as im:
        if ElementTree:
            assert (
                im.getxmp()["xmpmeta"]["xmptk"]
                == "Adobe XMP Core 5.3-c011 66.145661, 2012/02/06-14:56:27        "
            )
        else:
            with pytest.warns(
                UserWarning,
                match="XMP data cannot be read without defusedxml dependency",
            ):
                assert im.getxmp() == {}


def test_fix_exif_fail() -> None:
    with Image.open("Tests/images/flower2.jxl") as image:
        assert image._fix_exif(b"\0\0\0\0") is None


def test_read_exif_metadata_empty() -> None:
    with Image.open("Tests/images/hopper.jxl") as image:
        assert image._getexif() is None
