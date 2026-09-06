from __future__ import annotations

import os
import subprocess
import sys

import pytest


@pytest.mark.skipif(sys.platform == "ios", reason="Processes not supported on iOS")
@pytest.mark.parametrize(
    "args, report",
    ((["PIL"], False), (["PIL", "--report"], True), (["PIL.report"], True)),
)
def test_main(args: list[str], report: bool) -> None:
    args = [sys.executable, "-m"] + args
    out = subprocess.check_output(args).decode("utf-8")
    lines = out.splitlines()
    assert lines[0] == "-" * 68
    assert lines[1].startswith("Pillow ")
    assert lines[2].startswith("Python ")
    lines = lines[3:]
    while lines[0].startswith("    "):
        lines = lines[1:]
    assert lines[0] == "-" * 68
    assert lines[1].startswith("Python executable is")
    lines = lines[2:]
    if lines[0].startswith("Environment Python files loaded from"):
        lines = lines[1:]
    assert lines[0].startswith("System Python files loaded from")
    assert lines[1] == "-" * 68
    assert lines[2].startswith("Python Pillow modules loaded from ")
    assert lines[3].startswith("Binary Pillow modules loaded from ")
    assert lines[4] == "-" * 68
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
    assert report == (jpeg not in out)
