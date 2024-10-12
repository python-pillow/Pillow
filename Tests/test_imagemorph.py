# Test the ImageMorphology functionality
from __future__ import annotations

from pathlib import Path

import pytest

from PIL import Image, ImageMorph, _imagingmorph

from .helper import assert_image_equal_tofile, hopper


def string_to_img(image_string: str) -> Image.Image:
    """Turn a string image representation into a binary image"""
    rows = [s for s in image_string.replace(" ", "").split("\n") if len(s)]
    height = len(rows)
    width = len(rows[0])
    im = Image.new("L", (width, height))
    for i in range(width):
        for j in range(height):
            c = rows[j][i]
            v = c in "X1"
            im.putpixel((i, j), v)

    return im


A = string_to_img(
    """
    .......
    .......
    ..111..
    ..111..
    ..111..
    .......
    .......
    """
)


def img_to_string(im: Image.Image) -> str:
    """Turn a (small) binary image into a string representation"""
    chars = ".1"
    result = []
    for r in range(im.height):
        line = ""
        for c in range(im.width):
            value = im.getpixel((c, r))
            assert not isinstance(value, tuple)
            assert value is not None
            line += chars[value > 0]
        result.append(line)
    return "\n".join(result)


def img_string_normalize(im: str) -> str:
    return img_to_string(string_to_img(im))


def assert_img_equal_img_string(a: Image.Image, b_string: str) -> None:
    assert img_to_string(a) == img_string_normalize(b_string)


def test_str_to_img() -> None:
    assert_image_equal_tofile(A, "Tests/images/morph_a.png")


@pytest.mark.parametrize(
    "op", ("corner", "dilation4", "dilation8", "erosion4", "erosion8", "edge")
)
def test_lut(op: str) -> None:
    lb = ImageMorph.LutBuilder(op_name=op)
    assert lb.get_lut() is None

    lut = lb.build_lut()
    with open(f"Tests/images/{op}.lut", "rb") as f:
        assert lut == bytearray(f.read())


def test_no_operator_loaded() -> None:
    im = Image.new("L", (1, 1))
    mop = ImageMorph.MorphOp()
    with pytest.raises(Exception) as e:
        mop.apply(im)
    assert str(e.value) == "No operator loaded"
    with pytest.raises(Exception) as e:
        mop.match(im)
    assert str(e.value) == "No operator loaded"
    with pytest.raises(Exception) as e:
        mop.save_lut("")
    assert str(e.value) == "No operator loaded"


# Test the named patterns
def test_erosion8() -> None:
    # erosion8
    mop = ImageMorph.MorphOp(op_name="erosion8")
    count, Aout = mop.apply(A)
    assert count == 8
    assert_img_equal_img_string(
        Aout,
        """
                                     .......
                                     .......
                                     .......
                                     ...1...
                                     .......
                                     .......
                                     .......
                                     """,
    )


def test_dialation8() -> None:
    # dialation8
    mop = ImageMorph.MorphOp(op_name="dilation8")
    count, Aout = mop.apply(A)
    assert count == 16
    assert_img_equal_img_string(
        Aout,
        """
                                     .......
                                     .11111.
                                     .11111.
                                     .11111.
                                     .11111.
                                     .11111.
                                     .......
                                     """,
    )


def test_erosion4() -> None:
    # erosion4
    mop = ImageMorph.MorphOp(op_name="dilation4")
    count, Aout = mop.apply(A)
    assert count == 12
    assert_img_equal_img_string(
        Aout,
        """
                                     .......
                                     ..111..
                                     .11111.
                                     .11111.
                                     .11111.
                                     ..111..
                                     .......
                                     """,
    )


def test_edge() -> None:
    # edge
    mop = ImageMorph.MorphOp(op_name="edge")
    count, Aout = mop.apply(A)
    assert count == 1
    assert_img_equal_img_string(
        Aout,
        """
                                     .......
                                     .......
                                     ..111..
                                     ..1.1..
                                     ..111..
                                     .......
                                     .......
                                     """,
    )


def test_corner() -> None:
    # Create a corner detector pattern
    mop = ImageMorph.MorphOp(patterns=["1:(... ... ...)->0", "4:(00. 01. ...)->1"])
    count, Aout = mop.apply(A)
    assert count == 5
    assert_img_equal_img_string(
        Aout,
        """
                                     .......
                                     .......
                                     ..1.1..
                                     .......
                                     ..1.1..
                                     .......
                                     .......
                                     """,
    )

    # Test the coordinate counting with the same operator
    coords = mop.match(A)
    assert len(coords) == 4
    assert tuple(coords) == ((2, 2), (4, 2), (2, 4), (4, 4))

    coords = mop.get_on_pixels(Aout)
    assert len(coords) == 4
    assert tuple(coords) == ((2, 2), (4, 2), (2, 4), (4, 4))


