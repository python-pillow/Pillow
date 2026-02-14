from __future__ import annotations

from importlib.metadata import metadata

import pytest

from PIL import __version__

TYPE_CHECKING = False

if TYPE_CHECKING:
    from importlib.metadata import PackageMetadata

pyroma = pytest.importorskip("pyroma", reason="Pyroma not installed")


def map_metadata_keys(md: PackageMetadata) -> dict[str, str | list[str] | None]:
    # Convert installed wheel metadata into canonical Core Metadata 2.4 format.
    # This was a utility method in pyroma 4.3.3; it was removed in 5.0.
    # This implementation is constructed from the relevant logic from
    # Pyroma 5.0's `build_metadata()` implementation. This has been submitted
    # upstream to Pyroma as https://github.com/regebro/pyroma/pull/116,
    # so it may be possible to simplify this test in future.
    data = {}
    for key in set(md):
        value = md.get_all(key)
        key = pyroma.projectdata.normalize(key)

        if value is not None and len(value) == 1:
            first_value = value[0]
            if first_value.strip() != "UNKNOWN":
                data[key] = first_value
        else:
            data[key] = value
    return data


def test_pyroma() -> None:
    # Arrange
    data = map_metadata_keys(metadata("Pillow"))

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
