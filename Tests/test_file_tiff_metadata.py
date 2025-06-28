from __future__ import annotations

import io
import struct
from pathlib import Path

import pytest

from PIL import Image, TiffImagePlugin, TiffTags
from PIL.TiffImagePlugin import IFDRational

from .helper import assert_deep_equal, hopper

TAG_IDS: dict[str, int] = {
    info.name: info.value
    for info in TiffTags.TAGS_V2.values()
    if info.value is not None
}


def test_rt_metadata(tmp_path: Path) -> None:
    """Test writing arbitrary metadata into the tiff image directory
    Use case is ImageJ private tags, one numeric, one arbitrary
    data.  https://github.com/python-pillow/Pillow/issues/291
    """

    img = hopper()

    # Behaviour change: re #1416
    # Pre ifd rewrite, ImageJMetaData was being written as a string(2),
    # Post ifd rewrite, it's defined as arbitrary bytes(7). It should
    # roundtrip with the actual bytes, rather than stripped text
    # of the premerge tests.
    #
    # For text items, we still have to decode('ascii','replace') because
    # the tiff file format can't take 8 bit bytes in that field.

    base_text_data = "This is some arbitrary metadata for a text field"
    bin_data = base_text_data.encode("ascii") + b" \xff"
    text_data = base_text_data + " " + chr(255)
    reloaded_text_data = base_text_data + " ?"
    float_data = 12.345
    double_data = 67.89
    info = TiffImagePlugin.ImageFileDirectory()

    ImageJMetaData = TAG_IDS["ImageJMetaData"]
    ImageJMetaDataByteCounts = TAG_IDS["ImageJMetaDataByteCounts"]
    ImageDescription = TAG_IDS["ImageDescription"]

    info[ImageJMetaDataByteCounts] = len(bin_data)
    info[ImageJMetaData] = bin_data
    info[TAG_IDS["RollAngle"]] = float_data
    info.tagtype[TAG_IDS["RollAngle"]] = 11
    info[TAG_IDS["YawAngle"]] = double_data
    info.tagtype[TAG_IDS["YawAngle"]] = 12

    info[ImageDescription] = text_data

    f = tmp_path / "temp.tif"

    img.save(f, tiffinfo=info)

    with Image.open(f) as loaded:
        assert isinstance(loaded, TiffImagePlugin.TiffImageFile)
        assert loaded.tag[ImageJMetaDataByteCounts] == (len(bin_data),)
        assert loaded.tag_v2[ImageJMetaDataByteCounts] == (len(bin_data),)

        assert loaded.tag[ImageJMetaData] == bin_data
        assert loaded.tag_v2[ImageJMetaData] == bin_data

        assert loaded.tag[ImageDescription] == (reloaded_text_data,)
        assert loaded.tag_v2[ImageDescription] == reloaded_text_data

        loaded_float = loaded.tag[TAG_IDS["RollAngle"]][0]
        assert round(abs(loaded_float - float_data), 5) == 0
        loaded_double = loaded.tag[TAG_IDS["YawAngle"]][0]
        assert round(abs(loaded_double - double_data), 7) == 0

    # check with 2 element ImageJMetaDataByteCounts, issue #2006

    info[ImageJMetaDataByteCounts] = (8, len(bin_data) - 8)
    img.save(f, tiffinfo=info)
    with Image.open(f) as loaded:
        assert isinstance(loaded, TiffImagePlugin.TiffImageFile)
        assert loaded.tag[ImageJMetaDataByteCounts] == (8, len(bin_data) - 8)
        assert loaded.tag_v2[ImageJMetaDataByteCounts] == (8, len(bin_data) - 8)


def test_read_metadata() -> None:
    with Image.open("Tests/images/hopper_g4.tif") as img:
        assert isinstance(img, TiffImagePlugin.TiffImageFile)
        assert {
            "YResolution": IFDRational(4294967295, 113653537),
            "PlanarConfiguration": 1,
            "BitsPerSample": (1,),
            "ImageLength": 128,
            "Compression": 4,
            "FillOrder": 1,
            "RowsPerStrip": 128,
            "ResolutionUnit": 3,
            "PhotometricInterpretation": 0,
            "PageNumber": (0, 1),
            "XResolution": IFDRational(4294967295, 113653537),
            "ImageWidth": 128,
            "Orientation": 1,
            "StripByteCounts": (1968,),
            "SamplesPerPixel": 1,
            "StripOffsets": (8,),
        } == img.tag_v2.named()

        assert {
            "YResolution": ((4294967295, 113653537),),
            "PlanarConfiguration": (1,),
            "BitsPerSample": (1,),
            "ImageLength": (128,),
            "Compression": (4,),
            "FillOrder": (1,),
            "RowsPerStrip": (128,),
            "ResolutionUnit": (3,),
            "PhotometricInterpretation": (0,),
            "PageNumber": (0, 1),
            "XResolution": ((4294967295, 113653537),),
            "ImageWidth": (128,),
            "Orientation": (1,),
            "StripByteCounts": (1968,),
            "SamplesPerPixel": (1,),
            "StripOffsets": (8,),
        } == img.tag.named()


