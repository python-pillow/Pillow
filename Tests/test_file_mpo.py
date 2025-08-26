from __future__ import annotations

import warnings
from io import BytesIO
from typing import Any

import pytest

from PIL import Image, ImageFile, JpegImagePlugin, MpoImagePlugin

from .helper import (
    assert_image_equal,
    assert_image_similar,
    is_pypy,
    skip_unless_feature,
)

test_files = ["Tests/images/sugarshack.mpo", "Tests/images/frozenpond.mpo"]

pytestmark = skip_unless_feature("jpg")


def roundtrip(im: Image.Image, **options: Any) -> ImageFile.ImageFile:
    out = BytesIO()
    im.save(out, "MPO", **options)
    out.seek(0)
    return Image.open(out)


@pytest.mark.parametrize("test_file", test_files)
def test_sanity(test_file: str) -> None:
    def check(im: ImageFile.ImageFile) -> None:
        im.load()
        assert im.mode == "RGB"
        assert im.size == (640, 480)
        assert im.format == "MPO"

    with Image.open(test_file) as im:
        check(im)
    with MpoImagePlugin.MpoImageFile(test_file) as im:
        check(im)


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file() -> None:
    def open_test_image() -> None:
        im = Image.open(test_files[0])
        im.load()

    with pytest.warns(ResourceWarning):
        open_test_image()


def test_closed_file() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        im = Image.open(test_files[0])
        im.load()
        im.close()


def test_seek_after_close() -> None:
    im = Image.open(test_files[0])
    im.close()

    with pytest.raises(ValueError):
        im.seek(1)


def test_context_manager() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        with Image.open(test_files[0]) as im:
            im.load()


@pytest.mark.parametrize("test_file", test_files)
def test_app(test_file: str) -> None:
    # Test APP/COM reader (@PIL135)
    with Image.open(test_file) as im:
        assert isinstance(im, MpoImagePlugin.MpoImageFile)
        assert im.applist[0][0] == "APP1"
        assert im.applist[1][0] == "APP2"
        assert im.applist[1][1].startswith(
            b"MPF\x00MM\x00*\x00\x00\x00\x08\x00\x03\xb0\x00"
        )
        assert len(im.applist) == 2


@pytest.mark.parametrize("test_file", test_files)
def test_exif(test_file: str) -> None:
    with Image.open(test_file) as im_original:
        im_reloaded = roundtrip(im_original, save_all=True, exif=im_original.getexif())

    for im in (im_original, im_reloaded):
        assert isinstance(im, MpoImagePlugin.MpoImageFile)
        info = im._getexif()
        assert info is not None
        assert info[272] == "Nintendo 3DS"
        assert info[296] == 2
        assert info[34665] == 188


def test_frame_size() -> None:
    # This image has been hexedited to contain a different size
    # in the SOF marker of the second frame
    with Image.open("Tests/images/sugarshack_frame_size.mpo") as im:
        assert im.size == (640, 480)

        im.seek(1)
        assert im.size == (680, 480)

        im.seek(0)
        assert im.size == (640, 480)


def test_ignore_frame_size() -> None:
    # Ignore the different size of the second frame
    # since this is not a "Large Thumbnail" image
    with Image.open("Tests/images/ignore_frame_size.mpo") as im:
        assert im.size == (64, 64)

        im.seek(1)
        assert (
            im.mpinfo[0xB002][1]["Attribute"]["MPType"]
            == "Multi-Frame Image: (Disparity)"
        )
        assert im.size == (64, 64)


def test_parallax() -> None:
    # Nintendo
    with Image.open("Tests/images/sugarshack.mpo") as im:
        exif = im.getexif()
        assert exif.get_ifd(0x927C)[0x1101]["Parallax"] == -44.798187255859375

    # Fujifilm
    with Image.open("Tests/images/fujifilm.mpo") as im:
        im.seek(1)
        exif = im.getexif()
        assert exif.get_ifd(0x927C)[0xB211] == -3.125


def test_reload_exif_after_seek() -> None:
    with Image.open("Tests/images/sugarshack.mpo") as im:
        exif = im.getexif()
        del exif[296]

        im.seek(1)
        assert 296 in exif


@pytest.mark.parametrize("test_file", test_files)
def test_mp(test_file: str) -> None:
    with Image.open(test_file) as im:
        mpinfo = im._getmp()
        assert mpinfo is not None
        assert mpinfo[45056] == b"0100"
        assert mpinfo[45057] == 2


def test_mp_offset() -> None:
    # This image has been manually hexedited to have an IFD offset of 10
    # in APP2 data, in contrast to normal 8
    with Image.open("Tests/images/sugarshack_ifd_offset.mpo") as im:
        mpinfo = im._getmp()
        assert mpinfo is not None
        assert mpinfo[45056] == b"0100"
        assert mpinfo[45057] == 2


def test_mp_no_data() -> None:
    # This image has been manually hexedited to have the second frame
    # beyond the end of the file
    with Image.open("Tests/images/sugarshack_no_data.mpo") as im:
        with pytest.raises(ValueError):
            im.seek(1)


