import os
import sys
from io import BytesIO

import pytest

from PIL import Image, PSDraw


def _create_document(ps):
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


def test_draw_postscript(tmp_path):
    # Based on Pillow tutorial, but there is no textsize:
    # https://pillow.readthedocs.io/en/latest/handbook/tutorial.html#drawing-postscript

    # Arrange
    tempfile = str(tmp_path / "temp.ps")
    with open(tempfile, "wb") as fp:
        # Act
        ps = PSDraw.PSDraw(fp)
        _create_document(ps)

    # Assert
    # Check non-zero file was created
    assert os.path.isfile(tempfile)
    assert os.path.getsize(tempfile) > 0


@pytest.mark.parametrize("buffer", (True, False))
def test_stdout(buffer):
    # Temporarily redirect stdout
    old_stdout = sys.stdout

    if buffer:

        class MyStdOut:
            buffer = BytesIO()

        mystdout = MyStdOut()
    else:
        mystdout = BytesIO()

    sys.stdout = mystdout

    ps = PSDraw.PSDraw()
    _create_document(ps)

    # Reset stdout
    sys.stdout = old_stdout

    if buffer:
        mystdout = mystdout.buffer
    assert mystdout.getvalue() != b""