def test_write_metadata(tmp_path: Path) -> None:
    """Test metadata writing through the python code"""
    with Image.open("Tests/images/hopper.tif") as img:
        assert isinstance(img, TiffImagePlugin.TiffImageFile)
        f = tmp_path / "temp.tiff"
        del img.tag[278]
        img.save(f, tiffinfo=img.tag)

        original = img.tag_v2.named()

    with Image.open(f) as loaded:
        assert isinstance(loaded, TiffImagePlugin.TiffImageFile)
        reloaded = loaded.tag_v2.named()

    ignored = ["StripByteCounts", "RowsPerStrip", "PageNumber", "StripOffsets"]

    for tag, value in reloaded.items():
        if tag in ignored:
            continue
        if isinstance(original[tag], tuple) and isinstance(
            original[tag][0], IFDRational
        ):
            # Need to compare element by element in the tuple,
            # not comparing tuples of object references
            assert_deep_equal(
                original[tag],
                value,
                f"{tag} didn't roundtrip, {original[tag]}, {value}",
            )
        else:
            assert (
                original[tag] == value
            ), f"{tag} didn't roundtrip, {original[tag]}, {value}"

    for tag, value in original.items():
        if tag not in ignored:
            assert value == reloaded[tag], f"{tag} didn't roundtrip"


def test_change_stripbytecounts_tag_type(tmp_path: Path) -> None:
    out = tmp_path / "temp.tiff"
    with Image.open("Tests/images/hopper.tif") as im:
        assert isinstance(im, TiffImagePlugin.TiffImageFile)
        info = im.tag_v2
        del info[278]

        # Resize the image so that STRIPBYTECOUNTS will be larger than a SHORT
        im = im.resize((500, 500))
        info[TiffImagePlugin.IMAGEWIDTH] = im.width

        # STRIPBYTECOUNTS can be a SHORT or a LONG
        info.tagtype[TiffImagePlugin.STRIPBYTECOUNTS] = TiffTags.SHORT

        im.save(out, tiffinfo=info)

    with Image.open(out) as reloaded:
        assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
        assert reloaded.tag_v2.tagtype[TiffImagePlugin.STRIPBYTECOUNTS] == TiffTags.LONG


def test_save_multiple_stripoffsets() -> None:
    ifd = TiffImagePlugin.ImageFileDirectory_v2()
    ifd[TiffImagePlugin.STRIPOFFSETS] = (123, 456)
    assert ifd.tagtype[TiffImagePlugin.STRIPOFFSETS] == TiffTags.LONG

    # all values are in little-endian
    assert ifd.tobytes() == (
        # number of tags == 1
        b"\x01\x00"
        # tag id (2 bytes), type (2 bytes), count (4 bytes), value (4 bytes)
        # TiffImagePlugin.STRIPOFFSETS, TiffTags.LONG, 2, 18
        # where STRIPOFFSETS is 273, LONG is 4
        # and 18 is the offset of the tag data
        b"\x11\x01\x04\x00\x02\x00\x00\x00\x12\x00\x00\x00"
        # end of entries
        b"\x00\x00\x00\x00"
        # 26 is the total number of bytes output,
        # the offset for any auxiliary strip data that will then be appended
        # (123 + 26, 456 + 26) == (149, 482)
        b"\x95\x00\x00\x00\xe2\x01\x00\x00"
    )


def test_no_duplicate_50741_tag() -> None:
    assert TAG_IDS["MakerNoteSafety"] == 50741
    assert TAG_IDS["BestQualityScale"] == 50780


def test_iptc(tmp_path: Path) -> None:
    out = tmp_path / "temp.tiff"
    with Image.open("Tests/images/hopper.Lab.tif") as im:
        im.save(out)


@pytest.mark.parametrize("value, expected", ((b"test", "test"), (1, "1")))
def test_writing_other_types_to_ascii(
    value: bytes | int, expected: str, tmp_path: Path
) -> None:
    info = TiffImagePlugin.ImageFileDirectory_v2()

    tag = TiffTags.TAGS_V2[271]
    assert tag.type == TiffTags.ASCII

    info[271] = value

    im = hopper()
    out = tmp_path / "temp.tiff"
    im.save(out, tiffinfo=info)

    with Image.open(out) as reloaded:
        assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
        assert reloaded.tag_v2[271] == expected


