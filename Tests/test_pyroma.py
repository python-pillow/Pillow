import pytest
from PIL import __version__

try:
    import pyroma
except ImportError:
    pyroma = None


@pytest.mark.skipif(pyroma is None, reason="Pyroma is not installed")
def test_pyroma():
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
