from __future__ import annotations

import operator

import pytest

from PIL import Image

from .helper import hopper


@pytest.mark.parametrize("method", ["getdata", "get_flattened_data"])
def test_sanity(method: str) -> None:
    im = hopper()

    data = getattr(im, method)()
    assert len(data) == 128 * 128
    assert data[0] == (20, 20, 70)
    assert data[-1] == data[128 * 128 - 1]

    # And the single-band case
    band = getattr(im, method)(0)
    assert len(band) == 128 * 128
    assert band[0] == 20
    assert band[-1] == band[128 * 128 - 1]


@pytest.mark.parametrize("method", ["getdata", "get_flattened_data"])
def test_mode(method: str) -> None:
    def getdata(mode: str) -> tuple[float | tuple[int, ...] | None, int, int]:
        im = hopper(mode).resize((32, 30), Image.Resampling.NEAREST)
        data = getattr(im, method)()
        return data[0], len(data), len(list(data))

    assert getdata("1") == (0, 960, 960)
    assert getdata("L") == (17, 960, 960)
    assert getdata("I") == (17, 960, 960)
    assert getdata("F") == (17.0, 960, 960)
    assert getdata("RGB") == ((11, 13, 52), 960, 960)
    assert getdata("RGBA") == ((11, 13, 52, 255), 960, 960)
    assert getdata("CMYK") == ((244, 242, 203, 0), 960, 960)
    assert getdata("YCbCr") == ((16, 147, 123), 960, 960)


def test_index_out_of_range() -> None:
    hopper_data = hopper().getdata()
    for index in (128 * 128, -128 * 128 - 1, 1 << 40):
        with pytest.raises(IndexError):
            hopper_data[index]


def test_iteration_matches_indexing() -> None:
    hopper_data = hopper().getdata()
    as_list = list(hopper_data)
    assert len(as_list) == len(hopper_data)
    assert as_list == [hopper_data[i] for i in range(len(hopper_data))]


def test_iteration_is_repeatable() -> None:
    hopper_data = hopper().getdata()
    assert list(hopper_data) == list(hopper_data)


def test_exhausted_iterator_stays_exhausted() -> None:
    hopper_data = hopper().getdata()
    it = iter(hopper_data)
    assert len(list(it)) == len(hopper_data)
    assert list(it) == []
    with pytest.raises(StopIteration):
        next(it)


def test_length_hint() -> None:
    hopper_data = hopper().getdata()
    it = iter(hopper_data)
    assert operator.length_hint(it) == len(hopper_data)
    next(it)
    assert operator.length_hint(it) == len(hopper_data) - 1
    list(it)
    assert operator.length_hint(it) == 0


def test_matches_get_flattened_data() -> None:
    assert tuple(hopper().getdata()) == hopper().get_flattened_data()


def test_is_read_only() -> None:
    hopper_data = hopper().getdata()
    with pytest.raises(TypeError):
        hopper_data[0] = (0, 0, 0)  # type: ignore[index]


def test_getdata_does_not_expose_the_image_core() -> None:
    hopper_data = hopper().getdata()
    # "Weird" core bits are not exposed:
    for name in ["putpixel", "paste", "ptr", "putdata"]:
        assert not hasattr(hopper_data, name)


@pytest.mark.parametrize("size", [(0, 0), (0, 5), (5, 0)])
def test_empty_image(size: tuple[int, int]) -> None:
    data = Image.new("RGB", size).getdata()
    assert len(data) == 0
    assert list(data) == []
    with pytest.raises(IndexError):
        data[0]


def test_outlives_the_image() -> None:
    im = Image.new("RGB", (2, 2), (1, 2, 3))
    data = im.getdata()
    del im
    assert list(data) == [(1, 2, 3)] * 4


def test_is_a_live_view() -> None:
    im = Image.new("RGB", (2, 2), (0, 0, 0))
    data = im.getdata()
    im.putpixel((0, 0), (9, 9, 9))
    assert data[0] == (9, 9, 9)


def test_accepted_by_putdata() -> None:
    im = hopper()
    hopper_data = im.getdata()
    out = Image.new("RGB", im.size)
    out.putdata(hopper_data)
    assert out.tobytes() == im.tobytes()
