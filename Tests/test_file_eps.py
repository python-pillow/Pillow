from __future__ import annotations

import io
from pathlib import Path

import unittest
from unittest.mock import patch, MagicMock

import pytest

from PIL import EpsImagePlugin, Image, UnidentifiedImageError, features

from .helper import (
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
    is_win32,
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

# Three unsigned 32bit little-endian values:
#   0xC6D3D0C5 magic number
#   byte position of start of postscript section (12)
#   byte length of postscript section (0)
# this byte length isn't valid, but we don't read it
simple_binary_header = b"\xc5\xd0\xd3\xc6\x0c\x00\x00\x00\x00\x00\x00\x00"

# taken from page 8 of the specification
# https://web.archive.org/web/20220120164601/https://www.adobe.com/content/dam/acom/en/devnet/actionscript/articles/5002.EPSF_Spec.pdf
simple_eps_file = (
    b"%!PS-Adobe-3.0 EPSF-3.0",
    b"%%BoundingBox: 5 5 105 105",
    b"10 setlinewidth",
    b"10 10 moveto",
    b"0 90 rlineto 90 0 rlineto 0 -90 rlineto closepath",
    b"stroke",
)
simple_eps_file_with_comments = (
    simple_eps_file[:1]
    + (
        b"%%Comment1: Some Value",
        b"%%SecondComment: Another Value",
    )
    + simple_eps_file[1:]
)
simple_eps_file_without_version = simple_eps_file[1:]
simple_eps_file_without_boundingbox = simple_eps_file[:1] + simple_eps_file[2:]
simple_eps_file_with_invalid_boundingbox = (
    simple_eps_file[:1] + (b"%%BoundingBox: a b c d",) + simple_eps_file[2:]
)
simple_eps_file_with_invalid_boundingbox_valid_imagedata = (
    simple_eps_file_with_invalid_boundingbox + (b"%ImageData: 100 100 8 3",)
)
simple_eps_file_with_long_ascii_comment = (
    simple_eps_file[:2] + (b"%%Comment: " + b"X" * 300,) + simple_eps_file[2:]
)
simple_eps_file_with_long_binary_data = (
    simple_eps_file[:2]
    + (
        b"%%BeginBinary: 300",
        b"\0" * 300,
        b"%%EndBinary",
    )
    + simple_eps_file[2:]
)


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
@pytest.mark.parametrize(
    ("filename", "size"), ((FILE1, (460, 352)), (FILE2, (360, 252)))
)
@pytest.mark.parametrize("scale", (1, 2))
def test_sanity(filename: str, size: tuple[int, int], scale: int) -> None:
    expected_size = tuple(s * scale for s in size)
    with Image.open(filename) as image:
        image.load(scale=scale)
        assert image.mode == "RGB"
        assert image.size == expected_size
        assert image.format == "EPS"


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_load() -> None:
    with Image.open(FILE1) as im:
        assert im.load()[0, 0] == (255, 255, 255)

        # Test again now that it has already been loaded once
        assert im.load()[0, 0] == (255, 255, 255)


def test_binary() -> None:
    if HAS_GHOSTSCRIPT:
        assert EpsImagePlugin.gs_binary is not None
    else:
        assert EpsImagePlugin.gs_binary is False

    if not is_win32():
        assert EpsImagePlugin.gs_windows_binary is None
    elif not HAS_GHOSTSCRIPT:
        assert EpsImagePlugin.gs_windows_binary is False
    else:
        assert EpsImagePlugin.gs_windows_binary is not None


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"
    with pytest.raises(SyntaxError):
        EpsImagePlugin.EpsImageFile(invalid_file)


def test_binary_header_only() -> None:
    data = io.BytesIO(simple_binary_header)
    with pytest.raises(SyntaxError, match='EPS header missing "%!PS-Adobe" comment'):
        EpsImagePlugin.EpsImageFile(data)


@pytest.mark.parametrize("prefix", (b"", simple_binary_header))
def test_missing_version_comment(prefix: bytes) -> None:
    data = io.BytesIO(prefix + b"\n".join(simple_eps_file_without_version))
    with pytest.raises(SyntaxError):
        EpsImagePlugin.EpsImageFile(data)


@pytest.mark.parametrize("prefix", (b"", simple_binary_header))
def test_missing_boundingbox_comment(prefix: bytes) -> None:
    data = io.BytesIO(prefix + b"\n".join(simple_eps_file_without_boundingbox))
    with pytest.raises(SyntaxError, match='EPS header missing "%%BoundingBox" comment'):
        EpsImagePlugin.EpsImageFile(data)


@pytest.mark.parametrize("prefix", (b"", simple_binary_header))
def test_invalid_boundingbox_comment(prefix: bytes) -> None:
    data = io.BytesIO(prefix + b"\n".join(simple_eps_file_with_invalid_boundingbox))
    with pytest.raises(OSError, match="cannot determine EPS bounding box"):
        EpsImagePlugin.EpsImageFile(data)


@pytest.mark.parametrize("prefix", (b"", simple_binary_header))
def test_invalid_boundingbox_comment_valid_imagedata_comment(prefix: bytes) -> None:
    data = io.BytesIO(
        prefix + b"\n".join(simple_eps_file_with_invalid_boundingbox_valid_imagedata)
    )
    with Image.open(data) as img:
        assert img.mode == "RGB"
        assert img.size == (100, 100)
        assert img.format == "EPS"


@pytest.mark.parametrize("prefix", (b"", simple_binary_header))
def test_ascii_comment_too_long(prefix: bytes) -> None:
    data = io.BytesIO(prefix + b"\n".join(simple_eps_file_with_long_ascii_comment))
    with pytest.raises(SyntaxError, match="not an EPS file"):
        EpsImagePlugin.EpsImageFile(data)


@pytest.mark.parametrize("prefix", (b"", simple_binary_header))
def test_long_binary_data(prefix: bytes) -> None:
    data = io.BytesIO(prefix + b"\n".join(simple_eps_file_with_long_binary_data))
    EpsImagePlugin.EpsImageFile(data)


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
@pytest.mark.parametrize("prefix", (b"", simple_binary_header))
def test_load_long_binary_data(prefix: bytes) -> None:
    data = io.BytesIO(prefix + b"\n".join(simple_eps_file_with_long_binary_data))
    with Image.open(data) as img:
        img.load()
        assert img.mode == "RGB"
        assert img.size == (100, 100)
        assert img.format == "EPS"


@mark_if_feature_version(
    pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
)
@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_cmyk() -> None:
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
def test_showpage() -> None:
    # See https://github.com/python-pillow/Pillow/issues/2615
    with Image.open("Tests/images/reqd_showpage.eps") as plot_image:
        with Image.open("Tests/images/reqd_showpage.png") as target:
            # should not crash/hang
            plot_image.load()
            # fonts could be slightly different
            assert_image_similar(plot_image, target, 6)


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_transparency() -> None:
    with Image.open("Tests/images/reqd_showpage.eps") as plot_image:
        plot_image.load(transparency=True)
        assert plot_image.mode == "RGBA"

        with Image.open("Tests/images/reqd_showpage_transparency.png") as target:
            # fonts could be slightly different
            assert_image_similar(plot_image, target, 6)


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_file_object(tmp_path: Path) -> None:
    # issue 479
    with Image.open(FILE1) as image1:
        with open(str(tmp_path / "temp.eps"), "wb") as fh:
            image1.save(fh, "EPS")


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_bytesio_object() -> None:
    with open(FILE1, "rb") as f:
        img_bytes = io.BytesIO(f.read())

    with Image.open(img_bytes) as img:
        img.load()

        with Image.open(FILE1_COMPARE) as image1_scale1_compare:
            image1_scale1_compare = image1_scale1_compare.convert("RGB")
        image1_scale1_compare.load()
        assert_image_similar(img, image1_scale1_compare, 5)


def test_1_mode() -> None:
    with Image.open("Tests/images/1.eps") as im:
        assert im.mode == "1"


def test_image_mode_not_supported(tmp_path: Path) -> None:
    im = hopper("RGBA")
    tmpfile = str(tmp_path / "temp.eps")
    with pytest.raises(ValueError):
        im.save(tmpfile)


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
@skip_unless_feature("zlib")
def test_render_scale1() -> None:
    # We need png support for these render test

    # Zero bounding box
    with Image.open(FILE1) as image1_scale1:
        image1_scale1.load()
        with Image.open(FILE1_COMPARE) as image1_scale1_compare:
            image1_scale1_compare = image1_scale1_compare.convert("RGB")
        image1_scale1_compare.load()
        assert_image_similar(image1_scale1, image1_scale1_compare, 5)

    # Non-zero bounding box
    with Image.open(FILE2) as image2_scale1:
        image2_scale1.load()
        with Image.open(FILE2_COMPARE) as image2_scale1_compare:
            image2_scale1_compare = image2_scale1_compare.convert("RGB")
        image2_scale1_compare.load()
        assert_image_similar(image2_scale1, image2_scale1_compare, 10)


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
@skip_unless_feature("zlib")
def test_render_scale2() -> None:
    # We need png support for these render test

    # Zero bounding box
    with Image.open(FILE1) as image1_scale2:
        image1_scale2.load(scale=2)
        with Image.open(FILE1_COMPARE_SCALE2) as image1_scale2_compare:
            image1_scale2_compare = image1_scale2_compare.convert("RGB")
        image1_scale2_compare.load()
        assert_image_similar(image1_scale2, image1_scale2_compare, 5)

    # Non-zero bounding box
    with Image.open(FILE2) as image2_scale2:
        image2_scale2.load(scale=2)
        with Image.open(FILE2_COMPARE_SCALE2) as image2_scale2_compare:
            image2_scale2_compare = image2_scale2_compare.convert("RGB")
        image2_scale2_compare.load()
        assert_image_similar(image2_scale2, image2_scale2_compare, 10)


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
@pytest.mark.parametrize("filename", (FILE1, FILE2, "Tests/images/illu10_preview.eps"))
def test_resize(filename: str) -> None:
    with Image.open(filename) as im:
        new_size = (100, 100)
        im = im.resize(new_size)
        assert im.size == new_size


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
@pytest.mark.parametrize("filename", (FILE1, FILE2))
def test_thumbnail(filename: str) -> None:
    # Issue #619
    with Image.open(filename) as im:
        new_size = (100, 100)
        im.thumbnail(new_size)
        assert max(im.size) == max(new_size)


def test_read_binary_preview() -> None:
    # Issue 302
    # open image with binary preview
    with Image.open(FILE3):
        pass


def test_readline_psfile(tmp_path: Path) -> None:
    # check all the freaking line endings possible from the spec
    # test_string = u'something\r\nelse\n\rbaz\rbif\n'
    line_endings = ["\r\n", "\n", "\n\r", "\r"]
    strings = ["something", "else", "baz", "bif"]

    def _test_readline(t: EpsImagePlugin.PSFile, ending: str) -> None:
        ending = f"Failure with line ending: {''.join(str(ord(s)) for s in ending)}"
        assert t.readline().strip("\r\n") == "something", ending
        assert t.readline().strip("\r\n") == "else", ending
        assert t.readline().strip("\r\n") == "baz", ending
        assert t.readline().strip("\r\n") == "bif", ending

    def _test_readline_io_psfile(test_string: str, ending: str) -> None:
        f = io.BytesIO(test_string.encode("latin-1"))
        with pytest.warns(DeprecationWarning):
            t = EpsImagePlugin.PSFile(f)
        _test_readline(t, ending)

    def _test_readline_file_psfile(test_string: str, ending: str) -> None:
        f = str(tmp_path / "temp.txt")
        with open(f, "wb") as w:
            w.write(test_string.encode("latin-1"))

        with open(f, "rb") as r:
            with pytest.warns(DeprecationWarning):
                t = EpsImagePlugin.PSFile(r)
            _test_readline(t, ending)

    for ending in line_endings:
        s = ending.join(strings)
        _test_readline_io_psfile(s, ending)
        _test_readline_file_psfile(s, ending)


def test_psfile_deprecation() -> None:
    with pytest.warns(DeprecationWarning):
        EpsImagePlugin.PSFile(None)


@pytest.mark.parametrize("prefix", (b"", simple_binary_header))
@pytest.mark.parametrize(
    "line_ending",
    (b"\r\n", b"\n", b"\n\r", b"\r"),
)
def test_readline(prefix: bytes, line_ending: bytes) -> None:
    simple_file = prefix + line_ending.join(simple_eps_file_with_comments)
    data = io.BytesIO(simple_file)
    test_file = EpsImagePlugin.EpsImageFile(data)
    assert test_file.info["Comment1"] == "Some Value"
    assert test_file.info["SecondComment"] == "Another Value"
    assert test_file.size == (100, 100)


@pytest.mark.parametrize(
    "filename",
    (
        "Tests/images/illu10_no_preview.eps",
        "Tests/images/illu10_preview.eps",
        "Tests/images/illuCS6_no_preview.eps",
        "Tests/images/illuCS6_preview.eps",
    ),
)
def test_open_eps(filename: str) -> None:
    # https://github.com/python-pillow/Pillow/issues/1104
    with Image.open(filename) as img:
        assert img.mode == "RGB"


@pytest.mark.skipif(not HAS_GHOSTSCRIPT, reason="Ghostscript not available")
def test_emptyline() -> None:
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
def test_timeout(test_file: str) -> None:
    with open(test_file, "rb") as f:
        with pytest.raises(UnidentifiedImageError):
            with Image.open(f):
                pass


def test_bounding_box_in_trailer() -> None:
    # Check bounding boxes are parsed in the same way
    # when specified in the header and the trailer
    with Image.open("Tests/images/zero_bb_trailer.eps") as trailer_image, Image.open(
        FILE1
    ) as header_image:
        assert trailer_image.size == header_image.size


def test_eof_before_bounding_box() -> None:
    with pytest.raises(OSError):
        with Image.open("Tests/images/zero_bb_eof_before_boundingbox.eps"):
            pass


def test_invalid_data_after_eof() -> None:
    with open("Tests/images/illuCS6_preview.eps", "rb") as f:
        img_bytes = io.BytesIO(f.read() + b"\r\n%" + (b" " * 255))

    with Image.open(img_bytes) as img:
        assert img.mode == "RGB"

# class TestHasGhostscript(unittest.TestCase):
#     @patch('PIL.EpsImagePlugin.shutil.which')
#     @patch('PIL.EpsImagePlugin.sys.platform', 'win32')
#     def test_windows_with_ghostscript(self, mock_which):
#         # Simulate each binary being found in turn
#         for binary in ("gswin32c", "gswin64c", "gs"):
#             with self.subTest(binary=binary):
#                 EpsImagePlugin.gs_binary = None  # Reset global state
#                 mock_which.side_effect = lambda x: x if x == binary else None
#                 self.assertTrue(EpsImagePlugin.has_ghostscript())
#                 self.assertEqual(EpsImagePlugin.gs_windows_binary, binary)
#
#     @patch('PIL.EpsImagePlugin.shutil.which', return_value=None)
#     @patch('PIL.EpsImagePlugin.sys.platform', 'win32')
#     def test_windows_without_ghostscript(self, mock_which):
#         EpsImagePlugin.gs_binary = None  # Reset global state
#         self.assertFalse(EpsImagePlugin.has_ghostscript())
#         self.assertFalse(EpsImagePlugin.gs_windows_binary)
#
#     @patch('PIL.EpsImagePlugin.subprocess.check_call')
#     @patch('PIL.EpsImagePlugin.sys.platform', 'linux')
#     def test_non_windows_with_ghostscript(self, mock_check_call):
#         EpsImagePlugin.gs_binary = None  # Reset global state
#         mock_check_call.return_value = 0  # Simulate successful call
#         self.assertTrue(EpsImagePlugin.has_ghostscript())
#         self.assertEqual(EpsImagePlugin.gs_binary, "gs")
#
#     @patch('PIL.EpsImagePlugin.subprocess.check_call', side_effect=OSError)
#     @patch('PIL.EpsImagePlugin.sys.platform', 'linux')
#     def test_non_windows_without_ghostscript(self, mock_check_call):
#         EpsImagePlugin.gs_binary = None  # Reset global state
#         self.assertFalse(EpsImagePlugin.has_ghostscript())
#         self.assertFalse(EpsImagePlugin.gs_binary)
#
# if __name__ == '__main__':
#     unittest.main()
