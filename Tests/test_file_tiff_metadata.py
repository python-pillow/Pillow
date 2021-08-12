import io
import struct

import pytest

from PIL import Image, TiffImagePlugin, TiffTags
from PIL.TiffImagePlugin import IFDRational

from .helper import assert_deep_equal, hopper

TAG_IDS = {info.name: info.value for info in TiffTags.TAGS_V2.values()}


def test_rt_metadata(tmp_path):
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

    basetextdata = "This is some arbitrary metadata for a text field"
    bindata = basetextdata.encode("ascii") + b" \xff"
    textdata = basetextdata + " " + chr(255)
    reloaded_textdata = basetextdata + " ?"
    floatdata = 12.345
    doubledata = 67.89
    info = TiffImagePlugin.ImageFileDirectory()

    ImageJMetaData = TAG_IDS["ImageJMetaData"]
    ImageJMetaDataByteCounts = TAG_IDS["ImageJMetaDataByteCounts"]
    ImageDescription = TAG_IDS["ImageDescription"]

    info[ImageJMetaDataByteCounts] = len(bindata)
    info[ImageJMetaData] = bindata
    info[TAG_IDS["RollAngle"]] = floatdata
    info.tagtype[TAG_IDS["RollAngle"]] = 11
    info[TAG_IDS["YawAngle"]] = doubledata
    info.tagtype[TAG_IDS["YawAngle"]] = 12

    info[ImageDescription] = textdata

    f = str(tmp_path / "temp.tif")

    img.save(f, tiffinfo=info)

    with Image.open(f) as loaded:

        assert loaded.tag[ImageJMetaDataByteCounts] == (len(bindata),)
        assert loaded.tag_v2[ImageJMetaDataByteCounts] == (len(bindata),)

        assert loaded.tag[ImageJMetaData] == bindata
        assert loaded.tag_v2[ImageJMetaData] == bindata

        assert loaded.tag[ImageDescription] == (reloaded_textdata,)
        assert loaded.tag_v2[ImageDescription] == reloaded_textdata

        loaded_float = loaded.tag[TAG_IDS["RollAngle"]][0]
        assert round(abs(loaded_float - floatdata), 5) == 0
        loaded_double = loaded.tag[TAG_IDS["YawAngle"]][0]
        assert round(abs(loaded_double - doubledata), 7) == 0

    # check with 2 element ImageJMetaDataByteCounts, issue #2006

    info[ImageJMetaDataByteCounts] = (8, len(bindata) - 8)
    img.save(f, tiffinfo=info)
    with Image.open(f) as loaded:

        assert loaded.tag[ImageJMetaDataByteCounts] == (8, len(bindata) - 8)
        assert loaded.tag_v2[ImageJMetaDataByteCounts] == (8, len(bindata) - 8)


def test_read_metadata():
    with Image.open("Tests/images/hopper_g4.tif") as img:

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


def test_write_metadata(tmp_path):
    """Test metadata writing through the python code"""
    with Image.open("Tests/images/hopper.tif") as img:
        f = str(tmp_path / "temp.tiff")
        img.save(f, tiffinfo=img.tag)

        original = img.tag_v2.named()

    with Image.open(f) as loaded:
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


def test_change_stripbytecounts_tag_type(tmp_path):
    out = str(tmp_path / "temp.tiff")
    with Image.open("Tests/images/hopper.tif") as im:
        info = im.tag_v2

        # Resize the image so that STRIPBYTECOUNTS will be larger than a SHORT
        im = im.resize((500, 500))

        # STRIPBYTECOUNTS can be a SHORT or a LONG
        info.tagtype[TiffImagePlugin.STRIPBYTECOUNTS] = TiffTags.SHORT

        im.save(out, tiffinfo=info)

    with Image.open(out) as reloaded:
        assert reloaded.tag_v2.tagtype[TiffImagePlugin.STRIPBYTECOUNTS] == TiffTags.LONG


def test_no_duplicate_50741_tag():
    assert TAG_IDS["MakerNoteSafety"] == 50741
    assert TAG_IDS["BestQualityScale"] == 50780


def test_iptc(tmp_path):
    out = str(tmp_path / "temp.tiff")
    with Image.open("Tests/images/hopper.Lab.tif") as im:
        im.save(out)


def test_undefined_zero(tmp_path):
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


def test_empty_metadata():
    f = io.BytesIO(b"II*\x00\x08\x00\x00\x00")
    head = f.read(8)
    info = TiffImagePlugin.ImageFileDirectory(head)
    # Should not raise struct.error.
    pytest.warns(UserWarning, info.load, f)


def test_iccprofile(tmp_path):
    # https://github.com/python-pillow/Pillow/issues/1462
    out = str(tmp_path / "temp.tiff")
    with Image.open("Tests/images/hopper.iccprofile.tif") as im:
        im.save(out)

    with Image.open(out) as reloaded:
        assert not isinstance(im.info["icc_profile"], tuple)
        assert im.info["icc_profile"] == reloaded.info["icc_profile"]


def test_iccprofile_binary():
    # https://github.com/python-pillow/Pillow/issues/1526
    # We should be able to load this,
    # but probably won't be able to save it.

    with Image.open("Tests/images/hopper.iccprofile_binary.tif") as im:
        assert im.tag_v2.tagtype[34675] == 1
        assert im.info["icc_profile"]


def test_iccprofile_save_png(tmp_path):
    with Image.open("Tests/images/hopper.iccprofile.tif") as im:
        outfile = str(tmp_path / "temp.png")
        im.save(outfile)


