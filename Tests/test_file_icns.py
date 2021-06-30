import io

import pytest

from PIL import IcnsImagePlugin, Image, features

from .helper import assert_image_equal, assert_image_similar_tofile

# sample icon file
TEST_FILE = "Tests/images/pillow.icns"

ENABLE_JPEG2K = features.check_codec("jpg_2000")


def test_sanity():
    # Loading this icon by default should result in the largest size
    # (512x512@2x) being loaded
    with Image.open(TEST_FILE) as im:

        # Assert that there is no unclosed file warning
        with pytest.warns(None) as record:
            im.load()
        assert not record

        assert im.mode == "RGBA"
        assert im.size == (1024, 1024)
        assert im.format == "ICNS"


def test_save(tmp_path):
    temp_file = str(tmp_path / "temp.icns")

    with Image.open(TEST_FILE) as im:
        im.save(temp_file)

    with Image.open(temp_file) as reread:
        assert reread.mode == "RGBA"
        assert reread.size == (1024, 1024)
        assert reread.format == "ICNS"


def test_save_append_images(tmp_path):
    temp_file = str(tmp_path / "temp.icns")
    provided_im = Image.new("RGBA", (32, 32), (255, 0, 0, 128))

    with Image.open(TEST_FILE) as im:
        im.save(temp_file, append_images=[provided_im])

        assert_image_similar_tofile(im, temp_file, 1)

        with Image.open(temp_file) as reread:
            reread.size = (16, 16, 2)
            reread.load()
            assert_image_equal(reread, provided_im)


def test_save_fp():
    fp = io.BytesIO()

    with Image.open(TEST_FILE) as im:
        im.save(fp, format="ICNS")

    with Image.open(fp) as reread:
        assert reread.mode == "RGBA"
        assert reread.size == (1024, 1024)
        assert reread.format == "ICNS"


def test_sizes():
    # Check that we can load all of the sizes, and that the final pixel
    # dimensions are as expected
    with Image.open(TEST_FILE) as im:
        for w, h, r in im.info["sizes"]:
            wr = w * r
            hr = h * r
            im.size = (w, h, r)
            im.load()
            assert im.mode == "RGBA"
            assert im.size == (wr, hr)

        # Check that we cannot load an incorrect size
        with pytest.raises(ValueError):
            im.size = (1, 1)


def test_older_icon():
    # This icon was made with Icon Composer rather than iconutil; it still
    # uses PNG rather than JP2, however (since it was made on 10.9).
    with Image.open("Tests/images/pillow2.icns") as im:
        for w, h, r in im.info["sizes"]:
            wr = w * r
            hr = h * r
            with Image.open("Tests/images/pillow2.icns") as im2:
                im2.size = (w, h, r)
                im2.load()
                assert im2.mode == "RGBA"
                assert im2.size == (wr, hr)


def test_jp2_icon():
    # This icon was made by using Uli Kusterer's oldiconutil to replace
    # the PNG images with JPEG 2000 ones.  The advantage of doing this is
    # that OS X 10.5 supports JPEG 2000 but not PNG; some commercial
    # software therefore does just this.

    # (oldiconutil is here: https://github.com/uliwitness/oldiconutil)

    if not ENABLE_JPEG2K:
        return

    with Image.open("Tests/images/pillow3.icns") as im:
        for w, h, r in im.info["sizes"]:
            wr = w * r
            hr = h * r
            with Image.open("Tests/images/pillow3.icns") as im2:
                im2.size = (w, h, r)
                im2.load()
                assert im2.mode == "RGBA"
                assert im2.size == (wr, hr)


def test_getimage():
    with open(TEST_FILE, "rb") as fp:
        icns_file = IcnsImagePlugin.IcnsFile(fp)

        im = icns_file.getimage()
        assert im.mode == "RGBA"
        assert im.size == (1024, 1024)

        im = icns_file.getimage((512, 512))
        assert im.mode == "RGBA"
        assert im.size == (512, 512)


def test_not_an_icns_file():
    with io.BytesIO(b"invalid\n") as fp:
        with pytest.raises(SyntaxError):
            IcnsImagePlugin.IcnsFile(fp)


def test_icns_decompression_bomb():
    with Image.open(
        "Tests/images/oom-8ed3316a4109213ca96fb8a256a0bfefdece1461.icns"
    ) as im:
        with pytest.raises(Image.DecompressionBombError):
            im.load()
