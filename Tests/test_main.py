import os
import subprocess
import sys


def test_main():
    out = subprocess.check_output([sys.executable, "-m", "PIL"]).decode("utf-8")
    lines = out.splitlines()
    assert lines[0] == "-" * 68
    assert lines[1].startswith("Pillow ")
    assert lines[2].startswith("Python ")
    lines = lines[3:]
    while lines[0].startswith("    "):
        lines = lines[1:]
    assert lines[0] == "-" * 68
    assert lines[1].startswith("Python modules loaded from ")
    assert lines[2].startswith("Binary modules loaded from ")
    assert lines[3] == "-" * 68
    jpeg = (
        os.linesep
        + "-" * 68
        + os.linesep
        + "JPEG image/jpeg"
        + os.linesep
        + "Extensions: .jfif, .jpe, .jpeg, .jpg"
        + os.linesep
        + "Features: open, save"
        + os.linesep
        + "-" * 68
        + os.linesep
    )
    assert jpeg in out
