from __future__ import annotations

from io import BytesIO

import pytest

from PIL import CurImagePlugin, Image


def test_deerstalker() -> None:
    with Image.open("Tests/images/cur/deerstalker.cur") as im:
        assert im.size == (32, 32)
        assert im.info["hotspots"] == [(0, 0)]
        assert isinstance(im, CurImagePlugin.CurImageFile)
        # Check some pixel colors to ensure image is loaded properly
        assert im.getpixel((10, 1)) == (0, 0, 0, 0)
        assert im.getpixel((11, 1)) == (253, 254, 254, 1)
        assert im.getpixel((16, 16)) == (84, 87, 86, 255)


def test_posy_link():
    with Image.open("Tests/images/cur/posy_link.cur") as im:
        assert im.size == (128, 128)
        assert im.info["sizes"] == [(128, 128), (96, 96), (64, 64), (48, 48), (32, 32)]
        assert im.info["hotspots"] == [(25, 7), (18, 5), (12, 3), (9, 2), (5, 1)]
        # check some pixel colors
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((20, 20)) == (0, 0, 0, 255)
        assert im.getpixel((40, 40)) == (255, 255, 255, 255)

        im.size = (32, 32)
        im.load()
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((10, 10)) == (191, 191, 191, 255)


def test_stopwtch():
    with Image.open("Tests/images/cur/stopwtch.cur") as im:
        assert im.size == (32, 32)
        assert im.info["hotspots"] == [(16, 19)]

        assert im.getpixel((16, 16)) == (0, 0, 255, 255)
        assert im.getpixel((8, 16)) == (255, 0, 0, 255)


def test_win98_arrow():
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
    cur.fp.close()
    with open(no_cursors_file, "rb") as cur.fp:
        with pytest.raises(TypeError):
            cur._open()


def test_save_win98_arrow():
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

            with Image.open(output) as im2:
                assert im.tobytes() == im2.tobytes()

        with BytesIO() as output:
            im.save(output, format="CUR")

            # check default save params
            with Image.open(output) as im2:
                assert im2.size == (32, 32)
                assert im2.info["sizes"] == [(32, 32), (24, 24), (16, 16)]
                assert im2.info["hotspots"] == [(0, 0), (0, 0), (0, 0)]


def test_save_posy_link():
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
            with Image.open(output, formats=["CUR"]) as im2:
                assert (128, 128) == im2.size
                assert sizes == im2.info["sizes"]

        with BytesIO() as output:
            im.save(output, sizes=sizes[3:], hotspots=hotspots[3:], format="CUR")

            # make sure saved output is readable
            # and sizes/hotspots are correct
            with Image.open(output, formats=["CUR"]) as im2:
                assert (48, 48) == im2.size
                assert sizes[3:] == im2.info["sizes"]

            # make sure error is thrown when size and hotspot len's
            # don't match
            with pytest.raises(ValueError):
                im.save(
                    output,
                    sizes=sizes[2:],
                    hotspots=hotspots[3:],
                    format="CUR",
                    bitmap_format="bmp",
                )
