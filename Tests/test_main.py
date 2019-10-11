from __future__ import unicode_literals

import os
import subprocess
import sys
from unittest import TestCase

from .helper import is_pypy, is_win32, on_github_actions, unittest


class TestMain(TestCase):
    @unittest.skipIf(
        is_win32() and is_pypy() and on_github_actions(),
        "Failing on Windows on GitHub Actions running PyPy",
    )
    def test_main(self):
        out = subprocess.check_output([sys.executable, "-m", "PIL"]).decode("utf-8")
        lines = out.splitlines()
        self.assertEqual(lines[0], "-" * 68)
        self.assertTrue(lines[1].startswith("Pillow "))
        self.assertEqual(lines[2], "-" * 68)
        self.assertTrue(lines[3].startswith("Python modules loaded from "))
        self.assertTrue(lines[4].startswith("Binary modules loaded from "))
        self.assertEqual(lines[5], "-" * 68)
        self.assertTrue(lines[6].startswith("Python "))
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
        self.assertIn(jpeg, out)
