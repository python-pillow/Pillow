import warnings
from io import BytesIO

import pytest

from PIL import Image

from .helper import (
    assert_image_equal,
    assert_image_similar,
    is_pypy,
    skip_unless_feature,
)

test_files = ["Tests/images/sugarshack.mpo", "Tests/images/frozenpond.mpo"]

pytestmark = skip_unless_feature("jpg")


def roundtrip(im, **options):
    out = BytesIO()
    im.save(out, "MPO", **options)
    test_bytes = out.tell()
    out.seek(0)
    im = Image.open(out)
    im.bytes = test_bytes  # for testing only
    return im


@pytest.mark.parametrize("test_file", test_files)
def test_sanity(test_file):
    with Image.open(test_file) as im:
        im.load()
        assert im.mode == "RGB"
        assert im.size == (640, 480)
        assert im.format == "MPO"


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file():
    def open():
        im = Image.open(test_files[0])
        im.load()

    with pytest.warns(ResourceWarning):
        open()


def test_closed_file():
    with warnings.catch_warnings():
        im = Image.open(test_files[0])
        im.load()
        im.close()


def test_seek_after_close():
    im = Image.open(test_files[0])
    im.close()

    with pytest.raises(ValueError):
        im.seek(1)


def test_context_manager():
    with warnings.catch_warnings():
        with Image.open(test_files[0]) as im:
            im.load()


@pytest.mark.parametrize("test_file", test_files)
def test_app(test_file):
    # Test APP/COM reader (@PIL135)
    with Image.open(test_file) as im:
        assert im.applist[0][0] == "APP1"
        assert im.applist[1][0] == "APP2"
        assert (
            im.applist[1][1][:16] == b"MPF\x00MM\x00*\x00\x00\x00\x08\x00\x03\xb0\x00"
        )
        assert len(im.applist) == 2


@pytest.mark.parametrize("test_file", test_files)
def test_exif(test_file):
    with Image.open(test_file) as im_original:
        im_reloaded = roundtrip(im_original, save_all=True, exif=im_original.getexif())

    for im in (im_original, im_reloaded):
        info = im._getexif()
        assert info[272] == "Nintendo 3DS"
        assert info[296] == 2
        assert info[34665] == 188


def test_frame_size():
    # This image has been hexedited to contain a different size
    # in the EXIF data of the second frame
    with Image.open("Tests/images/sugarshack_frame_size.mpo") as im:
        assert im.size == (640, 480)

        im.seek(1)
        assert im.size == (680, 480)

        im.seek(0)
        assert im.size == (640, 480)


def test_ignore_frame_size():
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


def test_parallax():
    # Nintendo
    with Image.open("Tests/images/sugarshack.mpo") as im:
        exif = im.getexif()
        assert exif.get_ifd(0x927C)[0x1101]["Parallax"] == -44.798187255859375

    # Fujifilm
    with Image.open("Tests/images/fujifilm.mpo") as im:
        im.seek(1)
        exif = im.getexif()
        assert exif.get_ifd(0x927C)[0xB211] == -3.125


def test_reload_exif_after_seek():
    with Image.open("Tests/images/sugarshack.mpo") as im:
        exif = im.getexif()
        del exif[296]

        im.seek(1)
        assert 296 in exif


@pytest.mark.parametrize("test_file", test_files)
def test_mp(test_file):
    with Image.open(test_file) as im:
        mpinfo = im._getmp()
        assert mpinfo[45056] == b"0100"
        assert mpinfo[45057] == 2


def test_mp_offset():
    # This image has been manually hexedited to have an IFD offset of 10
    # in APP2 data, in contrast to normal 8
    with Image.open("Tests/images/sugarshack_ifd_offset.mpo") as im:
        mpinfo = im._getmp()
        assert mpinfo[45056] == b"0100"
        assert mpinfo[45057] == 2


def test_mp_no_data():
    # This image has been manually hexedited to have the second frame
    # beyond the end of the file
    with Image.open("Tests/images/sugarshack_no_data.mpo") as im:
        with pytest.raises(ValueError):
            im.seek(1)


@pytest.mark.parametrize("test_file", test_files)
def test_mp_attribute(test_file):
    with Image.open(test_file) as im:
        mpinfo = im._getmp()
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
def test_seek(test_file):
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


def test_n_frames():
    with Image.open("Tests/images/sugarshack.mpo") as im:
        assert im.n_frames == 2
        assert im.is_animated


def test_eoferror():
    with Image.open("Tests/images/sugarshack.mpo") as im:
        n_frames = im.n_frames

        # Test seeking past the last frame
        with pytest.raises(EOFError):
            im.seek(n_frames)
        assert im.tell() < n_frames

        # Test that seeking to the last frame does not raise an error
        im.seek(n_frames - 1)


@pytest.mark.parametrize("test_file", test_files)
def test_image_grab(test_file):
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
def test_save(test_file):
    with Image.open(test_file) as im:
        assert im.tell() == 0
        jpg0 = roundtrip(im)
        assert_image_similar(im, jpg0, 30)
        im.seek(1)
        assert im.tell() == 1
        jpg1 = roundtrip(im)
        assert_image_similar(im, jpg1, 30)


def test_save_all():
    for test_file in test_files:
        with Image.open(test_file) as im:
            im_reloaded = roundtrip(im, save_all=True)

            im.seek(0)
            assert_image_similar(im, im_reloaded, 30)

            im.seek(1)
            im_reloaded.seek(1)
            assert_image_similar(im, im_reloaded, 30)

    im = Image.new("RGB", (1, 1))
    im2 = Image.new("RGB", (1, 1), "#f00")
    im_reloaded = roundtrip(im, save_all=True, append_images=[im2])

    assert_image_equal(im, im_reloaded)
    assert im_reloaded.mpinfo[45056] == b"0100"

    im_reloaded.seek(1)
    assert_image_similar(im2, im_reloaded, 1)

    # Test that a single frame image will not be saved as an MPO
    jpg = roundtrip(im, save_all=True)
    assert "mp" not in jpg.info
