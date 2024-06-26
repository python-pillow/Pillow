from __future__ import annotations

import datetime
import os
import re
import shutil
import sys
from io import BytesIO
from pathlib import Path
from typing import Any, Literal, cast

import pytest

from PIL import Image, ImageMode, ImageWin, features

from .helper import (
    assert_image,
    assert_image_equal,
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
    is_pypy,
)

try:
    from PIL import ImageCms
    from PIL.ImageCms import ImageCmsProfile

    ImageCms.core.profile_open
except ImportError:
    # Skipped via setup_module()
    pass


SRGB = "Tests/icc/sRGB_IEC61966-2-1_black_scaled.icc"
HAVE_PROFILE = os.path.exists(SRGB)


def setup_module() -> None:
    try:
        from PIL import ImageCms
        # need to hit getattr to trigger the delayed import error
        ImageCms.core.profile_open
    except ImportError as v:
        pytest.skip(str(v))


def skip_missing() -> None:
    if not HAVE_PROFILE:
        pytest.skip("SRGB profile not available")


def test_sanity() -> None:
    # basic smoke test.
    # this mostly follows the cms_test outline.
    with pytest.warns(DeprecationWarning):
        v = ImageCms.versions()  # should return four strings
    assert v[0] == "1.0.0 pil"
    assert list(map(type, v)) == [str, str, str, str]

    # internal version number
    version = features.version_module("littlecms2")
    assert version is not None
    assert re.search(r"\d+\.\d+(\.\d+)?$", version)

    skip_missing()
    i = ImageCms.profileToProfile(hopper(), SRGB, SRGB)
    assert i is not None
    assert_image(i, "RGB", (128, 128))

    i = hopper()
    ImageCms.profileToProfile(i, SRGB, SRGB, inPlace=True)
    assert_image(i, "RGB", (128, 128))

    t = ImageCms.buildTransform(SRGB, SRGB, "RGB", "RGB")
    i = ImageCms.applyTransform(hopper(), t)
    assert i is not None
    assert_image(i, "RGB", (128, 128))

    with hopper() as i:
        t = ImageCms.buildTransform(SRGB, SRGB, "RGB", "RGB")
        ImageCms.applyTransform(hopper(), t, inPlace=True)
        assert i is not None
        assert_image(i, "RGB", (128, 128))

    p = ImageCms.createProfile("sRGB")
    o = ImageCms.getOpenProfile(SRGB)
    t = ImageCms.buildTransformFromOpenProfiles(p, o, "RGB", "RGB")
    i = ImageCms.applyTransform(hopper(), t)
    assert i is not None
    assert_image(i, "RGB", (128, 128))

    t = ImageCms.buildProofTransform(SRGB, SRGB, SRGB, "RGB", "RGB")
    assert t.inputMode == "RGB"
    assert t.outputMode == "RGB"
    i = ImageCms.applyTransform(hopper(), t)
    assert i is not None
    assert_image(i, "RGB", (128, 128))

    # test PointTransform convenience API
    hopper().point(t)


def test_flags() -> None:
    assert ImageCms.Flags.NONE == 0
    assert ImageCms.Flags.GRIDPOINTS(0) == ImageCms.Flags.NONE
    assert ImageCms.Flags.GRIDPOINTS(256) == ImageCms.Flags.NONE

    assert ImageCms.Flags.GRIDPOINTS(255) == (255 << 16)
    assert ImageCms.Flags.GRIDPOINTS(-1) == ImageCms.Flags.GRIDPOINTS(255)
    assert ImageCms.Flags.GRIDPOINTS(511) == ImageCms.Flags.GRIDPOINTS(255)


def test_name() -> None:
    skip_missing()
    # get profile information for file
    assert (
        ImageCms.getProfileName(SRGB).strip()
        == "IEC 61966-2-1 Default RGB Colour Space - sRGB"
    )


def test_info() -> None:
    skip_missing()
    assert ImageCms.getProfileInfo(SRGB).splitlines() == [
        "sRGB IEC61966-2-1 black scaled",
        "",
        "Copyright International Color Consortium, 2009",
        "",
    ]


def test_copyright() -> None:
    skip_missing()
    assert (
        ImageCms.getProfileCopyright(SRGB).strip()
        == "Copyright International Color Consortium, 2009"
    )


def test_manufacturer() -> None:
    skip_missing()
    assert ImageCms.getProfileManufacturer(SRGB).strip() == ""


