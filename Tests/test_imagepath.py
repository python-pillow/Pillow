import array
import struct
import pytest
import math

from PIL import Image, ImagePath
from PIL._util import py3

from .helper import PillowTestCase


class TestImagePath(PillowTestCase):
    def test_path(self):

        p = ImagePath.Path(list(range(10)))

        # sequence interface
        self.assertEqual(len(p), 5)
        self.assertEqual(p[0], (0.0, 1.0))
        self.assertEqual(p[-1], (8.0, 9.0))
        self.assertEqual(list(p[:1]), [(0.0, 1.0)])
        with self.assertRaises(TypeError) as cm:
            p["foo"]
        self.assertEqual(str(cm.exception),
                         "Path indices must be integers, not str")
        self.assertEqual(
            list(p), [(0.0, 1.0), (2.0, 3.0),
                      (4.0, 5.0), (6.0, 7.0), (8.0, 9.0)]
        )

        # method sanity check
        self.assertEqual(
            p.tolist(), [(0.0, 1.0), (2.0, 3.0),
                         (4.0, 5.0), (6.0, 7.0), (8.0, 9.0)]
        )
        self.assertEqual(
            p.tolist(1), [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
        )

        self.assertEqual(p.getbbox(), (0.0, 1.0, 8.0, 9.0))

        self.assertEqual(p.compact(5), 2)
        self.assertEqual(list(p), [(0.0, 1.0), (4.0, 5.0), (8.0, 9.0)])

        p.transform((1, 0, 1, 0, 1, 1))
        self.assertEqual(list(p), [(1.0, 2.0), (5.0, 6.0), (9.0, 10.0)])

        # alternative constructors
        p = ImagePath.Path([0, 1])
        self.assertEqual(list(p), [(0.0, 1.0)])
        p = ImagePath.Path([0.0, 1.0])
        self.assertEqual(list(p), [(0.0, 1.0)])
        p = ImagePath.Path([0, 1])
        self.assertEqual(list(p), [(0.0, 1.0)])
        p = ImagePath.Path([(0, 1)])
        self.assertEqual(list(p), [(0.0, 1.0)])
        p = ImagePath.Path(p)
        self.assertEqual(list(p), [(0.0, 1.0)])
        p = ImagePath.Path(p.tolist(0))
        self.assertEqual(list(p), [(0.0, 1.0)])
        p = ImagePath.Path(p.tolist(1))
        self.assertEqual(list(p), [(0.0, 1.0)])
        p = ImagePath.Path(array.array("f", [0, 1]))
        self.assertEqual(list(p), [(0.0, 1.0)])

        arr = array.array("f", [0, 1])
        if hasattr(arr, "tobytes"):
            p = ImagePath.Path(arr.tobytes())
        else:
            p = ImagePath.Path(arr.tostring())
        self.assertEqual(list(p), [(0.0, 1.0)])

    def test_overflow_segfault(self):
        # Some Pythons fail getting the argument as an integer, and it falls
        # through to the sequence. Seeing this on 32-bit Windows.
        with self.assertRaises((TypeError, MemoryError)):
            # post patch, this fails with a memory error
            x = evil()

            # This fails due to the invalid malloc above,
            # and segfaults
            for i in range(200000):
                if py3:
                    x[i] = b"0" * 16
                else:
                    x[i] = "0" * 16


def test_path_odd_number_of_coordinates():
    # Arrange
    coords = [0]

    # Act / Assert
    with pytest.raises(ValueError) as e:
        ImagePath.Path(coords)

    assert str(e.value) == "wrong number of coordinates"


def test_getbbox():
    for coords, expected in [
            ([0, 1, 2, 3], (0.0, 1.0, 2.0, 3.0)),
            ([3, 2, 1, 0], (1.0, 0.0, 3.0, 2.0)),
            (0, (0.0, 0.0, 0.0, 0.0)),
            (1, (0.0, 0.0, 0.0, 0.0)),
    ]:

        # Arrange
        p = ImagePath.Path(coords)

        # Act / Assert
        assert p.getbbox() == expected


def test_getbbox_no_args():
    # Arrange
    p = ImagePath.Path([0, 1, 2, 3])

    # Act / Assert
    with pytest.raises(TypeError):
        p.getbbox(1)


def test_map():
    for coords, expected in [
        (0, []),
        (list(range(6)), [(0.0, 3.0), (4.0, 9.0), (8.0, 15.0)]),
    ]:
        # Arrange
        p = ImagePath.Path(coords)

        # Act
        # Modifies the path in-place
        p.map(lambda x, y: (x * 2, y * 3))

        # Assert
        assert list(p) == expected


def test_transform():
    # Arrange
    p = ImagePath.Path([0, 1, 2, 3])
    theta = math.pi / 15

    # Act
    # Affine transform, in-place
    p.transform(
        (math.cos(theta), math.sin(theta), 20, -
         math.sin(theta), math.cos(theta), 20),
    )

    # Assert
    assert p.tolist() == [
        (20.20791169081776, 20.978147600733806),
        (22.58003027392089, 22.518619420565898),
    ]


def test_transform_with_wrap():
    # Arrange
    p = ImagePath.Path([0, 1, 2, 3])
    theta = math.pi / 15

    # Act
    # Affine transform, in-place, with wrap parameter
    p.transform(
        (math.cos(theta), math.sin(theta), 20, -
         math.sin(theta), math.cos(theta), 20),
        1.0,
    )

    # Assert
    assert p.tolist() == [
        (0.20791169081775962, 20.978147600733806),
        (0.5800302739208902, 22.518619420565898),
    ]


def test_overflow_segfault():
    # Some Pythons fail getting the argument as an integer, and it falls
    # through to the sequence. Seeing this on 32-bit Windows.
    with pytest.raises((TypeError, MemoryError)):
        # post patch, this fails with a memory error
        x = evil()

        # This fails due to the invalid malloc above,
        # and segfaults
        for i in range(200000):
            x[i] = b"0" * 16


class evil:
    def __init__(self):
        self.corrupt = Image.core.path(0x4000000000000000)

    def __getitem__(self, i):
        x = self.corrupt[i]
        return struct.pack("dd", x[0], x[1])

    def __setitem__(self, i, x):
        self.corrupt[i] = struct.unpack("dd", x)
