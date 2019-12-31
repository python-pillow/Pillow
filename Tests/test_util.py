import unittest

from PIL import _util

from .helper import PillowTestCase


class TestUtil(PillowTestCase):
    def test_is_path(self):
        # Arrange
        fp = "filename.ext"

        # Act
        it_is = _util.isPath(fp)

        # Assert
        self.assertTrue(it_is)

    @unittest.skipUnless(_util.py36, "os.path support for Paths added in 3.6")
    def test_path_obj_is_path(self):
        # Arrange
        from pathlib import Path

        test_path = Path("filename.ext")

        # Act
        it_is = _util.isPath(test_path)

        # Assert
        self.assertTrue(it_is)

    def test_is_not_path(self):
        # Arrange
        filename = self.tempfile("temp.ext")
        fp = open(filename, "w").close()

        # Act
        it_is_not = _util.isPath(fp)

        # Assert
        self.assertFalse(it_is_not)

    def test_is_directory(self):
        # Arrange
        directory = "Tests"

        # Act
        it_is = _util.isDirectory(directory)

        # Assert
        self.assertTrue(it_is)

    def test_is_not_directory(self):
        # Arrange
        text = "abc"

        # Act
        it_is_not = _util.isDirectory(text)

        # Assert
        self.assertFalse(it_is_not)

    def test_deferred_error(self):
        # Arrange

        # Act
        thing = _util.deferred_error(ValueError("Some error text"))

        # Assert
        self.assertRaises(ValueError, lambda: thing.some_attr)