def test_model() -> None:
    skip_missing()
    assert (
        ImageCms.getProfileModel(SRGB).strip()
        == "IEC 61966-2-1 Default RGB Colour Space - sRGB"
    )


def test_description() -> None:
    skip_missing()
    assert (
        ImageCms.getProfileDescription(SRGB).strip() == "sRGB IEC61966-2-1 black scaled"
    )


def test_intent() -> None:
    skip_missing()
    assert ImageCms.getDefaultIntent(SRGB) == 0
    support = ImageCms.isIntentSupported(
        SRGB, ImageCms.Intent.ABSOLUTE_COLORIMETRIC, ImageCms.Direction.INPUT
    )
    assert support == 1


def test_profile_object() -> None:
    # same, using profile object
    p = ImageCms.createProfile("sRGB")
    # assert ImageCms.getProfileName(p).strip() == "sRGB built-in - (lcms internal)"
    # assert ImageCms.getProfileInfo(p).splitlines() ==
    #     ["sRGB built-in", "", "WhitePoint : D65 (daylight)", "", ""]
    assert ImageCms.getDefaultIntent(p) == 0
    support = ImageCms.isIntentSupported(
        p, ImageCms.Intent.ABSOLUTE_COLORIMETRIC, ImageCms.Direction.INPUT
    )
    assert support == 1


def test_extensions() -> None:
    # extensions

    with Image.open("Tests/images/rgb.jpg") as i:
        p = ImageCms.getOpenProfile(BytesIO(i.info["icc_profile"]))
    assert (
        ImageCms.getProfileName(p).strip()
        == "IEC 61966-2.1 Default RGB colour space - sRGB"
    )


def test_exceptions() -> None:
    # Test mode mismatch
    psRGB = ImageCms.createProfile("sRGB")
    pLab = ImageCms.createProfile("LAB")
    t = ImageCms.buildTransform(pLab, psRGB, "LAB", "RGB")
    with pytest.raises(ValueError, match="mode mismatch"):
        t.apply_in_place(hopper("RGBA"))

    # the procedural pyCMS API uses PyCMSError for all sorts of errors
    with hopper() as im:
        with pytest.raises(ImageCms.PyCMSError, match="cannot open profile file"):
            ImageCms.profileToProfile(im, "foo", "bar")

    with pytest.raises(ImageCms.PyCMSError, match="cannot open profile file"):
        ImageCms.buildTransform("foo", "bar", "RGB", "RGB")

    with pytest.raises(ImageCms.PyCMSError, match="Invalid type for Profile"):
        ImageCms.getProfileName(None)  # type: ignore[arg-type]
    skip_missing()

    # Python <= 3.9: "an integer is required (got type NoneType)"
    # Python > 3.9: "'NoneType' object cannot be interpreted as an integer"
    with pytest.raises(ImageCms.PyCMSError, match="integer"):
        ImageCms.isIntentSupported(SRGB, None, None)  # type: ignore[arg-type]


def test_display_profile() -> None:
    # try fetching the profile for the current display device
    ImageCms.get_display_profile()

    if sys.platform == "win32":
        ImageCms.get_display_profile(ImageWin.HDC(0))
        ImageCms.get_display_profile(ImageWin.HWND(0))


def test_lab_color_profile() -> None:
    ImageCms.createProfile("LAB", 5000)
    ImageCms.createProfile("LAB", 6500)


def test_unsupported_color_space() -> None:
    with pytest.raises(
        ImageCms.PyCMSError,
        match=re.escape(
            "Color space not supported for on-the-fly profile creation (unsupported)"
        ),
    ):
        ImageCms.createProfile("unsupported")  # type: ignore[arg-type]


def test_invalid_color_temperature() -> None:
    with pytest.raises(
        ImageCms.PyCMSError,
        match='Color temperature must be numeric, "invalid" not valid',
    ):
        ImageCms.createProfile("LAB", "invalid")  # type: ignore[arg-type]


@pytest.mark.parametrize("flag", ("my string", -1))
def test_invalid_flag(flag: str | int) -> None:
    with hopper() as im:
        with pytest.raises(
            ImageCms.PyCMSError, match="flags must be an integer between 0 and "
        ):
            ImageCms.profileToProfile(im, "foo", "bar", flags=flag)  # type: ignore[arg-type]


