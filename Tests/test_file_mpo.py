from io import BytesIO

import pytest

from PIL import Image

from .helper import assert_image_similar, is_pypy, skip_unless_feature

test_files = ["Tests/images/sugarshack.mpo", "Tests/images/frozenpond.mpo"]

pytestmark = skip_unless_feature("jpg")


def frame_roundtrip(im, **options):
    # Note that for now, there is no MPO saving functionality
    out = BytesIO()
    im.save(out, "MPO", **options)
    test_bytes = out.tell()
    out.seek(0)
    im = Image.open(out)
    im.bytes = test_bytes  # for testing only
    return im


def test_sanity():
    for test_file in test_files:
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

    pytest.warns(ResourceWarning, open)


def test_closed_file():
    with pytest.warns(None) as record:
        im = Image.open(test_files[0])
        im.load()
        im.close()

    assert not record


def test_context_manager():
    with pytest.warns(None) as record:
        with Image.open(test_files[0]) as im:
            im.load()

    assert not record


def test_app():
    for test_file in test_files:
        # Test APP/COM reader (@PIL135)
        with Image.open(test_file) as im:
            assert im.applist[0][0] == "APP1"
            assert im.applist[1][0] == "APP2"
            assert (
                im.applist[1][1][:16]
                == b"MPF\x00MM\x00*\x00\x00\x00\x08\x00\x03\xb0\x00"
            )
            assert len(im.applist) == 2


def test_exif():
    for test_file in test_files:
        with Image.open(test_file) as im:
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


def test_mp():
    for test_file in test_files:
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


def test_mp_attribute():
    for test_file in test_files:
        with Image.open(test_file) as im:
            mpinfo = im._getmp()
        frameNumber = 0
        for mpentry in mpinfo[0xB002]:
            mpattr = mpentry["Attribute"]
            if frameNumber:
                assert not mpattr["RepresentativeImageFlag"]
            else:
                assert mpattr["RepresentativeImageFlag"]
            assert not mpattr["DependentParentImageFlag"]
            assert not mpattr["DependentChildImageFlag"]
            assert mpattr["ImageDataFormat"] == "JPEG"
            assert mpattr["MPType"] == "Multi-Frame Image: (Disparity)"
            assert mpattr["Reserved"] == 0
            frameNumber += 1


def test_seek():
    for test_file in test_files:
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


def test_image_grab():
    for test_file in test_files:
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


def test_save():
    # Note that only individual frames can be saved at present
    for test_file in test_files:
        with Image.open(test_file) as im:
            assert im.tell() == 0
            jpg0 = frame_roundtrip(im)
            assert_image_similar(im, jpg0, 30)
            im.seek(1)
            assert im.tell() == 1
            jpg1 = frame_roundtrip(im)
            assert_image_similar(im, jpg1, 30)
