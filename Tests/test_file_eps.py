import io

import pytest

from PIL import EpsImagePlugin, Image, features

from .helper import (
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
    mark_if_feature_version,
    skip_unless_feature,
)

HAS_GHOSTSCRIPT = EpsImagePlugin.has_ghostscript()

# Our two EPS test files (they are identical except for their bounding boxes)
FILE1 = "Tests/images/zero_bb.eps"
FILE2 = "Tests/images/non_zero_bb.eps"

# Due to palletization, we'll need to convert these to RGB after load
FILE1_COMPARE = "Tests/images/zero_bb.png"
FILE1_COMPARE_SCALE2 = "Tests/images/zero_bb_scale2.png"

FILE2_COMPARE = "Tests/images/non_zero_bb.png"
FILE2_COMPARE_SCALE2 = "Tests/images/non_zero_bb_scale2.png"

# EPS test files with binary preview
FILE3 = "Tests/images/binary_preview_map.eps"


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_sanity():
    # Regular scale
    with Image.open(FILE1) as image1:
        image1.load()
        assert image1.mode == "RGB"
        assert image1.size == (460, 352)
        assert image1.format == "EPS"

    with Image.open(FILE2) as image2:
        image2.load()
        assert image2.mode == "RGB"
        assert image2.size == (360, 252)
        assert image2.format == "EPS"

    # Double scale
    with Image.open(FILE1) as image1_scale2:
        image1_scale2.load(scale=2)
        assert image1_scale2.mode == "RGB"
        assert image1_scale2.size == (920, 704)
        assert image1_scale2.format == "EPS"

    with Image.open(FILE2) as image2_scale2:
        image2_scale2.load(scale=2)
        assert image2_scale2.mode == "RGB"
        assert image2_scale2.size == (720, 504)
        assert image2_scale2.format == "EPS"


def test_invalid_file():
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        EpsImagePlugin.EpsImageFile(invalid_file)


@mark_if_feature_version(
    pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
)
@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_cmyk():
    with Image.open("Tests/images/pil_sample_cmyk.eps") as cmyk_image:

        assert cmyk_image.mode == "CMYK"
        assert cmyk_image.size == (100, 100)
        assert cmyk_image.format == "EPS"

        cmyk_image.load()
        assert cmyk_image.mode == "RGB"

        if features.check("jpg"):
            assert_image_similar_tofile(
                cmyk_image, "Tests/images/pil_sample_rgb.jpg", 10
            )


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_showpage():
    # See https://github.com/python-pillow/Pillow/issues/2615
    with Image.open("Tests/images/reqd_showpage.eps") as plot_image:
        with Image.open("Tests/images/reqd_showpage.png") as target:
            # should not crash/hang
            plot_image.load()
            #  fonts could be slightly different
            assert_image_similar(plot_image, target, 6)


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_transparency():
    with Image.open("Tests/images/reqd_showpage.eps") as plot_image:
        plot_image.load(transparency=True)
        assert plot_image.mode == "RGBA"

        with Image.open("Tests/images/reqd_showpage_transparency.png") as target:
            #  fonts could be slightly different
            assert_image_similar(plot_image, target, 6)


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_file_object(tmp_path):
    # issue 479
    with Image.open(FILE1) as image1:
        with open(str(tmp_path / "temp.eps"), "wb") as fh:
            image1.save(fh, "EPS")


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_iobase_object(tmp_path):
    # issue 479
    with Image.open(FILE1) as image1:
        with open(str(tmp_path / "temp_iobase.eps"), "wb") as fh:
            image1.save(fh, "EPS")


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_bytesio_object():
    with open(FILE1, "rb") as f:
        img_bytes = io.BytesIO(f.read())

    with Image.open(img_bytes) as img:
        img.load()

        with Image.open(FILE1_COMPARE) as image1_scale1_compare:
            image1_scale1_compare = image1_scale1_compare.convert("RGB")
        image1_scale1_compare.load()
        assert_image_similar(img, image1_scale1_compare, 5)


