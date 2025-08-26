from __future__ import annotations

import re
import sys
import warnings
import zlib
from io import BytesIO
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import pytest

from PIL import Image, ImageFile, PngImagePlugin, features

from .helper import (
    PillowLeakTestCase,
    assert_image,
    assert_image_equal,
    assert_image_equal_tofile,
    hopper,
    is_win32,
    mark_if_feature_version,
    skip_unless_feature,
)

ElementTree: ModuleType | None
try:
    from defusedxml import ElementTree
except ImportError:
    ElementTree = None

# sample png stream

TEST_PNG_FILE = "Tests/images/hopper.png"

# stuff to create inline PNG images

MAGIC = PngImagePlugin._MAGIC


def chunk(cid: bytes, *data: bytes) -> bytes:
    test_file = BytesIO()
    PngImagePlugin.putchunk(test_file, cid, *data)
    return test_file.getvalue()


o32 = PngImagePlugin.o32

IHDR = chunk(b"IHDR", o32(1), o32(1), b"\x08\x02", b"\0\0\0")
IDAT = chunk(b"IDAT")
IEND = chunk(b"IEND")

HEAD = MAGIC + IHDR
TAIL = IDAT + IEND


def load(data: bytes) -> Image.Image:
    return Image.open(BytesIO(data))


def roundtrip(im: Image.Image, **options: Any) -> PngImagePlugin.PngImageFile:
    out = BytesIO()
    im.save(out, "PNG", **options)
    out.seek(0)
    return cast(PngImagePlugin.PngImageFile, Image.open(out))


