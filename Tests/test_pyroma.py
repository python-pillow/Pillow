from __future__ import annotations

from importlib.metadata import metadata

import pytest

from PIL import __version__

pyroma = pytest.importorskip("pyroma", reason="Pyroma not installed")


def test_pyroma() -> None:
    # Arrange
    data = pyroma.projectdata.map_metadata_keys(metadata("Pillow"))

    # Act
    rating = pyroma.ratings.rate(data)

    # Assert
    if "rc" in __version__:
        # Pyroma needs to chill about RC versions and not kill all our tests.
        assert rating == (
            9,
            ["The package's version number does not comply with PEP-386."],
        )

    else:
        # Should have a perfect score, but pyroma does not support PEP 639 yet.
        assert rating == (
            9,
            [
                "Your package does neither have a license field "
                "nor any license classifiers."
            ],
        )