def test_simple_lab() -> None:
    i = Image.new("RGB", (10, 10), (128, 128, 128))

    psRGB = ImageCms.createProfile("sRGB")
    pLab = ImageCms.createProfile("LAB")
    t = ImageCms.buildTransform(psRGB, pLab, "RGB", "LAB")

    i_lab = ImageCms.applyTransform(i, t)
    assert i_lab is not None
    assert i_lab.mode == "LAB"

    k = i_lab.getpixel((0, 0))
    # not a linear luminance map. so L != 128:
    assert k == (137, 128, 128)

    l_data = i_lab.getdata(0)
    a_data = i_lab.getdata(1)
    b_data = i_lab.getdata(2)

    assert list(l_data) == [137] * 100
    assert list(a_data) == [128] * 100
    assert list(b_data) == [128] * 100


def test_lab_color() -> None:
    psRGB = ImageCms.createProfile("sRGB")
    pLab = ImageCms.createProfile("LAB")
    t = ImageCms.buildTransform(psRGB, pLab, "RGB", "LAB")

    # Need to add a type mapping for some PIL type to TYPE_Lab_8 in findLCMSType, and
    # have that mapping work back to a PIL mode (likely RGB).
    i = ImageCms.applyTransform(hopper(), t)
    assert i is not None
    assert_image(i, "LAB", (128, 128))

    # i.save('temp.lab.tif')  # visually verified vs PS.

    assert_image_similar_tofile(i, "Tests/images/hopper.Lab.tif", 3.5)


def test_lab_srgb() -> None:
    psRGB = ImageCms.createProfile("sRGB")
    pLab = ImageCms.createProfile("LAB")
    t = ImageCms.buildTransform(pLab, psRGB, "LAB", "RGB")

    with Image.open("Tests/images/hopper.Lab.tif") as img:
        img_srgb = ImageCms.applyTransform(img, t)
    assert img_srgb is not None

    # img_srgb.save('temp.srgb.tif') # visually verified vs ps.

    assert_image_similar(hopper(), img_srgb, 30)
    assert img_srgb.info["icc_profile"]

    profile = ImageCmsProfile(BytesIO(img_srgb.info["icc_profile"]))
    assert "sRGB" in ImageCms.getProfileDescription(profile)


def test_lab_roundtrip() -> None:
    # check to see if we're at least internally consistent.
    psRGB = ImageCms.createProfile("sRGB")
    pLab = ImageCms.createProfile("LAB")
    t = ImageCms.buildTransform(psRGB, pLab, "RGB", "LAB")

    t2 = ImageCms.buildTransform(pLab, psRGB, "LAB", "RGB")

    i = ImageCms.applyTransform(hopper(), t)
    assert i is not None
    assert i.info["icc_profile"] == ImageCmsProfile(pLab).tobytes()

    out = ImageCms.applyTransform(i, t2)
    assert out is not None
    assert_image_similar(hopper(), out, 2)


def test_profile_tobytes() -> None:
    with Image.open("Tests/images/rgb.jpg") as i:
        p = ImageCms.getOpenProfile(BytesIO(i.info["icc_profile"]))

    p2 = ImageCms.getOpenProfile(BytesIO(p.tobytes()))

    # not the same bytes as the original icc_profile, but it does roundtrip
    assert p.tobytes() == p2.tobytes()
    assert ImageCms.getProfileName(p) == ImageCms.getProfileName(p2)
    assert ImageCms.getProfileDescription(p) == ImageCms.getProfileDescription(p2)