@skip_unless_feature("zlib")
class TestFilePng:
    def get_chunks(self, filename: Path) -> list[bytes]:
        chunks = []
        with open(filename, "rb") as fp:
            fp.read(8)
            with PngImagePlugin.PngStream(fp) as png:
                while True:
                    cid, pos, length = png.read()
                    chunks.append(cid)
                    try:
                        s = png.call(cid, pos, length)
                    except EOFError:
                        break
                    png.crc(cid, s)
        return chunks

    def test_sanity(self, tmp_path: Path) -> None:
        # internal version number
        version = features.version_codec("zlib")
        assert version is not None
        assert re.search(r"\d+(\.\d+){1,3}(\.zlib\-ng)?$", version)

        test_file = tmp_path / "temp.png"

        hopper("RGB").save(test_file)

        with Image.open(test_file) as im:
            im.load()
            assert im.mode == "RGB"
            assert im.size == (128, 128)
            assert im.format == "PNG"
            assert im.get_format_mimetype() == "image/png"

        for mode in ["1", "L", "P", "RGB", "I;16", "I;16B"]:
            im = hopper(mode)
            im.save(test_file)
            with Image.open(test_file) as reloaded:
                if mode == "I;16B":
                    reloaded = reloaded.convert(mode)
                assert_image_equal(reloaded, im)

    def test_invalid_file(self) -> None:
        invalid_file = "Tests/images/flower.jpg"

        with pytest.raises(SyntaxError):
            PngImagePlugin.PngImageFile(invalid_file)

    def test_broken(self) -> None:
        # Check reading of totally broken files.  In this case, the test
        # file was checked into Subversion as a text file.

        test_file = "Tests/images/broken.png"
        with pytest.raises(OSError):
            with Image.open(test_file):
                pass

    def test_bad_text(self) -> None:
        # Make sure PIL can read malformed tEXt chunks (@PIL152)

        im = load(HEAD + chunk(b"tEXt") + TAIL)
        assert im.info == {}

        im = load(HEAD + chunk(b"tEXt", b"spam") + TAIL)
        assert im.info == {"spam": ""}

        im = load(HEAD + chunk(b"tEXt", b"spam\0") + TAIL)
        assert im.info == {"spam": ""}

        im = load(HEAD + chunk(b"tEXt", b"spam\0egg") + TAIL)
        assert im.info == {"spam": "egg"}

        im = load(HEAD + chunk(b"tEXt", b"spam\0egg\0") + TAIL)
        assert im.info == {"spam": "egg\x00"}

    def test_bad_ztxt(self) -> None:
        # Test reading malformed zTXt chunks (python-pillow/Pillow#318)

        im = load(HEAD + chunk(b"zTXt") + TAIL)
        assert im.info == {}

        im = load(HEAD + chunk(b"zTXt", b"spam") + TAIL)
        assert im.info == {"spam": ""}

        im = load(HEAD + chunk(b"zTXt", b"spam\0") + TAIL)
        assert im.info == {"spam": ""}

        im = load(HEAD + chunk(b"zTXt", b"spam\0\0") + TAIL)
        assert im.info == {"spam": ""}

        im = load(HEAD + chunk(b"zTXt", b"spam\0\0" + zlib.compress(b"egg")[:1]) + TAIL)
        assert im.info == {"spam": ""}

        im = load(HEAD + chunk(b"zTXt", b"spam\0\0" + zlib.compress(b"egg")) + TAIL)
        assert im.info == {"spam": "egg"}

    def test_bad_itxt(self) -> None:
        im = load(HEAD + chunk(b"iTXt") + TAIL)
        assert im.info == {}

        im = load(HEAD + chunk(b"iTXt", b"spam") + TAIL)
        assert im.info == {}

        im = load(HEAD + chunk(b"iTXt", b"spam\0") + TAIL)
        assert im.info == {}

        im = load(HEAD + chunk(b"iTXt", b"spam\0\x02") + TAIL)
        assert im.info == {}

        im = load(HEAD + chunk(b"iTXt", b"spam\0\0\0foo\0") + TAIL)
        assert im.info == {}

        im = load(HEAD + chunk(b"iTXt", b"spam\0\0\0en\0Spam\0egg") + TAIL)
        assert im.info == {"spam": "egg"}
        assert im.info["spam"].lang == "en"
        assert im.info["spam"].tkey == "Spam"

        im = load(
            HEAD
            + chunk(b"iTXt", b"spam\0\1\0en\0Spam\0" + zlib.compress(b"egg")[:1])
            + TAIL
        )
        assert im.info == {"spam": ""}

        im = load(
            HEAD
            + chunk(b"iTXt", b"spam\0\1\1en\0Spam\0" + zlib.compress(b"egg"))
            + TAIL
        )
        assert im.info == {}

        im = load(
            HEAD
            + chunk(b"iTXt", b"spam\0\1\0en\0Spam\0" + zlib.compress(b"egg"))
            + TAIL
        )
        assert im.info == {"spam": "egg"}
        assert im.info["spam"].lang == "en"
        assert im.info["spam"].tkey == "Spam"

    def test_interlace(self) -> None:
        test_file = "Tests/images/pil123p.png"
        with Image.open(test_file) as im:
            assert_image(im, "P", (162, 150))
            assert im.info.get("interlace")

            im.load()

        test_file = "Tests/images/pil123rgba.png"
        with Image.open(test_file) as im:
            assert_image(im, "RGBA", (162, 150))
            assert im.info.get("interlace")

            im.load()

    def test_load_transparent_p(self) -> None:
        test_file = "Tests/images/pil123p.png"
        with Image.open(test_file) as im:
            assert_image(im, "P", (162, 150))
            im = im.convert("RGBA")
        assert_image(im, "RGBA", (162, 150))

        # image has 124 unique alpha values
        assert len(im.getchannel("A").getcolors()) == 124

    def test_load_transparent_rgb(self) -> None:
        test_file = "Tests/images/rgb_trns.png"
        with Image.open(test_file) as im:
            assert im.info["transparency"] == (0, 255, 52)

            assert_image(im, "RGB", (64, 64))
            im = im.convert("RGBA")
        assert_image(im, "RGBA", (64, 64))

        # image has 876 transparent pixels
        assert im.getchannel("A").getcolors()[0][0] == 876

    def test_save_p_transparent_palette(self, tmp_path: Path) -> None:
        in_file = "Tests/images/pil123p.png"
        with Image.open(in_file) as im:
            # 'transparency' contains a byte string with the opacity for
            # each palette entry
            assert len(im.info["transparency"]) == 256

            test_file = tmp_path / "temp.png"
            im.save(test_file)

        # check if saved image contains same transparency
        with Image.open(test_file) as im:
            assert len(im.info["transparency"]) == 256

            assert_image(im, "P", (162, 150))
            im = im.convert("RGBA")
        assert_image(im, "RGBA", (162, 150))

        # image has 124 unique alpha values
        assert len(im.getchannel("A").getcolors()) == 124

    def test_save_p_single_transparency(self, tmp_path: Path) -> None:
        in_file = "Tests/images/p_trns_single.png"
        with Image.open(in_file) as im:
            # pixel value 164 is full transparent
            assert im.info["transparency"] == 164
            assert im.getpixel((31, 31)) == 164

            test_file = tmp_path / "temp.png"
            im.save(test_file)

        # check if saved image contains same transparency
        with Image.open(test_file) as im:
            assert im.info["transparency"] == 164
            assert im.getpixel((31, 31)) == 164
            assert_image(im, "P", (64, 64))
            im = im.convert("RGBA")
        assert_image(im, "RGBA", (64, 64))

        assert im.getpixel((31, 31)) == (0, 255, 52, 0)

        # image has 876 transparent pixels
        assert im.getchannel("A").getcolors()[0][0] == 876

    def test_save_p_transparent_black(self, tmp_path: Path) -> None:
        # check if solid black image with full transparency
        # is supported (check for #1838)
        im = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        assert im.getcolors() == [(100, (0, 0, 0, 0))]

        im = im.convert("P")
        test_file = tmp_path / "temp.png"
        im.save(test_file)

        # check if saved image contains same transparency
        with Image.open(test_file) as im:
            assert len(im.info["transparency"]) == 256
            assert_image(im, "P", (10, 10))
            im = im.convert("RGBA")
        assert_image(im, "RGBA", (10, 10))
        assert im.getcolors() == [(100, (0, 0, 0, 0))]

    def test_save_grayscale_transparency(self, tmp_path: Path) -> None:
        for mode, num_transparent in {"1": 1994, "L": 559, "I;16": 559}.items():
            in_file = "Tests/images/" + mode.split(";")[0].lower() + "_trns.png"
            with Image.open(in_file) as im:
                assert im.mode == mode
                assert im.info["transparency"] == 255

                im_rgba = im.convert("RGBA")
            assert im_rgba.getchannel("A").getcolors()[0][0] == num_transparent

            test_file = tmp_path / "temp.png"
            im.save(test_file)

            with Image.open(test_file) as test_im:
                assert test_im.mode == mode
                assert test_im.info["transparency"] == 255
                assert_image_equal(im, test_im)

            test_im_rgba = test_im.convert("RGBA")
            assert test_im_rgba.getchannel("A").getcolors()[0][0] == num_transparent

    def test_save_rgb_single_transparency(self, tmp_path: Path) -> None:
        in_file = "Tests/images/caption_6_33_22.png"
        with Image.open(in_file) as im:
            test_file = tmp_path / "temp.png"
            im.save(test_file)

    def test_load_verify(self) -> None:
        # Check open/load/verify exception (@PIL150)

        with Image.open(TEST_PNG_FILE) as im:
            # Assert that there is no unclosed file warning
            with warnings.catch_warnings():
                warnings.simplefilter("error")

                im.verify()

        with Image.open(TEST_PNG_FILE) as im:
            im.load()
            with pytest.raises(RuntimeError):
                im.verify()

    def test_verify_struct_error(self) -> None:
        # Check open/load/verify exception (#1755)

        # offsets to test, -10: breaks in i32() in read. (OSError)
        #                  -13: breaks in crc, txt chunk.
        #                  -14: malformed chunk

        for offset in (-10, -13, -14):
            with open(TEST_PNG_FILE, "rb") as f:
                test_file = f.read()[:offset]

            with Image.open(BytesIO(test_file)) as im:
                assert im.fp is not None
                with pytest.raises((OSError, SyntaxError)):
                    im.verify()

    def test_verify_ignores_crc_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # check ignores crc errors in ancillary chunks

        chunk_data = chunk(b"tEXt", b"spam")
        broken_crc_chunk_data = chunk_data[:-1] + b"q"  # break CRC

        image_data = HEAD + broken_crc_chunk_data + TAIL
        with pytest.raises(SyntaxError):
            PngImagePlugin.PngImageFile(BytesIO(image_data))

        monkeypatch.setattr(ImageFile, "LOAD_TRUNCATED_IMAGES", True)
        im = load(image_data)
        assert im is not None

    def test_verify_not_ignores_crc_error_in_required_chunk(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # check does not ignore crc errors in required chunks

        image_data = MAGIC + IHDR[:-1] + b"q" + TAIL

        monkeypatch.setattr(ImageFile, "LOAD_TRUNCATED_IMAGES", True)
        with pytest.raises(SyntaxError):
            PngImagePlugin.PngImageFile(BytesIO(image_data))

    def test_roundtrip_dpi(self) -> None:
        # Check dpi roundtripping

        with Image.open(TEST_PNG_FILE) as im:
            im = roundtrip(im, dpi=(100.33, 100.33))
        assert im.info["dpi"] == (100.33, 100.33)

    def test_load_float_dpi(self) -> None:
        with Image.open(TEST_PNG_FILE) as im:
            assert im.info["dpi"] == (95.9866, 95.9866)

    def test_roundtrip_text(self) -> None:
        # Check text roundtripping

        with Image.open(TEST_PNG_FILE) as im:
            info = PngImagePlugin.PngInfo()
            info.add_text("TXT", "VALUE")
            info.add_text("ZIP", "VALUE", zip=True)

            im = roundtrip(im, pnginfo=info)
        assert im.info == {"TXT": "VALUE", "ZIP": "VALUE"}
        assert im.text == {"TXT": "VALUE", "ZIP": "VALUE"}

    def test_roundtrip_itxt(self) -> None:
        # Check iTXt roundtripping

        im = Image.new("RGB", (32, 32))
        info = PngImagePlugin.PngInfo()
        info.add_itxt("spam", "Eggs", "en", "Spam")
        info.add_text("eggs", PngImagePlugin.iTXt("Spam", "en", "Eggs"), zip=True)

        im = roundtrip(im, pnginfo=info)
        assert im.info == {"spam": "Eggs", "eggs": "Spam"}
        assert im.text == {"spam": "Eggs", "eggs": "Spam"}
        assert isinstance(im.text["spam"], PngImagePlugin.iTXt)
        assert im.text["spam"].lang == "en"
        assert im.text["spam"].tkey == "Spam"
        assert isinstance(im.text["eggs"], PngImagePlugin.iTXt)
        assert im.text["eggs"].lang == "en"
        assert im.text["eggs"].tkey == "Eggs"

    def test_nonunicode_text(self) -> None:
        # Check so that non-Unicode text is saved as a tEXt rather than iTXt

        im = Image.new("RGB", (32, 32))
        info = PngImagePlugin.PngInfo()
        info.add_text("Text", "Ascii")
        im = roundtrip(im, pnginfo=info)
        assert isinstance(im.info["Text"], str)

    def test_unicode_text(self) -> None:
        # Check preservation of non-ASCII characters

        def rt_text(value: str) -> None:
            im = Image.new("RGB", (32, 32))
            info = PngImagePlugin.PngInfo()
            info.add_text("Text", value)
            im = roundtrip(im, pnginfo=info)
            assert im.info == {"Text": value}

        rt_text(" Aa" + chr(0xA0) + chr(0xC4) + chr(0xFF))  # Latin1
        rt_text(chr(0x400) + chr(0x472) + chr(0x4FF))  # Cyrillic
        # CJK:
        rt_text(chr(0x4E00) + chr(0x66F0) + chr(0x9FBA) + chr(0x3042) + chr(0xAC00))
        rt_text("A" + chr(0xC4) + chr(0x472) + chr(0x3042))  # Combined

    def test_scary(self) -> None:
        # Check reading of evil PNG file.  For information, see:
        # http://scary.beasts.org/security/CESA-2004-001.txt
        # The first byte is removed from pngtest_bad.png
        # to avoid classification as malware.

        with open("Tests/images/pngtest_bad.png.bin", "rb") as fd:
            data = b"\x89" + fd.read()

        pngfile = BytesIO(data)
        with pytest.raises(OSError):
            with Image.open(pngfile):
                pass

    def test_trns_rgb(self) -> None:
        # Check writing and reading of tRNS chunks for RGB images.
        # Independent file sample provided by Sebastian Spaeth.

        test_file = "Tests/images/caption_6_33_22.png"
        with Image.open(test_file) as im:
            assert im.info["transparency"] == (248, 248, 248)

            # check saving transparency by default
            im = roundtrip(im)
        assert im.info["transparency"] == (248, 248, 248)

        im = roundtrip(im, transparency=(0, 1, 2))
        assert im.info["transparency"] == (0, 1, 2)

    def test_trns_p(self, tmp_path: Path) -> None:
        # Check writing a transparency of 0, issue #528
        im = hopper("P")
        im.info["transparency"] = 0

        f = tmp_path / "temp.png"
        im.save(f)

        with Image.open(f) as im2:
            assert "transparency" in im2.info

            assert_image_equal(im2.convert("RGBA"), im.convert("RGBA"))

    def test_trns_null(self) -> None:
        # Check reading images with null tRNS value, issue #1239
        test_file = "Tests/images/tRNS_null_1x1.png"
        with Image.open(test_file) as im:
            assert im.info["transparency"] == 0

    def test_save_icc_profile(self) -> None:
        with Image.open("Tests/images/icc_profile_none.png") as im:
            assert im.info["icc_profile"] is None

            with Image.open("Tests/images/icc_profile.png") as with_icc:
                expected_icc = with_icc.info["icc_profile"]

                im = roundtrip(im, icc_profile=expected_icc)
                assert im.info["icc_profile"] == expected_icc

    def test_discard_icc_profile(self) -> None:
        with Image.open("Tests/images/icc_profile.png") as im:
            assert "icc_profile" in im.info

            im = roundtrip(im, icc_profile=None)
        assert "icc_profile" not in im.info

    def test_roundtrip_icc_profile(self) -> None:
        with Image.open("Tests/images/icc_profile.png") as im:
            expected_icc = im.info["icc_profile"]

            im = roundtrip(im)
        assert im.info["icc_profile"] == expected_icc

    def test_roundtrip_no_icc_profile(self) -> None:
        with Image.open("Tests/images/icc_profile_none.png") as im:
            assert im.info["icc_profile"] is None

            im = roundtrip(im)
        assert "icc_profile" not in im.info

    def test_repr_png(self) -> None:
        im = hopper()
        b = im._repr_png_()
        assert b is not None

        with Image.open(BytesIO(b)) as repr_png:
            assert repr_png.format == "PNG"
            assert_image_equal(im, repr_png)

    def test_repr_png_error_returns_none(self) -> None:
        im = hopper("F")

        assert im._repr_png_() is None

    def test_chunk_order(self, tmp_path: Path) -> None:
        with Image.open("Tests/images/icc_profile.png") as im:
            test_file = tmp_path / "temp.png"
            im.convert("P").save(test_file, dpi=(100, 100))

        chunks = self.get_chunks(test_file)

        # https://www.w3.org/TR/PNG/#5ChunkOrdering
        # IHDR - shall be first
        assert chunks.index(b"IHDR") == 0
        # PLTE - before first IDAT
        assert chunks.index(b"PLTE") < chunks.index(b"IDAT")
        # iCCP - before PLTE and IDAT
        assert chunks.index(b"iCCP") < chunks.index(b"PLTE")
        assert chunks.index(b"iCCP") < chunks.index(b"IDAT")
        # tRNS - after PLTE, before IDAT
        assert chunks.index(b"tRNS") > chunks.index(b"PLTE")
        assert chunks.index(b"tRNS") < chunks.index(b"IDAT")
        # pHYs - before IDAT
        assert chunks.index(b"pHYs") < chunks.index(b"IDAT")

    def test_getchunks(self) -> None:
        im = hopper()

        chunks = PngImagePlugin.getchunks(im)
        assert len(chunks) == 3

    def test_read_private_chunks(self) -> None:
        with Image.open("Tests/images/exif.png") as im:
            assert isinstance(im, PngImagePlugin.PngImageFile)
            assert im.private_chunks == [(b"orNT", b"\x01")]

    def test_roundtrip_private_chunk(self) -> None:
        # Check private chunk roundtripping

        with Image.open(TEST_PNG_FILE) as im:
            info = PngImagePlugin.PngInfo()
            info.add(b"prIV", b"VALUE")
            info.add(b"atEC", b"VALUE2")
            info.add(b"prIV", b"VALUE3", True)

            im = roundtrip(im, pnginfo=info)
        assert im.private_chunks == [(b"prIV", b"VALUE"), (b"atEC", b"VALUE2")]
        im.load()
        assert im.private_chunks == [
            (b"prIV", b"VALUE"),
            (b"atEC", b"VALUE2"),
            (b"prIV", b"VALUE3", True),
        ]

    def test_textual_chunks_after_idat(self, monkeypatch: pytest.MonkeyPatch) -> None:
        with Image.open("Tests/images/hopper.png") as im:
            assert isinstance(im, PngImagePlugin.PngImageFile)
            assert "comment" in im.text
            for k, v in {
                "date:create": "2014-09-04T09:37:08+03:00",
                "date:modify": "2014-09-04T09:37:08+03:00",
            }.items():
                assert im.text[k] == v

        # Raises a SyntaxError in load_end
        with Image.open("Tests/images/broken_data_stream.png") as im:
            assert isinstance(im, PngImagePlugin.PngImageFile)
            with pytest.raises(OSError):
                assert isinstance(im.text, dict)

        # Raises an EOFError in load_end
        with Image.open("Tests/images/hopper_idat_after_image_end.png") as im:
            assert isinstance(im, PngImagePlugin.PngImageFile)
            assert im.text == {"TXT": "VALUE", "ZIP": "VALUE"}

        # Raises a UnicodeDecodeError in load_end
        with Image.open("Tests/images/truncated_image.png") as im:
            assert isinstance(im, PngImagePlugin.PngImageFile)

            # The file is truncated
            with pytest.raises(OSError):
                im.text
            monkeypatch.setattr(ImageFile, "LOAD_TRUNCATED_IMAGES", True)
            assert isinstance(im.text, dict)

    def test_unknown_compression_method(self) -> None:
        with pytest.raises(SyntaxError, match="Unknown compression method"):
            PngImagePlugin.PngImageFile("Tests/images/unknown_compression_method.png")

    def test_padded_idat(self) -> None:
        # This image has been manually hexedited
        # so that the IDAT chunk has padding at the end
        # Set MAXBLOCK to the length of the actual data
        # so that the decoder finishes reading before the chunk ends
        MAXBLOCK = ImageFile.MAXBLOCK
        ImageFile.MAXBLOCK = 45
        ImageFile.LOAD_TRUNCATED_IMAGES = True

        with Image.open("Tests/images/padded_idat.png") as im:
            im.load()

            ImageFile.MAXBLOCK = MAXBLOCK
            ImageFile.LOAD_TRUNCATED_IMAGES = False

            assert_image_equal_tofile(im, "Tests/images/bw_gradient.png")

    @pytest.mark.parametrize(
        "cid", (b"IHDR", b"sRGB", b"pHYs", b"acTL", b"fcTL", b"fdAT")
    )
    def test_truncated_chunks(
        self, cid: bytes, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fp = BytesIO()
        with PngImagePlugin.PngStream(fp) as png:
            with pytest.raises(ValueError):
                png.call(cid, 0, 0)

            monkeypatch.setattr(ImageFile, "LOAD_TRUNCATED_IMAGES", True)
            png.call(cid, 0, 0)

    @pytest.mark.parametrize("save_all", (True, False))
    def test_specify_bits(self, save_all: bool, tmp_path: Path) -> None:
        im = hopper("P")

        out = tmp_path / "temp.png"
        im.save(out, bits=4, save_all=save_all)

        with Image.open(out) as reloaded:
            assert len(reloaded.png.im_palette[1]) == 48

    def test_plte_length(self, tmp_path: Path) -> None:
        im = Image.new("P", (1, 1))
        im.putpalette((1, 1, 1))

        out = tmp_path / "temp.png"
        im.save(out)

        with Image.open(out) as reloaded:
            assert len(reloaded.png.im_palette[1]) == 3

    def test_getxmp(self) -> None:
        with Image.open("Tests/images/color_snakes.png") as im:
            if ElementTree is None:
                with pytest.warns(
                    UserWarning,
                    match="XMP data cannot be read without defusedxml dependency",
                ):
                    assert im.getxmp() == {}
            else:
                assert "xmp" in im.info
                xmp = im.getxmp()

                description = xmp["xmpmeta"]["RDF"]["Description"]
                assert description["PixelXDimension"] == "10"
                assert description["subject"]["Seq"] is None

    def test_exif(self) -> None:
        # With an EXIF chunk
        with Image.open("Tests/images/exif.png") as im:
            exif = im._getexif()
        assert exif[274] == 1

        # With an ImageMagick zTXt chunk
        with Image.open("Tests/images/exif_imagemagick.png") as im:
            exif = im._getexif()
            assert exif[274] == 1

            # Assert that info still can be extracted
            # when the image is no longer a PngImageFile instance
            exif = im.copy().getexif()
            assert exif[274] == 1

        # With a tEXt chunk
        with Image.open("Tests/images/exif_text.png") as im:
            exif = im._getexif()
        assert exif[274] == 1

        # With XMP tags
        with Image.open("Tests/images/xmp_tags_orientation.png") as im:
            exif = im.getexif()
        assert exif[274] == 3

    def test_exif_save(self, tmp_path: Path) -> None:
        # Test exif is not saved from info
        test_file = tmp_path / "temp.png"
        with Image.open("Tests/images/exif.png") as im:
            im.save(test_file)

        with Image.open(test_file) as reloaded:
            assert isinstance(reloaded, PngImagePlugin.PngImageFile)
            assert reloaded._getexif() is None

        # Test passing in exif
        with Image.open("Tests/images/exif.png") as im:
            im.save(test_file, exif=im.getexif())

        with Image.open(test_file) as reloaded:
            exif = reloaded._getexif()
        assert exif[274] == 1

    @mark_if_feature_version(
        pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
    )
    def test_exif_from_jpg(self, tmp_path: Path) -> None:
        with Image.open("Tests/images/pil_sample_rgb.jpg") as im:
            test_file = tmp_path / "temp.png"
            im.save(test_file, exif=im.getexif())

        with Image.open(test_file) as reloaded:
            exif = reloaded._getexif()
        assert exif[305] == "Adobe Photoshop CS Macintosh"

    def test_exif_argument(self, tmp_path: Path) -> None:
        with Image.open(TEST_PNG_FILE) as im:
            test_file = tmp_path / "temp.png"
            im.save(test_file, exif=b"exifstring")

        with Image.open(test_file) as reloaded:
            assert reloaded.info["exif"] == b"Exif\x00\x00exifstring"

    def test_tell(self) -> None:
        with Image.open(TEST_PNG_FILE) as im:
            assert im.tell() == 0

    def test_seek(self) -> None:
        with Image.open(TEST_PNG_FILE) as im:
            im.seek(0)

            with pytest.raises(EOFError):
                im.seek(1)

    @pytest.mark.parametrize("buffer", (True, False))
    def test_save_stdout(self, buffer: bool, monkeypatch: pytest.MonkeyPatch) -> None:

        class MyStdOut:
            buffer = BytesIO()

        mystdout: MyStdOut | BytesIO = MyStdOut() if buffer else BytesIO()

        monkeypatch.setattr(sys, "stdout", mystdout)

        with Image.open(TEST_PNG_FILE) as im:
            im.save(sys.stdout, "PNG")

        if isinstance(mystdout, MyStdOut):
            mystdout = mystdout.buffer
        with Image.open(mystdout) as reloaded:
            assert_image_equal_tofile(reloaded, TEST_PNG_FILE)

    def test_truncated_end_chunk(self, monkeypatch: pytest.MonkeyPatch) -> None:
        with Image.open("Tests/images/truncated_end_chunk.png") as im:
            with pytest.raises(OSError):
                im.load()

        monkeypatch.setattr(ImageFile, "LOAD_TRUNCATED_IMAGES", True)
        with Image.open("Tests/images/truncated_end_chunk.png") as im:
            assert_image_equal_tofile(im, "Tests/images/hopper.png")

    def test_deprecation(self, tmp_path: Path) -> None:
        test_file = tmp_path / "out.png"

        im = hopper("I")
        with pytest.warns(DeprecationWarning, match="Saving I mode images as PNG"):
            im.save(test_file)

        with Image.open(test_file) as reloaded:
            assert_image_equal(im, reloaded.convert("I"))


@pytest.mark.skipif(is_win32(), reason="Requires Unix or macOS")
@skip_unless_feature("zlib")
class TestTruncatedPngPLeaks(PillowLeakTestCase):
    mem_limit = 2 * 1024  # max increase in K
    iterations = 100  # Leak is 56k/iteration, this will leak 5.6megs

    def test_leak_load(self, monkeypatch: pytest.MonkeyPatch) -> None:
        with open("Tests/images/hopper.png", "rb") as f:
            DATA = BytesIO(f.read(16 * 1024))

        monkeypatch.setattr(ImageFile, "LOAD_TRUNCATED_IMAGES", True)
        with Image.open(DATA) as im:
            im.load()

        def core() -> None:
            with Image.open(DATA) as im:
                im.load()

        self._test_leak(core)
