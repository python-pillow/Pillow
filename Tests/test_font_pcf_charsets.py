import os

import pytest

from PIL import FontFile, Image, ImageDraw, ImageFont, PcfFontFile

from .helper import (
    assert_image_equal_tofile,
    assert_image_similar_tofile,
    skip_unless_feature,
)

fontname = "Tests/fonts/ter-x20b.pcf"

charsets = {
    "iso8859-1": {
        "glyph_count": 223,
        "message": "hello, world",
        "image1": "Tests/images/test_draw_pbm_ter_en_target.png",
    },
    "iso8859-2": {
        "glyph_count": 223,
        "message": "witaj świecie",
        "image1": "Tests/images/test_draw_pbm_ter_pl_target.png",
    },
    "cp1250": {
        "glyph_count": 250,
        "message": "witaj świecie",
        "image1": "Tests/images/test_draw_pbm_ter_pl_target.png",
    },
}


pytestmark = skip_unless_feature("zlib")


def save_font(request, tmp_path, encoding):
    with open(fontname, "rb") as test_file:
        font = PcfFontFile.PcfFontFile(test_file, encoding)
    assert isinstance(font, FontFile.FontFile)
    # check the number of characters in the font
    assert len([_f for _f in font.glyph if _f]) == charsets[encoding]["glyph_count"]

    tempname = str(tmp_path / "temp.pil")

    def delete_tempfile():
        try:
            os.remove(tempname[:-4] + ".pbm")
        except OSError:
            pass  # report?

    request.addfinalizer(delete_tempfile)
    font.save(tempname)

    with Image.open(tempname.replace(".pil", ".pbm")) as loaded:
        assert_image_equal_tofile(loaded, f"Tests/fonts/ter-x20b-{encoding}.pbm")

    with open(tempname, "rb") as f_loaded:
        with open(f"Tests/fonts/ter-x20b-{encoding}.pil", "rb") as f_target:
            assert f_loaded.read() == f_target.read()
    return tempname


@pytest.mark.parametrize("encoding", ("iso8859-1", "iso8859-2", "cp1250"))
def test_sanity(request, tmp_path, encoding):
    save_font(request, tmp_path, encoding)


@pytest.mark.parametrize("encoding", ("iso8859-1", "iso8859-2", "cp1250"))
def test_draw(request, tmp_path, encoding):
    tempname = save_font(request, tmp_path, encoding)
    font = ImageFont.load(tempname)
    im = Image.new("L", (150, 30), "white")
    draw = ImageDraw.Draw(im)
    message = charsets[encoding]["message"].encode(encoding)
    draw.text((0, 0), message, "black", font=font)
    assert_image_similar_tofile(im, charsets[encoding]["image1"], 0)


@pytest.mark.parametrize("encoding", ("iso8859-1", "iso8859-2", "cp1250"))
def test_textsize(request, tmp_path, encoding):
    tempname = save_font(request, tmp_path, encoding)
    font = ImageFont.load(tempname)
    for i in range(255):
        (ox, oy, dx, dy) = font.getbbox(bytearray([i]))
        assert ox == 0
        assert oy == 0
        assert dy == 20
        assert dx in (0, 10)
        assert font.getlength(bytearray([i])) == dx
    message = charsets[encoding]["message"].encode(encoding)
    for i in range(len(message)):
        msg = message[: i + 1]
        assert font.getlength(msg) == len(msg) * 10
        assert font.getbbox(msg) == (0, 0, len(msg) * 10, 20)