def test_extended_information() -> None:
    skip_missing()
    o = ImageCms.getOpenProfile(SRGB)
    p = o.profile

    def assert_truncated_tuple_equal(
        tup1: tuple[Any, ...] | None, tup2: tuple[Any, ...], digits: int = 10
    ) -> None:
        # Helper function to reduce precision of tuples of floats
        # recursively and then check equality.
        power = 10**digits

        def truncate_tuple(tuple_value: tuple[Any, ...]) -> tuple[Any, ...]:
            return tuple(
                (
                    truncate_tuple(val)
                    if isinstance(val, tuple)
                    else int(val * power) / power
                )
                for val in tuple_value
            )

        assert tup1 is not None
        assert truncate_tuple(tup1) == truncate_tuple(tup2)

    assert p.attributes == 4294967296
    assert_truncated_tuple_equal(
        p.blue_colorant,
        (
            (0.14306640625, 0.06060791015625, 0.7140960693359375),
            (0.1558847490315394, 0.06603820639433387, 0.06060791015625),
        ),
    )
    assert_truncated_tuple_equal(
        p.blue_primary,
        (
            (0.14306641366715667, 0.06060790921083026, 0.7140960805782015),
            (0.15588475410450106, 0.06603820408959558, 0.06060790921083026),
        ),
    )
    assert_truncated_tuple_equal(
        p.chromatic_adaptation,
        (
            (
                (1.04791259765625, 0.0229339599609375, -0.050201416015625),
                (0.02960205078125, 0.9904632568359375, -0.0170745849609375),
                (-0.009246826171875, 0.0150604248046875, 0.7517852783203125),
            ),
            (
                (1.0267159024652783, 0.022470062342089134, 0.0229339599609375),
                (0.02951378324103937, 0.9875098886387147, 0.9904632568359375),
                (-0.012205438066465256, 0.01987915407854985, 0.0150604248046875),
            ),
        ),
    )
    assert p.chromaticity is None
    assert p.clut == {
        0: (False, False, True),
        1: (False, False, True),
        2: (False, False, True),
        3: (False, False, True),
    }

    assert p.colorant_table is None
    assert p.colorant_table_out is None
    assert p.colorimetric_intent is None
    assert p.connection_space == "XYZ "
    assert p.copyright == "Copyright International Color Consortium, 2009"
    assert p.creation_date == datetime.datetime(2009, 2, 27, 21, 36, 31)
    assert p.device_class == "mntr"
    assert_truncated_tuple_equal(
        p.green_colorant,
        (
            (0.3851470947265625, 0.7168731689453125, 0.097076416015625),
            (0.32119769927720654, 0.5978443449048152, 0.7168731689453125),
        ),
    )
    assert_truncated_tuple_equal(
        p.green_primary,
        (
            (0.3851470888162112, 0.7168731974161346, 0.09707641738998518),
            (0.32119768793686687, 0.5978443567149709, 0.7168731974161346),
        ),
    )
    assert p.header_flags == 0
    assert p.header_manufacturer == "\x00\x00\x00\x00"
    assert p.header_model == "\x00\x00\x00\x00"
    assert p.icc_measurement_condition == {
        "backing": (0.0, 0.0, 0.0),
        "flare": 0.0,
        "geo": "unknown",
        "observer": 1,
        "illuminant_type": "D65",
    }
    assert p.icc_version == 33554432
    assert p.icc_viewing_condition is None
    assert p.intent_supported == {
        0: (True, True, True),
        1: (True, True, True),
        2: (True, True, True),
        3: (True, True, True),
    }
    assert p.is_matrix_shaper
    assert p.luminance == ((0.0, 80.0, 0.0), (0.0, 1.0, 80.0))
    assert p.manufacturer is None
    assert_truncated_tuple_equal(
        p.media_black_point,
        (
            (0.012054443359375, 0.0124969482421875, 0.01031494140625),
            (0.34573304157549234, 0.35842450765864337, 0.0124969482421875),
        ),
    )
    assert_truncated_tuple_equal(
        p.media_white_point,
        (
            (0.964202880859375, 1.0, 0.8249053955078125),
            (0.3457029219802284, 0.3585375327567059, 1.0),
        ),
    )
    assert_truncated_tuple_equal(
        (p.media_white_point_temperature,), (5000.722328847392,)
    )
    assert p.model == "IEC 61966-2-1 Default RGB Colour Space - sRGB"

    assert p.perceptual_rendering_intent_gamut is None

    assert p.profile_description == "sRGB IEC61966-2-1 black scaled"
    assert p.profile_id == b")\xf8=\xde\xaf\xf2U\xaexB\xfa\xe4\xca\x839\r"
    assert_truncated_tuple_equal(
        p.red_colorant,
        (
            (0.436065673828125, 0.2224884033203125, 0.013916015625),
            (0.6484536316398539, 0.3308524880306778, 0.2224884033203125),
        ),
    )
    assert_truncated_tuple_equal(
        p.red_primary,
        (
            (0.43606566581047446, 0.22248840582960838, 0.013916015621759925),
            (0.6484536250319214, 0.3308524944738204, 0.22248840582960838),
        ),
    )
    assert p.rendering_intent == 0
    assert p.saturation_rendering_intent_gamut is None
    assert p.screening_description is None
    assert p.target is None
    assert p.technology == "CRT "
    assert p.version == 2.0
    assert p.viewing_condition == "Reference Viewing Condition in IEC 61966-2-1"
    assert p.xcolor_space == "RGB "