def test_image_mode_not_supported(tmp_path):
    im = hopper("RGBA")
    tmpfile = str(tmp_path / "temp.eps")
    with pytest.raises(ValueError):
        im.save(tmpfile)


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
@skip_unless_feature("zlib")
def test_render_scale1():
    # We need png support for these render test

    # Zero bounding box
    with Image.open(FILE1) as image1_scale1:
        image1_scale1.load()
        with Image.open(FILE1_COMPARE) as image1_scale1_compare:
            image1_scale1_compare = image1_scale1_compare.convert("RGB")
        image1_scale1_compare.load()
        assert_image_similar(image1_scale1, image1_scale1_compare, 5)

    # Non-Zero bounding box
    with Image.open(FILE2) as image2_scale1:
        image2_scale1.load()
        with Image.open(FILE2_COMPARE) as image2_scale1_compare:
            image2_scale1_compare = image2_scale1_compare.convert("RGB")
        image2_scale1_compare.load()
        assert_image_similar(image2_scale1, image2_scale1_compare, 10)


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
@skip_unless_feature("zlib")
def test_render_scale2():
    # We need png support for these render test

    # Zero bounding box
    with Image.open(FILE1) as image1_scale2:
        image1_scale2.load(scale=2)
        with Image.open(FILE1_COMPARE_SCALE2) as image1_scale2_compare:
            image1_scale2_compare = image1_scale2_compare.convert("RGB")
        image1_scale2_compare.load()
        assert_image_similar(image1_scale2, image1_scale2_compare, 5)

    # Non-Zero bounding box
    with Image.open(FILE2) as image2_scale2:
        image2_scale2.load(scale=2)
        with Image.open(FILE2_COMPARE_SCALE2) as image2_scale2_compare:
            image2_scale2_compare = image2_scale2_compare.convert("RGB")
        image2_scale2_compare.load()
        assert_image_similar(image2_scale2, image2_scale2_compare, 10)


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_resize():
    files = [FILE1, FILE2, "Tests/images/illu10_preview.eps"]
    for fn in files:
        with Image.open(fn) as im:
            new_size = (100, 100)
            im = im.resize(new_size)
            assert im.size == new_size


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_thumbnail():
    # Issue #619
    # Arrange
    files = [FILE1, FILE2]
    for fn in files:
        with Image.open(FILE1) as im:
            new_size = (100, 100)
            im.thumbnail(new_size)
            assert max(im.size) == max(new_size)


def test_read_binary_preview():
    # Issue 302
    # open image with binary preview
    with Image.open(FILE3):
        pass


def test_readline(tmp_path):
    # check all the freaking line endings possible from the spec
    # test_string = u'something\r\nelse\n\rbaz\rbif\n'
    line_endings = ["\r\n", "\n", "\n\r", "\r"]
    strings = ["something", "else", "baz", "bif"]

    def _test_readline(t, ending):
        ending = "Failure with line ending: %s" % (
            "".join("%s" % ord(s) for s in ending)
        )
        assert t.readline().strip("\r\n") == "something", ending
        assert t.readline().strip("\r\n") == "else", ending
        assert t.readline().strip("\r\n") == "baz", ending
        assert t.readline().strip("\r\n") == "bif", ending

    def _test_readline_io_psfile(test_string, ending):
        f = io.BytesIO(test_string.encode("latin-1"))
        t = EpsImagePlugin.PSFile(f)
        _test_readline(t, ending)

    def _test_readline_file_psfile(test_string, ending):
        f = str(tmp_path / "temp.txt")
        with open(f, "wb") as w:
            w.write(test_string.encode("latin-1"))

        with open(f, "rb") as r:
            t = EpsImagePlugin.PSFile(r)
            _test_readline(t, ending)

    for ending in line_endings:
        s = ending.join(strings)
        _test_readline_io_psfile(s, ending)
        _test_readline_file_psfile(s, ending)


def test_open_eps():
    # https://github.com/python-pillow/Pillow/issues/1104
    # Arrange
    FILES = [
        "Tests/images/illu10_no_preview.eps",
        "Tests/images/illu10_preview.eps",
        "Tests/images/illuCS6_no_preview.eps",
        "Tests/images/illuCS6_preview.eps",
    ]

    # Act / Assert
    for filename in FILES:
        with Image.open(filename) as img:
            assert img.mode == "RGB"


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_emptyline():
    # Test file includes an empty line in the header data
    emptyline_file = "Tests/images/zero_bb_emptyline.eps"

    with Image.open(emptyline_file) as image:
        image.load()
    assert image.mode == "RGB"
    assert image.size == (460, 352)
    assert image.format == "EPS"


@pytest.mark.timeout(timeout=5)
@pytest.mark.parametrize(
    "test_file",
    ["Tests/images/timeout-d675703545fee17acab56e5fec644c19979175de.eps"],
)
def test_timeout(test_file):
    with open(test_file, "rb") as f:
        with pytest.raises(Image.UnidentifiedImageError):
            with Image.open(f):
                pass
