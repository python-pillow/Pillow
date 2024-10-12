from __future__ import annotations

import array
import math
import struct
from collections.abc import Sequence

import pytest

from PIL import Image, ImagePath


def test_path() -> None:
    p = ImagePath.Path(list(range(10)))

    # sequence interface
    assert len(p) == 5
    assert p[0] == (0.0, 1.0)
    assert p[-1] == (8.0, 9.0)
    assert list(p[:1]) == [(0.0, 1.0)]
    with pytest.raises(TypeError) as cm:
        p["foo"]
    assert str(cm.value) == "Path indices must be integers, not str"
    assert list(p) == [(0.0, 1.0), (2.0, 3.0), (4.0, 5.0), (6.0, 7.0), (8.0, 9.0)]

    # method sanity check
    assert p.tolist() == [
        (0.0, 1.0),
        (2.0, 3.0),
        (4.0, 5.0),
        (6.0, 7.0),
        (8.0, 9.0),
    ]
    assert p.tolist(True) == [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]

    assert p.getbbox() == (0.0, 1.0, 8.0, 9.0)

    assert p.compact(5) == 2
    assert list(p) == [(0.0, 1.0), (4.0, 5.0), (8.0, 9.0)]

    p.transform((1, 0, 1, 0, 1, 1))
    assert list(p) == [(1.0, 2.0), (5.0, 6.0), (9.0, 10.0)]


@pytest.mark.parametrize(
    "coords",
    (
        (0, 1),
        [0, 1],
        (0.0, 1.0),
        [0.0, 1.0],
        ((0, 1),),
        [(0, 1)],
        ((0.0, 1.0),),
        [(0.0, 1.0)],
        array.array("f", [0, 1]),
        array.array("f", [0, 1]).tobytes(),
        ImagePath.Path((0, 1)),
    ),
)
def test_path_constructors(
    coords: Sequence[float] | array.array[float] | ImagePath.Path,
) -> None:
    # Arrange / Act
    p = ImagePath.Path(coords)

    # Assert
    assert list(p) == [(0.0, 1.0)]


@pytest.mark.parametrize(
    "coords",
    (
        ("a", "b"),
        ([0, 1],),
        [[0, 1]],
        ([0.0, 1.0],),
        [[0.0, 1.0]],
    ),
)
def test_invalid_path_constructors(
    coords: tuple[str, str] | Sequence[Sequence[int]]
) -> None:
    # Act
    with pytest.raises(ValueError) as e:
        ImagePath.Path(coords)

    # Assert
    assert str(e.value) == "incorrect coordinate type"


@pytest.mark.parametrize(
    "coords",
    (
        (0,),
        [0],
        (0, 1, 2),
        [0, 1, 2],
    ),
)
def test_path_odd_number_of_coordinates(coords: Sequence[int]) -> None:
    # Act
    with pytest.raises(ValueError) as e:
        ImagePath.Path(coords)

    # Assert
    assert str(e.value) == "wrong number of coordinates"


@pytest.mark.parametrize(
    "coords, expected",
    [
        ([0, 1, 2, 3], (0.0, 1.0, 2.0, 3.0)),
        ([3, 2, 1, 0], (1.0, 0.0, 3.0, 2.0)),
        (0, (0.0, 0.0, 0.0, 0.0)),
        (1, (0.0, 0.0, 0.0, 0.0)),
    ],
)
def test_getbbox(
    coords: int | list[int], expected: tuple[float, float, float, float]
) -> None:
    # Arrange
    p = ImagePath.Path(coords)

    # Act / Assert
    assert p.getbbox() == expected


def test_getbbox_no_args() -> None:
    # Arrange
    p = ImagePath.Path([0, 1, 2, 3])

    # Act / Assert
    with pytest.raises(TypeError):
        p.getbbox(1)


@pytest.mark.parametrize(
    "coords, expected",
    [
        (0, []),
        (list(range(6)), [(0.0, 3.0), (4.0, 9.0), (8.0, 15.0)]),
    ],
)
def test_map(coords: int | list[int], expected: list[tuple[float, float]]) -> None:
    # Arrange
    p = ImagePath.Path(coords)

    # Act
    # Modifies the path in-place
    p.map(lambda x, y: (x * 2, y * 3))

    # Assert
    assert list(p) == expected


def test_transform() -> None:
    # Arrange
    p = ImagePath.Path([0, 1, 2, 3])
    theta = math.pi / 15

    # Act
    # Affine transform, in-place
    p.transform(
        (math.cos(theta), math.sin(theta), 20, -math.sin(theta), math.cos(theta), 20),
    )

    # Assert
    assert p.tolist() == [
        (20.20791169081776, 20.978147600733806),
        (22.58003027392089, 22.518619420565898),
    ]


def test_transform_with_wrap() -> None:
    # Arrange
    p = ImagePath.Path([0, 1, 2, 3])
    theta = math.pi / 15

    # Act
    # Affine transform, in-place, with wrap parameter
    p.transform(
        (math.cos(theta), math.sin(theta), 20, -math.sin(theta), math.cos(theta), 20),
        1.0,
    )

    # Assert
    assert p.tolist() == [
        (0.20791169081775962, 20.978147600733806),
        (0.5800302739208902, 22.518619420565898),
    ]


def test_overflow_segfault() -> None:
    # Some Pythons fail getting the argument as an integer, and it falls
    # through to the sequence. Seeing this on 32-bit Windows.
    with pytest.raises((TypeError, MemoryError)):
        # post patch, this fails with a memory error
        x = Evil()

        # This fails due to the invalid malloc above,
        # and segfaults
        for i in range(200000):
            x[i] = b"0" * 16


def test_compact_within_map() -> None:
    p = ImagePath.Path([0, 1])

    def map_func(x: float, y: float) -> tuple[float, float]:
        p.compact()
        return 0, 0

    with pytest.raises(ValueError):
        p.map(map_func)


class Evil:
    def __init__(self) -> None:
        self.corrupt = Image.core.path(0x4000000000000000)

    def __getitem__(self, i: int) -> bytes:
        x = self.corrupt[i]
        return struct.pack("dd", x[0], x[1])

    def __setitem__(self, i: int, x: bytes) -> None:
        self.corrupt[i] = struct.unpack("dd", x)
