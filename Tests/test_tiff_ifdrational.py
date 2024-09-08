from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from PIL import Image, TiffImagePlugin
from PIL.TiffImagePlugin import IFDRational

from .helper import hopper, skip_unless_feature


def _test_equal(
    num: float | Fraction | IFDRational,
    denom: int,
    target: float | Fraction | IFDRational,
) -> None:
    t = IFDRational(num, denom)

    assert target == t
    assert t == target


def test_sanity() -> None:
    _test_equal(1, 1, 1)
    _test_equal(1, 1, Fraction(1, 1))

    _test_equal(2, 2, 1)
    _test_equal(1.0, 1, Fraction(1, 1))

    _test_equal(Fraction(1, 1), 1, Fraction(1, 1))
    _test_equal(IFDRational(1, 1), 1, 1)

    _test_equal(1, 2, Fraction(1, 2))
    _test_equal(1, 2, IFDRational(1, 2))

    _test_equal(7, 5, 1.4)


def test_ranges() -> None:
    for num in range(1, 10):
        for denom in range(1, 10):
            assert IFDRational(num, denom) == IFDRational(num, denom)


def test_nonetype() -> None:
    # Fails if the _delegate function doesn't return a valid function

    xres = IFDRational(72)
    yres = IFDRational(72)
    assert xres._val is not None
    assert xres.numerator is not None
    assert xres.denominator is not None
    assert yres._val is not None

    assert xres
    assert yres


@pytest.mark.parametrize(
    "libtiff", (pytest.param(True, marks=skip_unless_feature("libtiff")), False)
)
def test_ifd_rational_save(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, libtiff: bool
) -> None:
    im = hopper()
    out = str(tmp_path / "temp.tiff")
    res = IFDRational(301, 1)

    monkeypatch.setattr(TiffImagePlugin, "WRITE_LIBTIFF", libtiff)
    im.save(out, dpi=(res, res), compression="raw")

    with Image.open(out) as reloaded:
        assert float(IFDRational(301, 1)) == float(reloaded.tag_v2[282])