def test_iccprofile_binary_save_png(tmp_path):
    with Image.open("Tests/images/hopper.iccprofile_binary.tif") as im:
        outfile = str(tmp_path / "temp.png")
        im.save(outfile)


def test_exif_div_zero(tmp_path):
    im = hopper()
    info = TiffImagePlugin.ImageFileDirectory_v2()
    info[41988] = TiffImagePlugin.IFDRational(0, 0)

    out = str(tmp_path / "temp.tiff")
    im.save(out, tiffinfo=info, compression="raw")

    with Image.open(out) as reloaded:
        assert 0 == reloaded.tag_v2[41988].numerator
        assert 0 == reloaded.tag_v2[41988].denominator


def test_ifd_unsigned_rational(tmp_path):
    im = hopper()
    info = TiffImagePlugin.ImageFileDirectory_v2()

    max_long = 2 ** 32 - 1

    # 4 bytes unsigned long
    numerator = max_long

    info[41493] = TiffImagePlugin.IFDRational(numerator, 1)

    out = str(tmp_path / "temp.tiff")
    im.save(out, tiffinfo=info, compression="raw")

    with Image.open(out) as reloaded:
        assert max_long == reloaded.tag_v2[41493].numerator
        assert 1 == reloaded.tag_v2[41493].denominator

    # out of bounds of 4 byte unsigned long
    numerator = max_long + 1

    info[41493] = TiffImagePlugin.IFDRational(numerator, 1)

    out = str(tmp_path / "temp.tiff")
    im.save(out, tiffinfo=info, compression="raw")

    with Image.open(out) as reloaded:
        assert max_long == reloaded.tag_v2[41493].numerator
        assert 1 == reloaded.tag_v2[41493].denominator


def test_ifd_signed_rational(tmp_path):
    im = hopper()
    info = TiffImagePlugin.ImageFileDirectory_v2()

    # pair of 4 byte signed longs
    numerator = 2 ** 31 - 1
    denominator = -(2 ** 31)

    info[37380] = TiffImagePlugin.IFDRational(numerator, denominator)

    out = str(tmp_path / "temp.tiff")
    im.save(out, tiffinfo=info, compression="raw")

    with Image.open(out) as reloaded:
        assert numerator == reloaded.tag_v2[37380].numerator
        assert denominator == reloaded.tag_v2[37380].denominator

    numerator = -(2 ** 31)
    denominator = 2 ** 31 - 1

    info[37380] = TiffImagePlugin.IFDRational(numerator, denominator)

    out = str(tmp_path / "temp.tiff")
    im.save(out, tiffinfo=info, compression="raw")

    with Image.open(out) as reloaded:
        assert numerator == reloaded.tag_v2[37380].numerator
        assert denominator == reloaded.tag_v2[37380].denominator

    # out of bounds of 4 byte signed long
    numerator = -(2 ** 31) - 1
    denominator = 1

    info[37380] = TiffImagePlugin.IFDRational(numerator, denominator)

    out = str(tmp_path / "temp.tiff")
    im.save(out, tiffinfo=info, compression="raw")

    with Image.open(out) as reloaded:
        assert 2 ** 31 - 1 == reloaded.tag_v2[37380].numerator
        assert -1 == reloaded.tag_v2[37380].denominator


def test_ifd_signed_long(tmp_path):
    im = hopper()
    info = TiffImagePlugin.ImageFileDirectory_v2()

    info[37000] = -60000

    out = str(tmp_path / "temp.tiff")
    im.save(out, tiffinfo=info, compression="raw")

    with Image.open(out) as reloaded:
        assert reloaded.tag_v2[37000] == -60000


def test_empty_values():
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
    info = dict(info)
    assert 33432 in info


def test_PhotoshopInfo(tmp_path):
    with Image.open("Tests/images/issue_2278.tif") as im:
        assert len(im.tag_v2[34377]) == 70
        assert isinstance(im.tag_v2[34377], bytes)
        out = str(tmp_path / "temp.tiff")
        im.save(out)
    with Image.open(out) as reloaded:
        assert len(reloaded.tag_v2[34377]) == 70
        assert isinstance(reloaded.tag_v2[34377], bytes)


def test_too_many_entries():
    ifd = TiffImagePlugin.ImageFileDirectory_v2()

    #    277: ("SamplesPerPixel", SHORT, 1),
    ifd._tagdata[277] = struct.pack("hh", 4, 4)
    ifd.tagtype[277] = TiffTags.SHORT

    # Should not raise ValueError.
    pytest.warns(UserWarning, lambda: ifd[277])


def test_tag_group_data():
    base_ifd = TiffImagePlugin.ImageFileDirectory_v2()
    interop_ifd = TiffImagePlugin.ImageFileDirectory_v2(group=40965)
    for ifd in (base_ifd, interop_ifd):
        ifd[2] = "test"
        ifd[256] = 10

    assert base_ifd.tagtype[256] == 4
    assert interop_ifd.tagtype[256] != base_ifd.tagtype[256]

    assert interop_ifd.tagtype[2] == 7
    assert base_ifd.tagtype[2] != interop_ifd.tagtype[256]


def test_empty_subifd(tmp_path):
    out = str(tmp_path / "temp.jpg")

    im = hopper()
    exif = im.getexif()
    exif[TiffImagePlugin.EXIFIFD] = {}
    im.save(out, exif=exif)

    with Image.open(out) as reloaded:
        exif = reloaded.getexif()
        assert exif.get_ifd(TiffImagePlugin.EXIFIFD) == {}
