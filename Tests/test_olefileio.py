from __future__ import print_function
from tester import *

import PIL.OleFileIO as OleFileIO


def test_isOleFile_false():
    # Arrange
    non_ole_file = "Tests/images/flower.jpg"

    # Act
    is_ole = OleFileIO.isOleFile(non_ole_file)

    # Assert
    assert_false(is_ole)


def test_isOleFile_true():
    # Arrange
    ole_file = "Tests/images/test-ole-file.doc"

    # Act
    is_ole = OleFileIO.isOleFile(ole_file)

    # Assert
    assert_true(is_ole)


def test_exists_worddocument():
    # Arrange
    ole_file = "Tests/images/test-ole-file.doc"
    ole = OleFileIO.OleFileIO(ole_file)

    # Act
    exists = ole.exists('worddocument')

    # Assert
    assert_true(exists)


def test_exists_no_vba_macros():
    # Arrange
    ole_file = "Tests/images/test-ole-file.doc"
    ole = OleFileIO.OleFileIO(ole_file)

    # Act
    exists = ole.exists('macros/vba')

    # Assert
    assert_false(exists)


def test_get_type():
    # Arrange
    ole_file = "Tests/images/test-ole-file.doc"
    ole = OleFileIO.OleFileIO(ole_file)

    # Act
    type = ole.get_type('worddocument')

    # Assert
    assert_equal(type, OleFileIO.STGTY_STREAM)


def test_get_size():
    # Arrange
    ole_file = "Tests/images/test-ole-file.doc"
    ole = OleFileIO.OleFileIO(ole_file)

    # Act
    size = ole.get_size('worddocument')

    # Assert
    assert_greater(size, 0)


def test_get_rootentry_name():
    # Arrange
    ole_file = "Tests/images/test-ole-file.doc"
    ole = OleFileIO.OleFileIO(ole_file)

    # Act
    root = ole.get_rootentry_name()

    # Assert
    assert_equal(root, "Root Entry")


def test_meta():
    # Arrange
    ole_file = "Tests/images/test-ole-file.doc"
    ole = OleFileIO.OleFileIO(ole_file)

    # Act
    meta = ole.get_metadata()

    # Assert
    assert_equal(meta.author, b"Laurence Ipsum")
    assert_equal(meta.num_pages, 1)

# End of file
