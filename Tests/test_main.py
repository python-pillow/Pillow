import os
import subprocess
import sys
from unittest import TestCase


class TestMain(TestCase):
    def test_main(self):
        out = subprocess.check_output([sys.executable, "-m", "PIL"]).decode("utf-8")
        lines = out.splitlines()
        self.assertEqual(lines[0], "-" * 68)
        self.assertTrue(lines[1].startswith("Pillow "))
        self.assertTrue(lines[2].startswith("Python "))
        lines = lines[3:]
        while lines[0].startswith("    "):
            lines = lines[1:]
        self.assertEqual(lines[0], "-" * 68)
        self.assertTrue(lines[1].startswith("Python modules loaded from "))
        self.assertTrue(lines[2].startswith("Binary modules loaded from "))
        self.assertEqual(lines[3], "-" * 68)
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
