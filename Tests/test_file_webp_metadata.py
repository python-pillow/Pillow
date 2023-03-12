from io import BytesIO

import pytest

from PIL import Image

from .helper import mark_if_feature_version, skip_unless_feature

pytestmark = [
    skip_unless_feature("webp"),
    skip_unless_feature("webp_mux"),
]

try:
    from defusedxml import ElementTree
except ImportError:
    ElementTree = None


def test_read_exif_metadata():
    file_path = "Tests/images/flower.webp"
    with Image.open(file_path) as image:
        assert image.format == "WEBP"
        exif_data = image.info.get("exif", None)
        assert exif_data

        exif = image._getexif()

        # Camera make
        assert exif[271] == "Canon"

        with Image.open("Tests/images/flower.jpg") as jpeg_image:
            expected_exif = jpeg_image.info["exif"]

            assert exif_data == expected_exif


def test_read_exif_metadata_without_prefix():
    with Image.open("Tests/images/flower2.webp") as im:
        # Assert prefix is not present
        assert im.info["exif"][:6] != b"Exif\x00\x00"

        exif = im.getexif()
        assert exif[305] == "Adobe Photoshop CS6 (Macintosh)"


@mark_if_feature_version(
    pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
)
def test_write_exif_metadata():
    file_path = "Tests/images/flower.jpg"
    test_buffer = BytesIO()
    with Image.open(file_path) as image:
        expected_exif = image.info["exif"]

        image.save(test_buffer, "webp", exif=expected_exif)

    test_buffer.seek(0)
    with Image.open(test_buffer) as webp_image:
        webp_exif = webp_image.info.get("exif", None)
    assert webp_exif == expected_exif[6:], "WebP EXIF didn't match"


def test_read_icc_profile():
    file_path = "Tests/images/flower2.webp"
    with Image.open(file_path) as image:
        assert image.format == "WEBP"
        assert image.info.get("icc_profile", None)

        icc = image.info["icc_profile"]

        with Image.open("Tests/images/flower2.jpg") as jpeg_image:
            expected_icc = jpeg_image.info["icc_profile"]

            assert icc == expected_icc


@mark_if_feature_version(
    pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
)
def test_write_icc_metadata():
    file_path = "Tests/images/flower2.jpg"
    test_buffer = BytesIO()
    with Image.open(file_path) as image:
        expected_icc_profile = image.info["icc_profile"]

        image.save(test_buffer, "webp", icc_profile=expected_icc_profile)

    test_buffer.seek(0)
    with Image.open(test_buffer) as webp_image:
        webp_icc_profile = webp_image.info.get("icc_profile", None)

    assert webp_icc_profile
    if webp_icc_profile:
        assert webp_icc_profile == expected_icc_profile, "Webp ICC didn't match"


@mark_if_feature_version(
    pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
)
def test_read_no_exif():
    file_path = "Tests/images/flower.jpg"
    test_buffer = BytesIO()
    with Image.open(file_path) as image:
        assert "exif" in image.info

        image.save(test_buffer, "webp")

    test_buffer.seek(0)
    with Image.open(test_buffer) as webp_image:
        assert not webp_image._getexif()


def test_getxmp():
    with Image.open("Tests/images/flower.webp") as im:
        assert "xmp" not in im.info
        assert im.getxmp() == {}

    with Image.open("Tests/images/flower2.webp") as im:
        if ElementTree is None:
            with pytest.warns(UserWarning):
                assert im.getxmp() == {}
        else:
            assert (
                im.getxmp()["xmpmeta"]["xmptk"]
                == "Adobe XMP Core 5.3-c011 66.145661, 2012/02/06-14:56:27        "
            )


@skip_unless_feature("webp_anim")
def test_write_animated_metadata(tmp_path):
    iccp_data = b"<iccp_data>"
    exif_data = b"<exif_data>"
    xmp_data = b"<xmp_data>"

    temp_file = str(tmp_path / "temp.webp")
    with Image.open("Tests/images/anim_frame1.webp") as frame1:
        with Image.open("Tests/images/anim_frame2.webp") as frame2:
            frame1.save(
                temp_file,
                save_all=True,
                append_images=[frame2, frame1, frame2],
                icc_profile=iccp_data,
                exif=exif_data,
                xmp=xmp_data,
            )

    with Image.open(temp_file) as image:
        assert "icc_profile" in image.info
        assert "exif" in image.info
        assert "xmp" in image.info
        assert iccp_data == image.info.get("icc_profile", None)
        assert exif_data == image.info.get("exif", None)
        assert xmp_data == image.info.get("xmp", None)