@pytest.mark.parametrize("value", (1, IFDRational(1)))
def test_writing_other_types_to_bytes(value: int | IFDRational, tmp_path: Path) -> None:
    im = hopper()
    info = TiffImagePlugin.ImageFileDirectory_v2()

    tag = TiffTags.TAGS_V2[700]
    assert tag.type == TiffTags.BYTE

    info[700] = value

    out = tmp_path / "temp.tiff"
    im.save(out, tiffinfo=info)

    with Image.open(out) as reloaded:
        assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
        assert reloaded.tag_v2[700] == b"\x01"


@pytest.mark.parametrize("value", (1, IFDRational(1)))
def test_writing_other_types_to_undefined(
    value: int | IFDRational, tmp_path: Path
) -> None:
    im = hopper()
    info = TiffImagePlugin.ImageFileDirectory_v2()

    tag = TiffTags.TAGS_V2[33723]
    assert tag.type == TiffTags.UNDEFINED

    info[33723] = value

    out = tmp_path / "temp.tiff"
    im.save(out, tiffinfo=info)

    with Image.open(out) as reloaded:
        assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
        assert reloaded.tag_v2[33723] == b"1"


def test_undefined_zero(tmp_path: Path) -> None:
    # Check that the tag has not been changed since this test was created
    tag = TiffTags.TAGS_V2[45059]
    assert tag.type == TiffTags.UNDEFINED
    assert tag.length == 0

    info = TiffImagePlugin.ImageFileDirectory(b"II*\x00\x08\x00\x00\x00")
    info[45059] = b"test"

    # Assert that the tag value does not change by setting it to itself
    original = info[45059]
    info[45059] = info[45059]
    assert info[45059] == original


def test_empty_metadata() -> None:
    f = io.BytesIO(b"II*\x00\x08\x00\x00\x00")
    head = f.read(8)
    info = TiffImagePlugin.ImageFileDirectory(head)
    # Should not raise struct.error.
    with pytest.warns(UserWarning, match="Corrupt EXIF data"):
        info.load(f)


def test_iccprofile(tmp_path: Path) -> None:
    # https://github.com/python-pillow/Pillow/issues/1462
    out = tmp_path / "temp.tiff"
    with Image.open("Tests/images/hopper.iccprofile.tif") as im:
        im.save(out)

    with Image.open(out) as reloaded:
        assert not isinstance(im.info["icc_profile"], tuple)
        assert im.info["icc_profile"] == reloaded.info["icc_profile"]


def test_iccprofile_binary() -> None:
    # https://github.com/python-pillow/Pillow/issues/1526
    # We should be able to load this,
    # but probably won't be able to save it.

    with Image.open("Tests/images/hopper.iccprofile_binary.tif") as im:
        assert isinstance(im, TiffImagePlugin.TiffImageFile)
        assert im.tag_v2.tagtype[34675] == 1
        assert im.info["icc_profile"]


def test_iccprofile_save_png(tmp_path: Path) -> None:
    with Image.open("Tests/images/hopper.iccprofile.tif") as im:
        outfile = tmp_path / "temp.png"
        im.save(outfile)


def test_iccprofile_binary_save_png(tmp_path: Path) -> None:
    with Image.open("Tests/images/hopper.iccprofile_binary.tif") as im:
        outfile = tmp_path / "temp.png"
        im.save(outfile)


def test_exif_div_zero(tmp_path: Path) -> None:
    im = hopper()
    info = TiffImagePlugin.ImageFileDirectory_v2()
    info[41988] = TiffImagePlugin.IFDRational(0, 0)

    out = tmp_path / "temp.tiff"
    im.save(out, tiffinfo=info, compression="raw")

    with Image.open(out) as reloaded:
        assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
        assert 0 == reloaded.tag_v2[41988].numerator
        assert 0 == reloaded.tag_v2[41988].denominator


def test_ifd_unsigned_rational(tmp_path: Path) -> None:
    im = hopper()
    info = TiffImagePlugin.ImageFileDirectory_v2()

    max_long = 2**32 - 1

    # 4 bytes unsigned long
    numerator = max_long

    info[41493] = TiffImagePlugin.IFDRational(numerator, 1)

    out = tmp_path / "temp.tiff"
    im.save(out, tiffinfo=info, compression="raw")

    with Image.open(out) as reloaded:
        assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
        assert max_long == reloaded.tag_v2[41493].numerator
        assert 1 == reloaded.tag_v2[41493].denominator

    # out of bounds of 4 byte unsigned long
    numerator = max_long + 1

    info[41493] = TiffImagePlugin.IFDRational(numerator, 1)

    out = tmp_path / "temp.tiff"
    im.save(out, tiffinfo=info, compression="raw")

    with Image.open(out) as reloaded:
        assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
        assert max_long == reloaded.tag_v2[41493].numerator
        assert 1 == reloaded.tag_v2[41493].denominator


