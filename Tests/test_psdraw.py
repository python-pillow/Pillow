from __future__ import annotations

import os
import sys
from io import BytesIO

import pytest

from PIL import Image, PSDraw

TYPE_CHECKING = False
if TYPE_CHECKING:
    from pathlib import Path


def _create_document(ps: PSDraw.PSDraw) -> None:
    title = "hopper"
    box = (1 * 72, 2 * 72, 7 * 72, 10 * 72)  # in points

    ps.begin_document(title)

    # draw diagonal lines in a cross
    ps.line((1 * 72, 2 * 72), (7 * 72, 10 * 72))
    ps.line((7 * 72, 2 * 72), (1 * 72, 10 * 72))

    # draw the image (75 dpi)
    with Image.open("Tests/images/hopper.ppm") as im:
        ps.image(box, im, 75)
    ps.rectangle(box)

    # draw title
    ps.setfont("Courier", 36)
    ps.text((3 * 72, 4 * 72), title)

    ps.end_document()


def test_draw_postscript(tmp_path: Path) -> None:
    # Based on Pillow tutorial, but there is no textsize:
    # https://pillow.readthedocs.io/en/latest/handbook/tutorial.html#drawing-postscript

    # Arrange
    tempfile = tmp_path / "temp.ps"
    with open(tempfile, "wb") as fp:
        # Act
        ps = PSDraw.PSDraw(fp)
        _create_document(ps)

    # Assert
    # Check non-zero file was created
    assert os.path.isfile(tempfile)
    assert os.path.getsize(tempfile) > 0


def test_stdout(monkeypatch: pytest.MonkeyPatch) -> None:
    # Temporarily redirect stdout
    class MyStdOut:
        buffer = BytesIO()

    mystdout = MyStdOut()

    monkeypatch.setattr(sys, "stdout", mystdout)

    ps = PSDraw.PSDraw()
    _create_document(ps)

    assert mystdout.buffer.getvalue() != b""


@pytest.mark.parametrize("escape", (None, False, True))
@pytest.mark.parametrize(
    "text, expected, escaped",
    (
        ("plain text", b"plain text", b"plain text"),
        ("a(b)c", rb"a\(b\)c", rb"a\(b\)c"),
        (r"C:\temp\new", rb"C:\temp\new", rb"C:\\temp\\new"),
        (r"a\(b)\c", rb"a\\(b\)\c", rb"a\\\(b\)\\c"),
        (r"\n\t\101", rb"\n\t\101", rb"\\n\\t\\101"),
    ),
)
def test_text(text: str, expected: bytes, escaped: bytes, escape: bool | None) -> None:
    with BytesIO() as buffer:
        ps = PSDraw.PSDraw(buffer)
        if escape is None:
            ps.text((10, 20), text)
        else:
            ps.text((10, 20), text, escape=escape)
        if escape:
            expected = escaped
        assert buffer.getvalue() == b"10 20 M (" + expected + b") S\n"


def test_text_encoding_error() -> None:
    with BytesIO() as buffer:
        ps = PSDraw.PSDraw(buffer)
        with pytest.raises(UnicodeEncodeError):
            ps.text((10, 20), "\u0100")
        assert buffer.getvalue() == b""
