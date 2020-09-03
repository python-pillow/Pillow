import pytest

from PIL import _util


def test_is_path():
    # Arrange
    fp = "filename.ext"

    # Act
    it_is = _util.isPath(fp)

    # Assert
    assert it_is


def test_path_obj_is_path():
    # Arrange
    from pathlib import Path

    test_path = Path("filename.ext")

    # Act
    it_is = _util.isPath(test_path)

    # Assert
    assert it_is


def test_is_not_path(tmp_path):
    # Arrange
    with (tmp_path / "temp.ext").open("w") as fp:
        pass

    # Act
    it_is_not = _util.isPath(fp)

    # Assert
    assert not it_is_not


def test_is_directory():
    # Arrange
    directory = "Tests"

    # Act
    it_is = _util.isDirectory(directory)

    # Assert
    assert it_is


def test_is_not_directory():
    # Arrange
    text = "abc"

    # Act
    it_is_not = _util.isDirectory(text)

    # Assert
    assert not it_is_not


def test_deferred_error():
    # Arrange

    # Act
    thing = _util.deferred_error(ValueError("Some error text"))

    # Assert
    with pytest.raises(ValueError):
        thing.some_attr