def test_ifd_signed_rational(tmp_path: Path) -> None:
    im = hopper()
    info = TiffImagePlugin.ImageFileDirectory_v2()

    # pair of 4 byte signed longs
    numerator = 2**31 - 1
    denominator = -(2**31)

    info[37380] = TiffImagePlugin.IFDRational(numerator, denominator)

    out = tmp_path / "temp.tiff"
    im.save(out, tiffinfo=info, compression="raw")

    with Image.open(out) as reloaded:
        assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
        assert numerator == reloaded.tag_v2[37380].numerator
        assert denominator == reloaded.tag_v2[37380].denominator

    numerator = -(2**31)
    denominator = 2**31 - 1

    info[37380] = TiffImagePlugin.IFDRational(numerator, denominator)

    out = tmp_path / "temp.tiff"
    im.save(out, tiffinfo=info, compression="raw")

    with Image.open(out) as reloaded:
        assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
        assert numerator == reloaded.tag_v2[37380].numerator
        assert denominator == reloaded.tag_v2[37380].denominator

    # out of bounds of 4 byte signed long
    numerator = -(2**31) - 1
    denominator = 1

    info[37380] = TiffImagePlugin.IFDRational(numerator, denominator)

    out = tmp_path / "temp.tiff"
    im.save(out, tiffinfo=info, compression="raw")

    with Image.open(out) as reloaded:
        assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
        assert 2**31 - 1 == reloaded.tag_v2[37380].numerator
        assert -1 == reloaded.tag_v2[37380].denominator


def test_ifd_signed_long(tmp_path: Path) -> None:
    im = hopper()
    info = TiffImagePlugin.ImageFileDirectory_v2()

    info[37000] = -60000

    out = tmp_path / "temp.tiff"
    im.save(out, tiffinfo=info, compression="raw")

    with Image.open(out) as reloaded:
        assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
        assert reloaded.tag_v2[37000] == -60000


def test_empty_values() -> None:
    data = io.BytesIO(
        b"II*\x00\x08\x00\x00\x00\x03\x00\x1a\x01\x05\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x1b\x01\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x98\x82\x02\x00\x07\x00\x00\x002\x00\x00\x00\x00\x00\x00\x00a "
        b"text\x00\x00"
    )
    head = data.read(8)
    info = TiffImagePlugin.ImageFileDirectory_v2(head)
    info.load(data)
    # Should not raise ValueError.
    info_dict = dict(info)
    assert 33432 in info_dict


def test_photoshop_info(tmp_path: Path) -> None:
    with Image.open("Tests/images/issue_2278.tif") as im:
        assert isinstance(im, TiffImagePlugin.TiffImageFile)
        assert len(im.tag_v2[34377]) == 70
        assert isinstance(im.tag_v2[34377], bytes)
        out = tmp_path / "temp.tiff"
        im.save(out)
    with Image.open(out) as reloaded:
        assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
        assert len(reloaded.tag_v2[34377]) == 70
        assert isinstance(reloaded.tag_v2[34377], bytes)


def test_too_many_entries() -> None:
    ifd = TiffImagePlugin.ImageFileDirectory_v2()

    #    277: ("SamplesPerPixel", SHORT, 1),
    ifd._tagdata[277] = struct.pack("<hh", 4, 4)
    ifd.tagtype[277] = TiffTags.SHORT

    # Should not raise ValueError.
    with pytest.warns(UserWarning, match="Metadata Warning"):
        assert ifd[277] == 4


def test_tag_group_data() -> None:
    base_ifd = TiffImagePlugin.ImageFileDirectory_v2()
    interop_ifd = TiffImagePlugin.ImageFileDirectory_v2(group=40965)
    for ifd in (base_ifd, interop_ifd):
        ifd[2] = "test"
        ifd[256] = 10

    assert base_ifd.tagtype[256] == 4
    assert interop_ifd.tagtype[256] != base_ifd.tagtype[256]

    assert interop_ifd.tagtype[2] == 7
    assert base_ifd.tagtype[2] != interop_ifd.tagtype[256]


def test_empty_subifd(tmp_path: Path) -> None:
    out = tmp_path / "temp.jpg"

    im = hopper()
    exif = im.getexif()
    exif[TiffImagePlugin.EXIFIFD] = {}
    im.save(out, exif=exif)

    with Image.open(out) as reloaded:
        exif = reloaded.getexif()
        assert exif.get_ifd(TiffImagePlugin.EXIFIFD) == {}
