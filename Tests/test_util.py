from __future__ import annotations

from pathlib import Path, PurePath

import pytest

from PIL import _util


@pytest.mark.parametrize(
    "test_path", ["filename.ext", Path("filename.ext"), PurePath("filename.ext")]
)
def test_is_path(test_path: str | Path | PurePath) -> None:
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


def test_deferred_error() -> None:
    # Arrange

    # Act
    thing = _util.DeferredError.new(ValueError("Some error text"))

    # Assert
    with pytest.raises(ValueError):
        thing.some_attr
