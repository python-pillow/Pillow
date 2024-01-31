from __future__ import annotations

from pathlib import Path

import pytest

from PIL import _util


def test_is_path() -> None:
    # Arrange
    fp = "filename.ext"

    # Act
    it_is = _util.is_path(fp)

    # Assert
    assert it_is


def test_path_obj_is_path() -> None:
    # Arrange
    from pathlib import Path

    test_path = Path("filename.ext")

    # Act
    it_is = _util.is_path(test_path)

    # Assert
    assert it_is


def test_is_not_path(tmp_path: Path) -> None:
    # Arrange
    with (tmp_path / "temp.ext").open("w") as fp:
        pass

    # Act
    it_is_not = _util.is_path(fp)

    # Assert
    assert not it_is_not


def test_is_directory() -> None:
    # Arrange
    directory = "Tests"

    # Act
    it_is = _util.is_directory(directory)

    # Assert
    assert it_is


def test_is_not_directory() -> None:
    # Arrange
    text = "abc"

    # Act
    it_is_not = _util.is_directory(text)

    # Assert
    assert not it_is_not


def test_deferred_error() -> None:
    # Arrange

    # Act
    thing = _util.DeferredError.new(ValueError("Some error text"))

    # Assert
    with pytest.raises(ValueError):
        thing.some_attr