@pytest.mark.parametrize("test_file", test_files)
def test_mp_attribute(test_file: str) -> None:
    with Image.open(test_file) as im:
        mpinfo = im._getmp()
    assert mpinfo is not None
    for frame_number, mpentry in enumerate(mpinfo[0xB002]):
        mpattr = mpentry["Attribute"]
        if frame_number:
            assert not mpattr["RepresentativeImageFlag"]
        else:
            assert mpattr["RepresentativeImageFlag"]
        assert not mpattr["DependentParentImageFlag"]
        assert not mpattr["DependentChildImageFlag"]
        assert mpattr["ImageDataFormat"] == "JPEG"
        assert mpattr["MPType"] == "Multi-Frame Image: (Disparity)"
        assert mpattr["Reserved"] == 0


@pytest.mark.parametrize("test_file", test_files)
def test_seek(test_file: str) -> None:
    with Image.open(test_file) as im:
        assert im.tell() == 0
        # prior to first image raises an error, both blatant and borderline
        with pytest.raises(EOFError):
            im.seek(-1)
        with pytest.raises(EOFError):
            im.seek(-523)
        # after the final image raises an error,
        # both blatant and borderline
        with pytest.raises(EOFError):
            im.seek(2)
        with pytest.raises(EOFError):
            im.seek(523)
        # bad calls shouldn't change the frame
        assert im.tell() == 0
        # this one will work
        im.seek(1)
        assert im.tell() == 1
        # and this one, too
        im.seek(0)
        assert im.tell() == 0


def test_n_frames() -> None:
    with Image.open("Tests/images/sugarshack.mpo") as im:
        assert isinstance(im, MpoImagePlugin.MpoImageFile)
        assert im.n_frames == 2
        assert im.is_animated


def test_eoferror() -> None:
    with Image.open("Tests/images/sugarshack.mpo") as im:
        assert isinstance(im, MpoImagePlugin.MpoImageFile)
        n_frames = im.n_frames

        # Test seeking past the last frame
        with pytest.raises(EOFError):
            im.seek(n_frames)
        assert im.tell() < n_frames

        # Test that seeking to the last frame does not raise an error
        im.seek(n_frames - 1)


def test_adopt_jpeg() -> None:
    with Image.open("Tests/images/hopper.jpg") as im:
        assert isinstance(im, JpegImagePlugin.JpegImageFile)

        with pytest.raises(ValueError):
            MpoImagePlugin.MpoImageFile.adopt(im)


def test_ultra_hdr() -> None:
    with Image.open("Tests/images/ultrahdr.jpg") as im:
        assert im.format == "JPEG"


@pytest.mark.parametrize("test_file", test_files)
def test_image_grab(test_file: str) -> None:
    with Image.open(test_file) as im:
        assert im.tell() == 0
        im0 = im.tobytes()
        im.seek(1)
        assert im.tell() == 1
        im1 = im.tobytes()
        im.seek(0)
        assert im.tell() == 0
        im02 = im.tobytes()
        assert im0 == im02
        assert im0 != im1


@pytest.mark.parametrize("test_file", test_files)
def test_save(test_file: str) -> None:
    with Image.open(test_file) as im:
        assert im.tell() == 0
        jpg0 = roundtrip(im)
        assert_image_similar(im, jpg0, 30)
        im.seek(1)
        assert im.tell() == 1
        jpg1 = roundtrip(im)
        assert_image_similar(im, jpg1, 30)


def test_save_all() -> None:
    for test_file in test_files:
        with Image.open(test_file) as im:
            im_reloaded = roundtrip(im, save_all=True)

            im.seek(0)
            assert_image_similar(im, im_reloaded, 30)

            im.seek(1)
            im_reloaded.seek(1)
            assert_image_similar(im, im_reloaded, 30)

    im = Image.new("RGB", (1, 1))
    for colors in (("#f00",), ("#f00", "#0f0")):
        append_images = [Image.new("RGB", (1, 1), color) for color in colors]
        im_reloaded = roundtrip(im, save_all=True, append_images=append_images)

        assert_image_equal(im, im_reloaded)
        assert isinstance(im_reloaded, MpoImagePlugin.MpoImageFile)
        assert im_reloaded.mpinfo is not None
        assert im_reloaded.mpinfo[45056] == b"0100"

        for im_expected in append_images:
            im_reloaded.seek(im_reloaded.tell() + 1)
            assert_image_similar(im_reloaded, im_expected, 1)

    # Test that a single frame image will not be saved as an MPO
    jpg = roundtrip(im, save_all=True)
    assert "mp" not in jpg.info


def test_save_xmp() -> None:
    im = Image.new("RGB", (1, 1))
    im2 = Image.new("RGB", (1, 1), "#f00")

    def roundtrip_xmp() -> list[Any]:
        im_reloaded = roundtrip(im, xmp=b"Default", save_all=True, append_images=[im2])
        xmp = [im_reloaded.info["xmp"]]
        im_reloaded.seek(1)
        return xmp + [im_reloaded.info["xmp"]]

    # Use the save parameters for all frames by default
    assert roundtrip_xmp() == [b"Default", b"Default"]

    # Specify a value for the first frame
    im.encoderinfo = {"xmp": b"First frame"}
    assert roundtrip_xmp() == [b"First frame", b"Default"]
    del im.encoderinfo

    # Specify value for the second frame
    im2.encoderinfo = {"xmp": b"Second frame"}
    assert roundtrip_xmp() == [b"Default", b"Second frame"]

    # Test that encoderinfo is unchanged
    assert im2.encoderinfo == {"xmp": b"Second frame"}