def test_mirroring() -> None:
    # Test 'M' for mirroring
    mop = ImageMorph.MorphOp(patterns=["1:(... ... ...)->0", "M:(00. 01. ...)->1"])
    count, Aout = mop.apply(A)
    assert count == 7
    assert_img_equal_img_string(
        Aout,
        """
                                     .......
                                     .......
                                     ..1.1..
                                     .......
                                     .......
                                     .......
                                     .......
                                     """,
    )


def test_negate() -> None:
    # Test 'N' for negate
    mop = ImageMorph.MorphOp(patterns=["1:(... ... ...)->0", "N:(00. 01. ...)->1"])
    count, Aout = mop.apply(A)
    assert count == 8
    assert_img_equal_img_string(
        Aout,
        """
                                     .......
                                     .......
                                     ..1....
                                     .......
                                     .......
                                     .......
                                     .......
                                     """,
    )


def test_incorrect_mode() -> None:
    im = hopper("RGB")
    mop = ImageMorph.MorphOp(op_name="erosion8")

    with pytest.raises(ValueError) as e:
        mop.apply(im)
    assert str(e.value) == "Image mode must be L"
    with pytest.raises(ValueError) as e:
        mop.match(im)
    assert str(e.value) == "Image mode must be L"
    with pytest.raises(ValueError) as e:
        mop.get_on_pixels(im)
    assert str(e.value) == "Image mode must be L"


def test_add_patterns() -> None:
    # Arrange
    lb = ImageMorph.LutBuilder(op_name="corner")
    assert lb.patterns == ["1:(... ... ...)->0", "4:(00. 01. ...)->1"]
    new_patterns = ["M:(00. 01. ...)->1", "N:(00. 01. ...)->1"]

    # Act
    lb.add_patterns(new_patterns)

    # Assert
    assert lb.patterns == [
        "1:(... ... ...)->0",
        "4:(00. 01. ...)->1",
        "M:(00. 01. ...)->1",
        "N:(00. 01. ...)->1",
    ]


def test_unknown_pattern() -> None:
    with pytest.raises(Exception):
        ImageMorph.LutBuilder(op_name="unknown")


def test_pattern_syntax_error() -> None:
    # Arrange
    lb = ImageMorph.LutBuilder(op_name="corner")
    new_patterns = ["a pattern with a syntax error"]
    lb.add_patterns(new_patterns)

    # Act / Assert
    with pytest.raises(Exception) as e:
        lb.build_lut()
    assert str(e.value) == 'Syntax error in pattern "a pattern with a syntax error"'


def test_load_invalid_mrl() -> None:
    # Arrange
    invalid_mrl = "Tests/images/hopper.png"
    mop = ImageMorph.MorphOp()

    # Act / Assert
    with pytest.raises(Exception) as e:
        mop.load_lut(invalid_mrl)
    assert str(e.value) == "Wrong size operator file!"


def test_roundtrip_mrl(tmp_path: Path) -> None:
    # Arrange
    tempfile = str(tmp_path / "temp.mrl")
    mop = ImageMorph.MorphOp(op_name="corner")
    initial_lut = mop.lut

    # Act
    mop.save_lut(tempfile)
    mop.load_lut(tempfile)

    # Act / Assert
    assert mop.lut == initial_lut


def test_set_lut() -> None:
    # Arrange
    lb = ImageMorph.LutBuilder(op_name="corner")
    lut = lb.build_lut()
    mop = ImageMorph.MorphOp()

    # Act
    mop.set_lut(lut)

    # Assert
    assert mop.lut == lut


def test_wrong_mode() -> None:
    lut = ImageMorph.LutBuilder(op_name="corner").build_lut()
    imrgb_ptr = Image.new("RGB", (10, 10)).getim()
    iml_ptr = Image.new("L", (10, 10)).getim()

    with pytest.raises(RuntimeError):
        _imagingmorph.apply(bytes(lut), imrgb_ptr, iml_ptr)

    with pytest.raises(RuntimeError):
        _imagingmorph.apply(bytes(lut), iml_ptr, imrgb_ptr)

    with pytest.raises(RuntimeError):
        _imagingmorph.match(bytes(lut), imrgb_ptr)

    # Should not raise
    _imagingmorph.match(bytes(lut), iml_ptr)