def test_non_ascii_path(tmp_path: Path) -> None:
    skip_missing()
    tempfile = str(tmp_path / ("temp_" + chr(128) + ".icc"))
    try:
        shutil.copy(SRGB, tempfile)
    except UnicodeEncodeError:
        pytest.skip("Non-ASCII path could not be created")

    o = ImageCms.getOpenProfile(tempfile)
    p = o.profile
    assert p.model == "IEC 61966-2-1 Default RGB Colour Space - sRGB"


def test_profile_typesafety() -> None:
    # does not segfault
    with pytest.raises(TypeError, match="Invalid type for Profile"):
        ImageCms.ImageCmsProfile(0)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="Invalid type for Profile"):
        ImageCms.ImageCmsProfile(1)  # type: ignore[arg-type]

    # also check core function
    with pytest.raises(TypeError):
        ImageCms.core.profile_tobytes(0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        ImageCms.core.profile_tobytes(1)  # type: ignore[arg-type]

    if not is_pypy():
        # core profile should not be directly instantiable
        with pytest.raises(TypeError):
            ImageCms.core.CmsProfile()
        with pytest.raises(TypeError):
            ImageCms.core.CmsProfile(0)  # type: ignore[call-arg]


@pytest.mark.skipif(is_pypy(), reason="fails on PyPy")
def test_transform_typesafety() -> None:
    # core transform should not be directly instantiable
    with pytest.raises(TypeError):
        ImageCms.core.CmsTransform()
    with pytest.raises(TypeError):
        ImageCms.core.CmsTransform(0)  # type: ignore[call-arg]


def assert_aux_channel_preserved(
    mode: str, transform_in_place: bool, preserved_channel: str
) -> None:
    def create_test_image() -> Image.Image:
        # set up test image with something interesting in the tested aux channel.
        # fmt: off
        nine_grid_deltas = [
            (-1, -1), (-1, 0), (-1, 1),
            (0,  -1),  (0, 0),  (0, 1),
            (1,  -1),  (1, 0),  (1, 1),
        ]
        # fmt: on
        chans = []
        bands = ImageMode.getmode(mode).bands
        for band_ndx in range(len(bands)):
            channel_type = "L"  # 8-bit unorm
            channel_pattern = hopper(channel_type)

            # paste pattern with varying offsets to avoid correlation
            # potentially hiding some bugs (like channels getting mixed).
            paste_offset = (
                int(band_ndx / len(bands) * channel_pattern.size[0]),
                int(band_ndx / (len(bands) * 2) * channel_pattern.size[1]),
            )
            channel_data = Image.new(channel_type, channel_pattern.size)
            for delta in nine_grid_deltas:
                channel_data.paste(
                    channel_pattern,
                    tuple(
                        paste_offset[c] + delta[c] * channel_pattern.size[c]
                        for c in range(2)
                    ),
                )
            chans.append(channel_data)
        return Image.merge(mode, chans)

    source_image = create_test_image()
    source_image_aux = source_image.getchannel(preserved_channel)

    # create some transform, it doesn't matter which one
    source_profile = ImageCms.createProfile("sRGB")
    destination_profile = ImageCms.createProfile("sRGB")
    t = ImageCms.buildTransform(
        source_profile, destination_profile, inMode=mode, outMode=mode
    )

    # apply transform
    result_image: Image.Image | None
    if transform_in_place:
        ImageCms.applyTransform(source_image, t, inPlace=True)
        result_image = source_image
    else:
        result_image = ImageCms.applyTransform(source_image, t, inPlace=False)
    assert result_image is not None
    result_image_aux = result_image.getchannel(preserved_channel)

    assert_image_equal(source_image_aux, result_image_aux)


def test_preserve_auxiliary_channels_rgba() -> None:
    assert_aux_channel_preserved(
        mode="RGBA", transform_in_place=False, preserved_channel="A"
    )


def test_preserve_auxiliary_channels_rgba_in_place() -> None:
    assert_aux_channel_preserved(
        mode="RGBA", transform_in_place=True, preserved_channel="A"
    )


def test_preserve_auxiliary_channels_rgbx() -> None:
    assert_aux_channel_preserved(
        mode="RGBX", transform_in_place=False, preserved_channel="X"
    )


def test_preserve_auxiliary_channels_rgbx_in_place() -> None:
    assert_aux_channel_preserved(
        mode="RGBX", transform_in_place=True, preserved_channel="X"
    )


def test_auxiliary_channels_isolated() -> None:
    # test data in aux channels does not affect non-aux channels
    aux_channel_formats = [
        # format, profile, color-only format, source test image
        ("RGBA", "sRGB", "RGB", hopper("RGBA")),
        ("RGBX", "sRGB", "RGB", hopper("RGBX")),
        ("LAB", "LAB", "LAB", Image.open("Tests/images/hopper.Lab.tif")),
    ]
    for src_format in aux_channel_formats:
        for dst_format in aux_channel_formats:
            for transform_in_place in [True, False]:
                # inplace only if format doesn't change
                if transform_in_place and src_format[0] != dst_format[0]:
                    continue

                # convert with and without AUX data, test colors are equal
                src_colorSpace = cast(Literal["LAB", "XYZ", "sRGB"], src_format[1])
                source_profile = ImageCms.createProfile(src_colorSpace)
                destination_profile = ImageCms.createProfile(dst_format[1])
                source_image = src_format[3]
                test_transform = ImageCms.buildTransform(
                    source_profile,
                    destination_profile,
                    inMode=src_format[0],
                    outMode=dst_format[0],
                )

                # test conversion from aux-ful source
                test_image: Image.Image | None
                if transform_in_place:
                    test_image = source_image.copy()
                    ImageCms.applyTransform(test_image, test_transform, inPlace=True)
                else:
                    test_image = ImageCms.applyTransform(
                        source_image, test_transform, inPlace=False
                    )
                assert test_image is not None

                # reference conversion from aux-less source
                reference_transform = ImageCms.buildTransform(
                    source_profile,
                    destination_profile,
                    inMode=src_format[2],
                    outMode=dst_format[2],
                )
                reference_image = ImageCms.applyTransform(
                    source_image.convert(src_format[2]), reference_transform
                )
                assert reference_image is not None
                assert_image_equal(test_image.convert(dst_format[2]), reference_image)


def test_long_modes() -> None:
    p = ImageCms.getOpenProfile("Tests/icc/sGrey-v2-nano.icc")
    ImageCms.buildTransform(p, p, "ABCDEFGHI", "ABCDEFGHI")


@pytest.mark.parametrize("mode", ("RGB", "RGBA", "RGBX"))
def test_rgb_lab(mode: str) -> None:
    im = Image.new(mode, (1, 1))
    converted_im = im.convert("LAB")
    assert converted_im.getpixel((0, 0)) == (0, 128, 128)

    im = Image.new("LAB", (1, 1), (255, 0, 0))
    converted_im = im.convert(mode)
    assert converted_im.getpixel((0, 0))[:3] == (0, 255, 255)


def test_deprecation() -> None:
    with pytest.warns(DeprecationWarning):
        assert ImageCms.DESCRIPTION.strip().startswith("pyCMS")
    with pytest.warns(DeprecationWarning):
        assert ImageCms.VERSION == "1.0.0 pil"
    with pytest.warns(DeprecationWarning):
        assert isinstance(ImageCms.FLAGS, dict)

def test_buildTransform_flags_non_integer():
    with pytest.raises(ImageCms.PyCMSError):
        ImageCms.buildTransform(
            inputProfile="path/to/input/profile",
            outputProfile="path/to/output/profile",
            inMode="RGB",
            outMode="CMYK",
            renderingIntent=ImageCms.Intent.PERCEPTUAL,
            flags="not_an_integer"
        )

def test_buildTransform_flags_out_of_range():
    with pytest.raises(ImageCms.PyCMSError):
        ImageCms.buildTransform(
            inputProfile="path/to/input/profile",
            outputProfile="path/to/output/profile",
            inMode="RGB",
            outMode="CMYK",
            renderingIntent=ImageCms.Intent.PERCEPTUAL,
            flags=999999
        )

def test_renderingIntent_non_integer():
    with pytest.raises(ImageCms.PyCMSError) as exc_info:
        ImageCms.buildTransform(
            inputProfile="path/to/input/profile",
            outputProfile="path/to/output/profile",
            inMode="RGB",
            outMode="CMYK",
            renderingIntent="not an integer",
            flags=0
        )
    assert str(exc_info.value) == "renderingIntent must be an integer between 0 and 3"

