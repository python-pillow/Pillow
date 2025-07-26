from __future__ import annotations

import shutil

import pytest

from PIL import __version__

pyroma = pytest.importorskip("pyroma", reason="Pyroma not installed")


@pytest.mark.skipif(not shutil.which("git"), reason="Git is used by check-manifest")
def test_pyroma() -> None:
    # Arrange
    data = pyroma.projectdata.get_data(".")

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
        # Should have a perfect score
        assert rating == (10, [])
