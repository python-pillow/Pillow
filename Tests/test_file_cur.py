from __future__ import annotations

from io import BytesIO

import pytest

from PIL import CurImagePlugin, Image
from PIL._binary import o8
from PIL._binary import o16le as o16
from PIL._binary import o32le as o32

from .helper import assert_image_equal


def test_sanity() -> None:
    with Image.open("Tests/images/cur/deerstalker.cur") as im:
        assert im.size == (32, 32)
        assert im.info["hotspots"] == [(0, 0)]
        assert isinstance(im, CurImagePlugin.CurImageFile)

        # Check pixel colors to ensure image is loaded properly
        assert im.getpixel((10, 1)) == (0, 0, 0, 0)
        assert im.getpixel((11, 1)) == (253, 254, 254, 1)
        assert im.getpixel((16, 16)) == (84, 87, 86, 255)


def test_largest_cursor() -> None:
    magic = b"\x00\x00\x02\x00"
    sizes = ((1, 1), (8, 8), (4, 4))
    data = magic + o16(len(sizes))
    for w, h in sizes:
        image_offset = 6 + len(sizes) * 16 if (w, h) == max(sizes) else 0
        data += o8(w) + o8(h) + o8(0) * 10 + o32(image_offset)
    data += (
        o32(12)  # header size
        + o16(8)  # width
        + o16(16)  # height
        + o16(0)  # planes
        + o16(1)  # bits
    )
    with Image.open(BytesIO(data)) as im:
        assert im.size == (8, 8)


def test_posy_link() -> None:
    with Image.open("Tests/images/cur/posy_link.cur") as im:
        assert im.size == (128, 128)
        assert im.info["sizes"] == {(128, 128), (96, 96), (64, 64), (48, 48), (32, 32)}
        assert im.info["hotspots"] == [(25, 7), (18, 5), (12, 3), (9, 2), (5, 1)]

        # check pixel colors
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((20, 20)) == (0, 0, 0, 255)
        assert im.getpixel((40, 40)) == (255, 255, 255, 255)

        im.size = (32, 32)
        im.load()
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((10, 10)) == (191, 191, 191, 255)


def test_stopwtch() -> None:
    with Image.open("Tests/images/cur/stopwtch.cur") as im:
        assert im.size == (32, 32)
        assert im.info["hotspots"] == [(16, 19)]

        assert im.getpixel((16, 16)) == (0, 0, 255, 255)
        assert im.getpixel((8, 16)) == (255, 0, 0, 255)


def test_win98_arrow() -> None:
    with Image.open("Tests/images/cur/win98_arrow.cur") as im:
        assert im.size == (32, 32)
        assert im.info["hotspots"] == [(10, 10)]

        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((16, 16)) == (0, 0, 0, 255)
        assert im.getpixel((14, 19)) == (255, 255, 255, 255)


def test_invalid_file() -> None:
    invalid_file = "Tests/images/cur/posy_link.png"

    with pytest.raises(SyntaxError):
        CurImagePlugin.CurImageFile(invalid_file)

    no_cursors_file = "Tests/images/cur/no_cursors.cur"

    cur = CurImagePlugin.CurImageFile("Tests/images/cur/deerstalker.cur")
    assert cur.fp is not None
    cur.fp.close()
    with open(no_cursors_file, "rb") as cur.fp:
        with pytest.raises(TypeError):
            cur._open()


def test_save_win98_arrow() -> None:
    with Image.open("Tests/images/cur/win98_arrow.png") as im:
        # save the data
        with BytesIO() as output:
            im.save(
                output,
                format="CUR",
                sizes=[(32, 32)],
                hotspots=[(10, 10)],
                bitmap_format="bmp",
            )
            with Image.open(output) as reloaded:
                assert_image_equal(im, reloaded)

        with BytesIO() as output:
            im.save(output, format="CUR")

            # check default save params
            with Image.open(output) as reloaded:
                assert reloaded.size == (32, 32)
                assert reloaded.info["sizes"] == {(32, 32), (24, 24), (16, 16)}
                assert reloaded.info["hotspots"] == [(0, 0), (0, 0), (0, 0)]


def test_save_posy_link() -> None:
    sizes = [(128, 128), (96, 96), (64, 64), (48, 48), (32, 32)]
    hotspots = [(25, 7), (18, 5), (12, 3), (9, 2), (5, 1)]

    with Image.open("Tests/images/cur/posy_link.png") as im:
        # save the data
        with BytesIO() as output:
            im.save(
                output,
                sizes=sizes,
                hotspots=hotspots,
                format="CUR",
                bitmap_format="bmp",
            )

            # make sure saved output is readable
            # and sizes/hotspots are correct
            with Image.open(output, formats=["CUR"]) as reloaded:
                assert (128, 128) == reloaded.size
                assert set(sizes) == reloaded.info["sizes"]

        with BytesIO() as output:
            im.save(output, sizes=sizes[3:], hotspots=hotspots[3:], format="CUR")

            # make sure saved output is readable
            # and sizes/hotspots are correct
            with Image.open(output, formats=["CUR"]) as reloaded:
                assert reloaded.size == (48, 48)
                assert reloaded.info["sizes"] == set(sizes[3:])

            # check error is thrown when size and hotspot length don't match
            with pytest.raises(ValueError):
                im.save(
                    output,
                    sizes=sizes[2:],
                    hotspots=hotspots[3:],
                    format="CUR",
                    bitmap_format="bmp",
                )
